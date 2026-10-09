# -*- coding: utf-8 -*-
"""批次 A/B 纯函数单测: 收录过滤 / 置顶判定 / 缓存与重建 / 关联数据 / 时间 / 引用替换 / 色标 / tag 数据投影 / 图片懒加载 / 行号包裹 / 渲染版本 / 模板冒烟。"""
import calendar
import glob
import json
import os
import re
from datetime import datetime, timezone
from types import SimpleNamespace

from jinja2 import Environment, FileSystemLoader
from github import GithubException

from Gmeek import (
    GMEEK, IconList, IconViewBox, IconStrokeWidth, i18n, i18nCN, RENDER_VERSION, resolve_top, carry_cache, should_include_issue,
    resolve_regen_mode, resolve_run_mode, slim_state, list_order, nav_order,
    format_datetime_utc8, format_date_utc8,
    deterministic_hue, hex_to_hue, label_hue, resolve_label_color_mode, replace_issue_refs, tag_data, is_html_stale, search_settings,
    migrate_state,
)
from md2html import Markdown2GithubHtml
from icons import ICONS, render as render_icon, viewbox

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

UTC = timezone.utc
T0 = datetime(2025, 1, 1, tzinfo=UTC)
T1 = datetime(2025, 2, 1, tzinfo=UTC)
T2 = datetime(2025, 3, 1, tzinfo=UTC)


def ev(name, at):
    return SimpleNamespace(event=name, created_at=at)


class TestShouldIncludeIssue:
    def test_owner_issue_included(self):
        issue = SimpleNamespace(pull_request=None, user=SimpleNamespace(name="anaer"))
        assert should_include_issue(issue, "anaer")

    def test_pull_request_skipped(self):
        # 负向控制: PR 不得进入收录
        issue = SimpleNamespace(pull_request=object(), user=SimpleNamespace(name="anaer"))
        assert not should_include_issue(issue, "anaer")

    def test_other_author_skipped(self):
        issue = SimpleNamespace(pull_request=None, user=SimpleNamespace(name="someone"))
        assert not should_include_issue(issue, "anaer")

    def test_deleted_user_skipped(self):
        issue = SimpleNamespace(pull_request=None, user=None)
        assert not should_include_issue(issue, "anaer")


class TestResolveTop:
    def test_closed_issue_last(self):
        assert resolve_top("closed", []) == -1

    def test_never_pinned(self):
        assert resolve_top("open", [ev("labeled", T0), ev("subscribed", T1)]) == 0

    def test_pinned(self):
        assert resolve_top("open", [ev("pinned", T0)]) == 1

    def test_unpin_releases_pin(self):
        # 负向控制: 线上 issue #6 场景——历史 pinned 不得压制后续 unpinned
        assert resolve_top("open", [ev("pinned", T0), ev("unpinned", T1)]) == 0

    def test_repin_after_unpin(self):
        assert resolve_top("open", [ev("pinned", T0), ev("unpinned", T1), ev("pinned", T2)]) == 1

    def test_event_order_agnostic(self):
        shuffled = [ev("subscribed", T2), ev("unpinned", T1), ev("pinned", T0)]
        assert resolve_top("open", shuffled) == 0


class TestCarryCache:
    def test_carry_when_updated_at_unchanged(self):
        post = {"updatedAt": 5}
        old = {"updatedAt": 5, "description": "摘要", "buildedAt": 5, "postTitle": "旧标题"}
        carry_cache(post, old)
        assert post["description"] == "摘要"
        assert post["buildedAt"] == 5

    def test_no_carry_when_updated(self):
        # 负向控制: 内容有变更时不得携带旧缓存
        post = {"updatedAt": 6}
        old = {"updatedAt": 5, "description": "摘要", "buildedAt": 5}
        carry_cache(post, old)
        assert "description" not in post
        assert "buildedAt" not in post

    def test_no_carry_without_cache(self):
        post = {"updatedAt": 5}
        carry_cache(post, None)
        assert "description" not in post

    def test_carries_render_version(self):
        post = {"updatedAt": 5}
        old = {"updatedAt": 5, "buildedAt": 5, "renderVersion": RENDER_VERSION}
        carry_cache(post, old)
        assert post["renderVersion"] == RENDER_VERSION


class TestResolveRegenMode:
    def test_stale_html_rebuilds(self):
        assert resolve_regen_mode(True, "摘要", True, 10) == "rebuild"

    def test_cached_reuses_when_unchanged(self):
        assert resolve_regen_mode(False, "摘要", True, 10) is None

    def test_empty_summary_retries(self):
        assert resolve_regen_mode(False, "", True, 10) == "summary"

    def test_retry_budget_exhausted(self):
        # 负向控制: 预算用尽后不再重试
        assert resolve_regen_mode(False, "", True, 0) is None

    def test_unconfigured_api_no_retry(self):
        assert resolve_regen_mode(False, "", False, 10) is None


class TestGetCached:
    def test_rebuild_snapshot_takes_priority(self):
        # 全量构建: 缓存一律取重建前快照
        fake = SimpleNamespace(rebuild_cache={"P1": {"updatedAt": 1}}, blogBase={})
        assert GMEEK.get_cached(fake, "P1") == {"updatedAt": 1}

    def test_fallback_to_current_collections(self):
        # 增量构建: 依次查两个索引集合, 未命中返回 None
        fake = SimpleNamespace(
            rebuild_cache=None,
            blogBase={"postListJson": {}, "singeListJson": {"P2": {"updatedAt": 2}}},
        )
        assert GMEEK.get_cached(fake, "P2") == {"updatedAt": 2}
        assert GMEEK.get_cached(fake, "P9") is None


class TestSlimState:
    def test_only_content_indexes_persisted(self):
        blog_base = {"title": "t", "prevUrl": "x", "postListJson": {"P1": {}}, "singeListJson": {}}
        state = slim_state(blog_base)
        assert set(state.keys()) == {"postListJson", "singeListJson"}
        assert state["postListJson"] == {"P1": {}}


def mk_post(number, created, updated=None, labels=None):
    return {"number": str(number), "createdAt": created, "updatedAt": updated if updated else created,
            "top": 0, "postTitle": "T%d" % number, "postUrl": "post/%d.html" % number,
            "labels": labels if labels else []}


class TestRelatedOrder:
    """关联数据的顺序必须与列表页同序: 前端只在「共享标签数」相同的条目之间依赖该先后作次级排序。"""

    def test_same_sequence(self):
        pj = {"P1": mk_post(1, 100), "P2": mk_post(2, 300), "P3": mk_post(3, 200)}
        pj["P2"]["top"] = 1
        assert nav_order(pj) == list(list_order(pj))

    def test_uses_updated_at_not_created_at(self):
        # 排序键必须是 updatedAt: 若按 createdAt, P2(created 200) 会排在 P1(created 100) 之后, 与列表页不一致
        pj = {"P1": mk_post(1, 100), "P2": mk_post(2, 200, updated=900)}
        assert nav_order(pj) == ["P2", "P1"]


class TestRunOneRendersOnlyChangedPost:
    """关联文章在运行时按 nav.json 计算, 增量构建无需回刷其他文章页。"""

    @staticmethod
    def _fake(post_list):
        fake = SimpleNamespace()
        fake.blogBase = {"postListJson": post_list, "singeListJson": {}}
        fake.checkDir = lambda: None
        rendered = []
        fake.createPostHtml = lambda post: rendered.append(post["number"])
        fake.createPlistHtml = lambda: None
        fake.createFeedXml = lambda: None
        fake.createNavJson = lambda: None
        fake.createSearchHtml = lambda: None
        fake.repo = SimpleNamespace(get_issue=lambda n: object())
        return fake, rendered

    @staticmethod
    def _install(fake, number, post):
        def add(issue):
            fake.blogBase["postListJson"]["P" + str(number)] = post
            return post
        fake.addOnePostJson = add

    def test_new_post_does_not_rerender_others(self):
        fake, rendered = self._fake({"P1": mk_post(1, 100), "P2": mk_post(2, 200)})
        self._install(fake, 3, mk_post(3, 300))
        GMEEK.runOne(fake, "3")
        # 负向控制: 旧实现会连带重渲染相邻文章; 关联方案下只应渲染变更这一篇
        assert rendered == ["3"]

    def test_reorder_does_not_rerender_others(self):
        fake, rendered = self._fake({"P1": mk_post(1, 100), "P2": mk_post(2, 200), "P3": mk_post(3, 300)})
        self._install(fake, 2, mk_post(2, 400))
        GMEEK.runOne(fake, "2")
        assert rendered == ["2"]


class TestUtc8Format:
    def test_known_epoch_datetime(self):
        assert format_datetime_utc8(1694176150) == "2023-09-08 20:29:10"

    def test_epoch_collection_uses_utc(self):
        dt = datetime(2023, 9, 8, 12, 29, 10, tzinfo=UTC)
        assert calendar.timegm(dt.utctimetuple()) == 1694176150

    def test_cross_day_date(self):
        # 负向控制: 20:00Z 的帖子在 UTC+8 已是次日, 不能再取 UTC 日期
        epoch = calendar.timegm(datetime(2023, 9, 8, 20, 0, 0, tzinfo=UTC).utctimetuple())
        assert format_date_utc8(epoch) == "2023-09-09"


class TestDeterministicHue:
    def test_stable_for_same_seed(self):
        assert deterministic_hue("7") == deterministic_hue("7")

    def test_varies_across_seeds(self):
        hues = {deterministic_hue(str(i)) for i in range(1, 20)}
        assert len(hues) > 1

    def test_hue_range(self):
        for i in range(1, 60):
            hue = deterministic_hue(str(i))
            assert isinstance(hue, int)
            assert 0 <= hue < 360


class TestLabelColorMode:
    """labelColorMode: derived(默认) 按名称派生色相; github 取 GitHub 标签色的色相。"""

    def test_hex_to_hue_known_values(self):
        assert hex_to_hue("ff0000") == 0        # 红
        assert hex_to_hue("#00ff00") == 120     # 绿
        assert hex_to_hue("0000ff") == 240      # 蓝
        assert hex_to_hue("fff") == 0           # 三位简写(灰色)

    def test_hex_to_hue_unparsable(self):
        for bad in ("", "xyz", "12345", None):
            assert hex_to_hue(bad) is None

    def test_derived_mode_ignores_github_color(self):
        assert label_hue("blog", "ff0000", "derived") == deterministic_hue("blog")
        assert label_hue("blog", None, "derived") == deterministic_hue("blog")

    def test_github_mode_uses_github_color(self):
        assert label_hue("blog", "ff0000", "github") == 0

    def test_github_mode_falls_back_when_unparsable(self):
        # 色值缺失或非法时退回名称派生, 不产生空色相
        assert label_hue("blog", "", "github") == deterministic_hue("blog")
        assert label_hue("blog", "zzz", "github") == deterministic_hue("blog")

    def test_config_default_is_derived(self):
        with open(os.path.join(ROOT, "Gmeek.py"), encoding="utf-8") as f:
            assert '"labelColorMode":"derived"' in f.read()

    def test_mode_normalisation(self):
        assert resolve_label_color_mode("github") == "github"
        for other in ("derived", "", None, "GITHUB", "github "):
            assert resolve_label_color_mode(other) == "derived"


class TestLabelHueTheme:
    """标签配色: 色相由标签名确定性派生, 底色/字色在 CSS 里按主题从 --label-hue 推导。"""

    @staticmethod
    def _render(tpl, blog_base, post_list=None):
        env = Environment(loader=FileSystemLoader("templates"))
        return env.get_template(tpl).render(
            blogBase=blog_base, postListJson=post_list or {}, i18n=i18nCN,
            IconList=IconList, IconViewBox=IconViewBox, IconStrokeWidth=IconStrokeWidth)

    def test_css_derives_both_colors_per_theme(self):
        html = self._render("post.html", TestTemplateSmoke._post_base())
        # 浅色: 浅底 + 深字; 深色: 深底 + 浅字 —— 同一色相, 明度反转
        assert "hsl(var(--label-hue, 210), 70%, 92%)" in html
        assert "hsl(var(--label-hue, 210), 80%, 26%)" in html
        # 深色: WorkBuddy 风: 饱和度降到 30%, 底色更深(18%), 文字降到 78%(见 base.html)
        assert "hsl(var(--label-hue, 210), 30%, 18%)" in html
        assert "hsl(var(--label-hue, 210), 78%, 80%)" in html

    def test_tag_label_carries_hue_not_hex(self):
        html = self._render("post.html", TestTemplateSmoke._post_base(labels=["X"], labelHueDict={"X": 42}))
        span = re.search(r'<span class="Label"[^>]*--label-hue:42[^>]*>', html)
        assert span, "标签应带 --label-hue"
        # 不再输出 GitHub 十六进制底色, 也不再硬编码白字
        assert "background-color" not in span.group(0)
        assert "#fff" not in span.group(0)

    def test_plist_hue_driven_and_comment_badge_solid(self):
        post = {"labels": ["X"], "postUrl": "post/1.html", "postTitle": "T1",
                "dateLabelHue": 123, "createdDate": "2023-09-08", "commentNum": 3, "buildedAt": 1}
        html = self._render("plist.html", TestSearchPageSmoke._plist_base(labelHueDict={"X": 42}), {"1": post})
        assert "--label-hue:42" in html                 # 标签
        assert "--label-hue:123" in html                # 日期标签
        assert 'class="Label Label--solid"' in html     # 评论数徽标维持配置色
        assert "background-color:hsl(" not in html.replace(" ", "")

    def test_unknown_label_falls_back_to_default_hue(self):
        html = self._render("post.html", TestTemplateSmoke._post_base(labels=["未登记"], labelHueDict={}))
        assert "--label-hue:210" in html

    def test_init_initialises_labelHueDict_before_defaultConfig(self):
        # 回归: __init__ 调用 defaultConfig() 时, self.labelHueDict 必须先有占位值,
        # 否则 defaultConfig 第 255 行 self.blogBase["labelHueDict"]=self.labelHueDict 会 AttributeError。
        # 测试不实际实例化 GMEEK(GitHub 网络), 直接审计源码行序。
        import inspect
        src, start = inspect.getsourcelines(GMEEK.__init__)
        body = "".join(src)
        idx_init = body.find("self.labelHueDict =")
        idx_default = body.find("self.defaultConfig(")
        assert idx_init != -1,  "GMEEK.__init__ 必须先对 self.labelHueDict 赋值"
        assert idx_default != -1
        assert idx_init < idx_default, "self.labelHueDict 的占位值必须在 defaultConfig 调用之前"

    def test_init_resyncs_blogBase_labelHueDict_after_recompute(self):
        # 回归: 占位空 dict 进了 defaultConfig 后, __init__ 末尾按 GitHub 标签重算 labelHueDict,
        # 必须把重算结果同步写回 self.blogBase["labelHueDict"], 否则模板读到的仍是占位空 dict。
        # 测试不实例化 GMEEK(避免真实 GitHub 网络), 走「审计源码行序」+ 校验博客基础映射最终值已重算。
        import inspect
        body = "".join(inspect.getsourcelines(GMEEK.__init__)[0])
        # 找到占位赋值之后, 重算语句之后, 必须存在把 labelHueDict 写回 blogBase 的行
        assert 'self.blogBase["labelHueDict"] = self.labelHueDict' in body, (
            "__init__ 末尾必须把重算后的 labelHueDict 写回 blogBase, 供模板消费")
        # 写回必须在重算之后, 不能放在占位之后(否则仍是空 dict)
        idx_recompute = body.find("self.repo.get_labels()")
        idx_resync = body.find('self.blogBase["labelHueDict"] = self.labelHueDict')
        idx_default = body.find("self.defaultConfig(")
        assert idx_recompute != -1 and idx_resync != -1 and idx_default != -1
        assert idx_recompute < idx_resync, "回写必须在重算之后"
        assert idx_default < idx_resync, "回写必须在 defaultConfig 之后(否则覆盖的就是占位)"


class TestReplaceIssueRefs:
    @staticmethod
    def resolver(mapping):
        return lambda num: mapping.get(num)

    def test_plain_text_replaced(self):
        out = replace_issue_refs("见 #2 一文", self.resolver({"2": " [T2](u) "}))
        assert "[T2](u)" in out
        assert "#2" not in out

    def test_fenced_code_untouched(self):
        # 负向控制: 代码块内不替换, 块外替换
        content = "前文 #2\n```\n#2 code\n```\n后文 #2"
        out = replace_issue_refs(content, self.resolver({"2": " [T2](u) "}))
        assert "#2 code" in out
        assert out.count("[T2](u)") == 2

    def test_inline_code_untouched(self):
        out = replace_issue_refs("行内 `#2` 与正文 #2", self.resolver({"2": " [T2](u) "}))
        assert "`#2`" in out
        assert out.count("[T2](u)") == 1

    def test_missing_target_kept(self):
        assert replace_issue_refs("见 #9", self.resolver({})) == "见 #9"


class TestCreatePostHtmlRelated:
    @staticmethod
    def _fake(blog_base):
        fake = SimpleNamespace()
        fake.blogBase = blog_base
        fake.options = SimpleNamespace(repo_name="x/y")
        captured = {}
        fake.renderHtml = lambda template, postBase, postListJson, htmlDir: captured.update(postBase)
        return fake, captured

    @staticmethod
    def _post(tmp_path, number):
        md = tmp_path / ("%d.md" % number)
        md.write_text("body", encoding="utf-8")
        (tmp_path / ("%d.md.html" % number)).write_text("<p>body</p>", encoding="utf-8")
        return {"number": str(number), "markdown": str(md), "postTitle": "T%d" % number,
                "labels": ["py"], "commentNum": 0, "style": "", "script": "", "top": 0,
                "postSourceUrl": "u", "description": "", "createdAt": 100 * number, "updatedAt": 100 * number,
                "htmlDir": "docs/post/%d.html" % number}

    @staticmethod
    def _base():
        return {"homeUrl": "https://example.com/blog",
                "postListJson": {"P1": mk_post(1, 100), "P2": mk_post(2, 200), "P3": mk_post(3, 300)}}

    def test_exposes_current_labels_and_number(self, tmp_path):
        # 关联文章由 nav.js 用这两个入口在运行时算出, 构建期不再写死任何链接
        fake, captured = self._fake(self._base())
        GMEEK.createPostHtml(fake, self._post(tmp_path, 2))
        assert captured["postNumber"] == "2"
        assert captured["labels"] == ["py"]

    def test_no_neighbor_fields_written(self, tmp_path):
        # 负向控制: 上一篇/下一篇字段不得出现在文章页数据里
        fake, captured = self._fake(self._base())
        GMEEK.createPostHtml(fake, self._post(tmp_path, 2))
        for key in ("prevUrl", "prevTitle", "nextUrl", "nextTitle"):
            assert key not in captured

    def test_list_pagination_fields_are_not_leaked(self, tmp_path):
        # 负向控制: createPlistHtml 会把分页 prevUrl/nextUrl 写在 blogBase 上,
        # postBase 是它的副本, 残留字段必须清除, 否则旧链接会漏进文章页
        base = self._base()
        base["prevUrl"] = "stale"
        base["nextUrl"] = "stale"
        fake, captured = self._fake(base)
        GMEEK.createPostHtml(fake, self._post(tmp_path, 1))
        assert "prevUrl" not in captured and "nextUrl" not in captured


class TestTemplateSmoke:
    @staticmethod
    def _render(template, blog_base):
        env = Environment(loader=FileSystemLoader("templates"))
        return env.get_template(template).render(blogBase=blog_base, postListJson={}, i18n=i18nCN, IconList=IconList, IconViewBox=IconViewBox, IconStrokeWidth=IconStrokeWidth)

    @staticmethod
    def _post_base(**overrides):
        base = {
            "title": "T", "homeUrl": "https://example.com/blog", "nightTheme": "dark", "dayTheme": "light",
            "faviconUrl": "", "GMEEK_VERSION": "v2.4", "issuesUrl": "https://github.com/x/y/issues",
            "postTitle": "标题", "labels": [], "labelHueDict": {}, "commentNum": 0, "style": "", "script": "",
            "top": 0, "postSourceUrl": "https://github.com/x/y/issues/1", "repoName": "x/y",
            "description": "", "postBody": "<p>正文</p>",
            "createdAt": "2023-09-08 20:29:10", "updatedAt": "2023-09-08 20:29:10", "highlight": 0,
        }
        base.update(overrides)
        return base

    def test_post_description_escaped(self):
        html = self._render("post.html", self._post_base(description='<img src=x onerror=alert(1)>'))
        assert "&lt;img src=x onerror=alert(1)&gt;" in html
        assert "<img src=x" not in html

    def test_post_label_link_encoded(self):
        html = self._render("post.html", self._post_base(labels=["C++"], labelHueDict={"C++": 210}))
        assert "tag.html#C%2B%2B" in html

    def test_post_related_exposes_runtime_hooks(self):
        html = self._render("post.html", self._post_base(postNumber="166", labels=["Python", "C++"]))
        assert 'class="related-posts"' in html
        assert 'data-nav-url="https://example.com/blog/nav.json"' in html
        assert 'data-post-number="166"' in html
        assert 'data-heading="相关文章"' in html
        assert 'data-labels=\'["Python", "C++"]\'' in html
        assert "assets/nav.js" in html

    def test_post_related_labels_survive_quotes(self):
        # 标签名含引号/尖括号时不得破坏 data-labels 属性: tojson 需做 HTML 安全转义, 且仍是合法 JSON
        labels = ['a"b', "<c>", "it's"]
        html = self._render("post.html", self._post_base(labels=labels))
        raw = re.search(r"data-labels='([^']*)'", html).group(1)
        assert "<c>" not in raw
        assert json.loads(raw) == labels

    def test_post_has_no_prev_next_markup(self):
        # 负向控制: 上一页/下一页区块已被关联文章取代
        html = self._render("post.html", self._post_base(postNumber="1", prevTitle="相邻旧标题", nextTitle="相邻旧标题"))
        assert "paginate-container" not in html
        assert "previous_page" not in html
        assert "相邻旧标题" not in html
        assert "rel=\"previous\"" not in html

    def test_post_body_is_search_indexed(self):
        # 只索引正文容器: 列表页/标签页/搜索页不含该属性, 因此不进索引
        html = self._render("post.html", self._post_base())
        assert 'id="postBody" data-pagefind-body' in html

    def test_post_del_uses_muted_tokens_for_text_and_line(self):
        # 旧文本视觉退到 muted/subtle, 不抢当前文本权重; 走主题变量, 明暗自适应
        html = self._render("post.html", self._post_base(postBody='<del>旧实现</del><s>原生</s>'))
        m = re.search(r'\.markdown-body\s+del\s*\{[^}]+\}', html)
        assert m, "post.html 必须包含 .markdown-body del 样式"
        css = m.group(0)
        assert "color:var(--color-fg-muted)" in css
        assert "text-decoration:line-through" in css
        assert "text-decoration-color:var(--color-fg-subtle)" in css
        # 不应硬编码 hex/rgb, 否则明暗自适应失效
        assert "#[0-9a-f]" not in css.replace("var(--color-fg-muted)", "").replace("var(--color-fg-subtle)", "")
        assert "rgb(" not in css

    def test_post_theme_tokens_cover_del_dependencies(self):
        # data-color-mode=light/dark 的 token 块必须同时给出 fg-muted 与 fg-subtle,
        # 否则 del 会在某一主题下回落到继承默认色, 等同未生效
        html = self._render("post.html", self._post_base())
        for mode in ('light', 'dark'):
            block = re.search(rf'\[data-color-mode="{mode}"\]\s*\.markdown-body\s*\{{([^}}]+)\}}', html)
            assert block, f"缺少 {mode} 主题的 .markdown-body token 块"
            assert "--color-fg-muted:" in block.group(1)
            assert "--color-fg-subtle:" in block.group(1)

    def test_plist_single_page_link_uses_home_url(self):
        base = {
            "title": "T", "homeUrl": "https://example.com/blog", "nightTheme": "dark", "dayTheme": "light",
            "faviconUrl": "", "GMEEK_VERSION": "v2.4", "avatarUrl": "https://example.com/a.png",
            "displayTitle": "T", "subTitle": "s", "issuesUrl": "https://github.com/x/y/issues",
            "singeListJson": {"S1": {"label": "about", "postTitle": "About"}},
            "labelHueDict": {}, "commentLabelColor": "#006b75",
            "prevUrl": "disabled", "nextUrl": "disabled", "firstUrl": "disabled", "lastUrl": "disabled",
        }
        html = self._render("plist.html", base)
        assert 'href="https://example.com/blog/about.html"' in html
        assert 'href="/about.html"' not in html


class TestCreateFeedXmlSmoke:
    def test_feed_generates_with_single_and_post(self, tmp_path):
        fake = SimpleNamespace()
        fake.root_dir = str(tmp_path) + os.sep
        fake.blogBase = {
            "title": "T", "subTitle": "S", "homeUrl": "https://example.com/blog",
            "avatarUrl": "https://example.com/a.png",
            "singeListJson": {"S1": {"postUrl": "about.html", "postTitle": "About", "description": "", "createdAt": 1694176150}},
            "postListJson": {"P1": {"postUrl": "post/1.html", "postTitle": "T1", "description": "d", "createdAt": 1694176150}},
        }
        GMEEK.createFeedXml(fake)
        rss = (tmp_path / "rss.xml").read_text(encoding="utf-8")
        assert "about.html" in rss
        assert "post/1.html" in rss


class TestCreateNavJson:
    def test_writes_nav_in_time_order(self, tmp_path):
        fake = SimpleNamespace()
        fake.root_dir = str(tmp_path) + os.sep
        fake.blogBase = {
            "homeUrl": "https://example.com/blog",
            "postListJson": {"P2": mk_post(2, 200, labels=["py"]), "P1": mk_post(1, 100, labels=["go"])},
        }
        GMEEK.createNavJson(fake)
        data = json.loads((tmp_path / "nav.json").read_text(encoding="utf-8"))
        # 与列表页同序(updatedAt 降序)
        assert [p["number"] for p in data] == ["2", "1"]
        assert data[0]["title"] == "T2"
        assert data[0]["url"] == "https://example.com/blog/post/2.html"

    def test_exports_labels_for_relation_scoring(self, tmp_path):
        # 关联度只能在客户端由「当前文章标签 × 各文章标签」算出, 故 labels 必须随数据导出
        fake = SimpleNamespace()
        fake.root_dir = str(tmp_path) + os.sep
        fake.blogBase = {
            "homeUrl": "https://example.com/blog",
            "postListJson": {"P1": mk_post(1, 100, labels=["py", "工具"])},
        }
        GMEEK.createNavJson(fake)
        data = json.loads((tmp_path / "nav.json").read_text(encoding="utf-8"))
        assert data[0]["labels"] == ["py", "工具"]

    def test_missing_labels_default_empty(self, tmp_path):
        # 负向控制: 老状态文件条目可能没有 labels, 不得让整份数据构建崩溃
        fake = SimpleNamespace()
        fake.root_dir = str(tmp_path) + os.sep
        fake.blogBase = {"homeUrl": "https://example.com/blog",
                         "postListJson": {"P1": mk_post(1, 100)}}
        fake.blogBase["postListJson"]["P1"].pop("labels")
        GMEEK.createNavJson(fake)
        data = json.loads((tmp_path / "nav.json").read_text(encoding="utf-8"))
        assert data[0]["labels"] == []

    def test_empty_posts(self, tmp_path):
        fake = SimpleNamespace()
        fake.root_dir = str(tmp_path) + os.sep
        fake.blogBase = {"homeUrl": "https://example.com/blog", "postListJson": {}}
        GMEEK.createNavJson(fake)
        assert json.loads((tmp_path / "nav.json").read_text(encoding="utf-8")) == []


class TestMigrateState:
    """一次构建迁移: 老状态文件缺派生字段时由 build 入口就地补, 落盘后下游消费者统一走真值路径。"""

    def test_fills_dateLabelHue_and_createdDate_on_legacy_entries(self):
        # 真实场景: blogBase.json 是在 dateLabelHue/createdDate 上线前已存的, 历史条目缺这俩
        state = {
            "postListJson": {
                "P9": {"labels": ["blog"], "postUrl": "post/9.html", "postTitle": "老帖 9",
                       "number": "9", "createdAt": 1696770000, "updatedAt": 1696770000,
                       "top": 0, "commentNum": 0, "description": "", "style": "", "script": "",
                       "postSourceUrl": "#", "markdown": "m", "htmlDir": "/"},
            },
            "singeListJson": {
                "P10": {"labels": ["about"], "postUrl": "about.html", "postTitle": "关于",
                        "number": "10", "createdAt": 1696770001, "updatedAt": 1696770001,
                        "label": "about", "top": 0, "commentNum": 0, "description": "",
                        "style": "", "script": "", "postSourceUrl": "#", "markdown": "m", "htmlDir": "/"},
            },
        }
        migrate_state(state)
        for key in ("P9",):
            assert state["postListJson"][key]["dateLabelHue"] == deterministic_hue("9")
            assert state["postListJson"][key]["createdDate"] == format_date_utc8(1696770000)
        assert state["singeListJson"]["P10"]["dateLabelHue"] == deterministic_hue("10")
        assert state["singeListJson"]["P10"]["createdDate"] == format_date_utc8(1696770001)

    def test_idempotent_when_entries_already_have_fields(self):
        # 已含派生字段的条目不应被覆盖(保护 fresh 数据不被篡改)
        real_hue = 123
        real_date = "2024-12-31"
        state = {"postListJson": {"P1": {"labels": [], "postUrl": "p.html", "postTitle": "T",
                                          "number": "1", "createdAt": 1, "updatedAt": 1,
                                          "dateLabelHue": real_hue, "createdDate": real_date}}}
        migrate_state(state)
        assert state["postListJson"]["P1"]["dateLabelHue"] == real_hue
        assert state["postListJson"]["P1"]["createdDate"] == real_date

    def test_does_not_touch_other_fields(self):
        # 迁移只能补派生字段; 不应影响 labels/postTitle 等已有的非派生键
        state = {"postListJson": {"P1": {"labels": ["Life"], "postUrl": "post/1.html",
                                          "postTitle": "老帖", "number": "1",
                                          "createdAt": 1696770000, "updatedAt": 1696770000}}}
        labels_before = state["postListJson"]["P1"]["labels"]
        title_before = state["postListJson"]["P1"]["postTitle"]
        migrate_state(state)
        assert state["postListJson"]["P1"]["labels"] == labels_before
        assert state["postListJson"]["P1"]["postTitle"] == title_before
        assert "dateLabelHue" in state["postListJson"]["P1"]
        assert "createdDate" in state["postListJson"]["P1"]

    def test_handles_missing_postListJson_or_singeListJson(self):
        # 健壮性: 状态文件极简(只有 postListJson 或 只有 singeListJson 或 都没有)都不能崩
        for partial in ({}, {"postListJson": {}}, {"singeListJson": {}},
                        {"postListJson": None}, {"singeListJson": None}):
            migrate_state(partial)  # 不能抛
        # None 值情况下不能崩, 但消费 NPE 那是模板侧的责任
        state = {"postListJson": None, "singeListJson": {"P1": {}}}
        migrate_state(state)

    def test_deterministic_hue_matches_addOnePostJson(self):
        # 端到端契约: migrate_state 派生出的 dateLabelHue 与 addOnePostJson 一致, 否则同一帖子
        # 在两个上下文会渲染出不同色相
        from Gmeek import deterministic_hue as _h
        post = {"number": "42"}
        migrate_state({"postListJson": {"P42": post}})
        assert post["dateLabelHue"] == _h("42")


class TestTagData:
    def test_projects_only_needed_fields(self):
        full = {"labels": ["Life"], "postUrl": "post/1.html", "postTitle": "T1",
                "dateLabelHue": 123, "createdDate": "2023-09-08",
                "description": "长摘要" * 100, "style": "", "script": "", "markdown": "m.md", "buildedAt": 1}
        out = tag_data({"P1": full})
        assert set(out["P1"].keys()) == {"labels", "postUrl", "postTitle", "dateLabelHue", "createdDate"}

    def test_empty_input(self):
        assert tag_data({}) == {}

    def test_missing_fields_fall_back_to_defaults(self):
        # 真实事故复现: 旧状态文件(blogBase.json)里的帖子在本特性加入前已存,
        # 缺少 dateLabelHue(以及其它新增字段), KeyError 会让整页构建崩溃。
        # 投影必须字段缺失兜底, 不让单条缺失中断整页。
        legacy = {"number": "1", "labels": ["Life"], "postUrl": "post/1.html", "postTitle": "T1"}
        out = tag_data({"P1": legacy})
        assert out["P1"]["labels"] == ["Life"]
        assert out["P1"]["postUrl"] == "post/1.html"
        assert out["P1"]["postTitle"] == "T1"
        # 缺失字段按 defaults 兜底, 与模板 / JS 的弱契约保持一致
        assert out["P1"]["dateLabelHue"] == 210
        assert out["P1"]["createdDate"] == ""

    def test_partial_missing_only_some_fields(self):
        # 混合数据(部分新, 部分老)也必须整体跑通, 不让单条死循环相邻崩溃
        new = {"labels": ["blog"], "postUrl": "post/9.html", "postTitle": "新帖",
               "dateLabelHue": 7, "createdDate": "2026-10-08"}
        old = {"labels": ["Life"], "postUrl": "post/1.html", "postTitle": "老帖"}
        out = tag_data({"P9": new, "P1": old})
        assert out["P9"]["dateLabelHue"] == 7
        assert out["P1"]["dateLabelHue"] == 210
        assert set(out.keys()) == {"P9", "P1"}

    def test_output_value_types_match_defaults(self):
        # 钉死默认值的「类型 + 取值」, 防止后续误改(例如把 dateLabelHue 改成 None, 模板 setProperty 会变 '')
        post = {}  # 完全空
        out = tag_data({"P0": post})
        d = out["P0"]
        assert d["labels"] == [] and isinstance(d["labels"], list)
        assert d["postUrl"] == "" and isinstance(d["postUrl"], str)
        assert d["postTitle"] == "" and isinstance(d["postTitle"], str)
        assert d["dateLabelHue"] == 210 and isinstance(d["dateLabelHue"], int)
        assert d["createdDate"] == "" and isinstance(d["createdDate"], str)


class TestImageLazyLoading:
    def test_image_gets_lazy_attributes(self):
        html = Markdown2GithubHtml().convert("![alt](https://example.com/a.png)")
        assert html.count('loading="lazy" decoding="async"') == 1
        assert '<img loading="lazy" decoding="async"' in html

    def test_existing_loading_attribute_not_duplicated(self):
        tool = Markdown2GithubHtml()
        assert tool._add_lazy_loading('<img loading="eager" src="a.png">') == '<img loading="eager" src="a.png">'


class TestHtmlStale:
    @staticmethod
    def _post(**overrides):
        post = {"updatedAt": 100, "buildedAt": 100, "renderVersion": RENDER_VERSION}
        post.update(overrides)
        return post

    def test_fresh_cache_not_stale(self):
        assert not is_html_stale(True, self._post())

    def test_missing_render_version_regenerates(self):
        # 负向控制: 老帖子(无版本标记)必须重转
        assert is_html_stale(True, {"updatedAt": 100, "buildedAt": 100})

    def test_version_mismatch_regenerates(self):
        assert is_html_stale(True, self._post(renderVersion=RENDER_VERSION + 1))

    def test_updated_content_regenerates(self):
        assert is_html_stale(True, self._post(buildedAt=99))

    def test_missing_file_regenerates(self):
        assert is_html_stale(False, self._post())


class TestWrapCodeLines:
    @staticmethod
    def _tool():
        return Markdown2GithubHtml()

    def test_single_line(self):
        assert self._tool()._wrap_code_lines("single") == '<span class="cl">single</span>'

    def test_lines_counted(self):
        out = self._tool()._wrap_code_lines("a\nb\nc")
        assert out.count('class="cl"') == 3

    def test_multiline_token_closed_and_reopened(self):
        # 负向控制: 跨行 span 必须在行内闭合并重开
        out = self._tool()._wrap_code_lines('<span class="s">"a\nb"</span>')
        assert out == ('<span class="cl"><span class="s">"a</span></span>'
                       '<span class="cl"><span class="s">b"</span></span>')

    def test_no_stray_newline_between_line_spans(self):
        # 回归: .cl 之间不得出现裸换行, 否则 pre(white-space:pre) 下会多出空行, 行距翻倍
        out = self._tool()._wrap_code_lines("a\nb\nc")
        assert "</span>\n<span" not in out
        assert out.count("\n") == 0

    def test_trailing_newline_not_numbered(self):
        out = self._tool()._wrap_code_lines("x\ny\n")
        assert out.count('class="cl"') == 2

    def test_blank_line_counted(self):
        out = self._tool()._wrap_code_lines("a\n\nb")
        assert out.count('class="cl"') == 3

    def test_convert_produces_line_spans(self):
        html = self._tool().convert("```python\nprint(1)\nprint(2)\n```")
        assert html.count('<span class="cl">') == 2

    def test_convert_includes_toggle_controls(self):
        html = self._tool().convert("```\nx\n```")
        assert "wrap-toggle" in html and "lines-toggle" in html
        assert "classList.toggle('nowrap')" in html
        assert "classList.toggle('nolines')" in html

    def test_blank_line_keeps_visible_height(self):
        # 空 <span class="cl"></span> 无 in-flow content, 默认 height:0,
        # 会让空行「消失」并与下一行挤在一起. min-height 必须锁定到一行高度
        html = self._tool().convert("```python\na\n\nb\n```")
        # 包含 min-height 规则, 数值与 line-height(1.45)对齐
        m = re.search(r"\.highlight\s+\.cl\s*\{([^}]*)\}", html, re.DOTALL)
        assert m, "缺少 .highlight .cl 基础规则"
        body = m.group(1)
        assert "min-height" in body, "空行没有 min-height 兜底, 会与下一行挤在一起"
        # 必须为 1.45em, 与 line-height 一致, 保留视觉一行高度
        assert re.search(r"min-height:\s*1\.45em", body), \
            f"min-height 数值 {body!r} 不符合预期(应为 1.45em 与 line-height 对齐)"

    def test_blank_line_emits_empty_cl(self):
        # _wrap_code_lines 必须为空行也产生一个 .cl 标签(不能吞掉),
        # 否则 CSS 计数器行号会跳号, 且 min-height 也没机会生效
        out = self._tool()._wrap_code_lines("a\n\nb")
        assert out.count('class="cl"') == 3
        # 中间那个就是空行
        assert "<span class=\"cl\"></span>" in out


class TestHardBreaks:
    # 硬换行(行末两空格)只作用于围栏代码块之外
    def test_breaks_added_outside_fence(self):
        out = Markdown2GithubHtml._add_hard_breaks("line1\nline2")
        assert out == "line1  \nline2  "

    def test_code_block_content_untouched(self):
        md = "text\n```python\nx = 1\nprint(x)\n```\nafter"
        out = Markdown2GithubHtml._add_hard_breaks(md)
        assert "x = 1\n" in out and "x = 1  " not in out
        assert "print(x)\n" in out and "print(x)  " not in out
        # 围栏外仍补空格
        assert "text  " in out and "after  " in out

    def test_tilde_fence_supported(self):
        out = Markdown2GithubHtml._add_hard_breaks("~~~\ncode\n~~~\nend")
        assert "code\n" in out and "code  " not in out
        assert "end  " in out

    def test_convert_code_has_no_trailing_spaces(self):
        html = Markdown2GithubHtml().convert("```python\nx = 1\n```")
        code = re.search(r"<pre.*?</pre>", html, re.S).group(0)
        assert "x = 1  " not in code


class TestCodeBlockResponsiveCss:
    # 代码块: 换行开关须真正生效, 且移动端有常显控件样式
    @staticmethod
    def _html():
        return Markdown2GithubHtml().convert("```python\nx = 1\ny = 2\n```")

    def test_line_span_allows_wrapping(self):
        html = self._html()
        # .cl 必须显式 pre-wrap, 才能覆盖 .markdown-body pre>code 的 white-space:pre
        assert "white-space: pre-wrap" in html

    def test_nowrap_switch_forces_pre(self):
        html = self._html()
        assert ".code-block-wrapper.nowrap .cl" in html
        assert "white-space: pre;" in html

    def test_touch_media_query_present(self):
        html = self._html()
        assert "@media (hover: none), (max-width: 767px)" in html
        assert "opacity: 1" in html          # 触屏下控件常显
        assert "padding-top: 30px" in html   # 为控件预留空间, 不遮挡代码

    def test_gutter_background_light_theme(self):
        # 行号槽位底色: 浅主题用 rgba(175,184,193,0.28) 染左 2em, 收尾 1px 分隔线
        html = self._html()
        # 必须出现 linear-gradient 与浅色 rgba, 避免行号与代码区同色难以分辨
        assert "linear-gradient(to right" in html
        assert "rgba(175, 184, 193, 0.28)" in html
        assert "rgba(175, 184, 193, 0.55)" in html   # 1px 分隔线更深
        # 槽位宽 2em
        assert "calc(2em - 1px)" in html

    def test_gutter_background_dark_theme(self):
        # 深主题(WorkBuddy 风): 槽位与分隔线都用中性白色微染, 不带蓝灰调
        # 槽位 rgba(255,255,255,0.045), 1px 分隔线 rgba(255,255,255,0.10)
        html = self._html()
        assert "rgba(255, 255, 255, 0.045)" in html
        assert "rgba(255, 255, 255, 0.10)" in html
        # 旧蓝灰色 rgba(110, 118, 129, ...) 不得再出现
        assert "rgba(110, 118, 129, 0.22)" not in html
        assert "rgba(110, 118, 129, 0.45)" not in html
        # 深色规则挂载在 html[data-color-mode="dark"] .highlight .cl
        assert 'html[data-color-mode="dark"] .highlight .cl' in html

    def test_gutter_background_removed_when_lines_off(self):
        # 行号关闭(nolines)时, 槽位底色必须一并撤掉, 否则左侧会留一道与代码区不连贯的色块
        html = self._html()
        assert ".code-block-wrapper.nolines .cl" in html
        # 紧跟 nolines .cl 的规则必须含 background-image: none
        m = re.search(r"\.code-block-wrapper\.nolines\s+\.cl\s*\{([^}]*)\}", html, re.DOTALL)
        assert m, "缺少 nolines .cl 规则"
        assert "background-image: none" in m.group(1)

    def test_gutter_single_width_across_viewports(self):
        # 行号槽宽与代码缩进在桌面/窄屏统一为 2em / 2.8em: 槽位贴合行号数字宽度, 行号不再整体偏右
        html = self._html()
        m = re.search(r"\.highlight \.cl\s*\{([^}]*)\}", html, re.DOTALL)
        assert m, "缺少 .highlight .cl 基础规则"
        assert "padding-left: 2.8em" in m.group(1)
        assert "width: 2em" in html    # ::before 行号槽宽
        # 负向控制: 旧的更宽槽位(2.4em)与更宽缩进(3.2em)不得残留, 视口内也不应再有第二套行号槽宽度
        for stale in ("2.4em", "3.2em"):
            assert stale not in html, stale
        # 深浅两套主题的槽宽必须一致
        dark = re.search(r'html\[data-color-mode="dark"\] \.highlight \.cl\s*\{([^}]*)\}', html, re.DOTALL).group(1)
        assert "calc(2em - 1px)" in dark
        assert "transparent 2em" in dark


class TestDefaultConfig:
    @staticmethod
    def _fake():
        return SimpleNamespace(repo=SimpleNamespace(full_name="x/y"), labelHueDict={})

    def test_slim_state_falls_back_to_defaults(self, tmp_path, monkeypatch):
        # 负向控制: 瘦身后的 blogBase.json(无 i18n 等键) 必须回落内置默认值, 而不是 KeyError
        (tmp_path / "blogBase.json").write_text(json.dumps({"postListJson": {}, "singeListJson": {}}), encoding="utf-8")
        (tmp_path / "config.json").write_text(json.dumps({"title": "T"}), encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        fake = self._fake()
        GMEEK.defaultConfig(fake)
        assert fake.blogBase["i18n"] == "CN"
        assert fake.blogBase["onePageListNum"] == 15
        assert fake.blogBase["title"] == "T"
        assert fake.i18n is i18nCN

    def test_config_overrides_defaults(self, tmp_path, monkeypatch):
        (tmp_path / "config.json").write_text(json.dumps({"i18n": "EN"}), encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        fake = self._fake()
        GMEEK.defaultConfig(fake)
        assert fake.blogBase["i18n"] == "EN"
        assert fake.i18n is i18n

    def test_derives_search_settings(self, tmp_path, monkeypatch):
        (tmp_path / "config.json").write_text(
            json.dumps({"homeUrl": "https://example.com/blog/"}), encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        fake = self._fake()
        GMEEK.defaultConfig(fake)
        assert fake.blogBase["lang"] == "zh-CN"
        assert fake.blogBase["searchBaseUrl"] == "https://example.com/blog/"


class TestSearchSettings:
    def test_cn_maps_to_zh_cn(self):
        assert search_settings("CN", "https://example.com/blog")["lang"] == "zh-CN"

    def test_non_cn_maps_to_en(self):
        assert search_settings("EN", "https://example.com/blog")["lang"] == "en"

    def test_base_url_gets_trailing_slash(self):
        assert search_settings("CN", "https://example.com/blog")["searchBaseUrl"] == "https://example.com/blog/"

    def test_base_url_does_not_double_slash(self):
        # 负向控制: homeUrl 已带尾斜杠时不得拼出 "//"
        assert search_settings("CN", "https://example.com/blog/")["searchBaseUrl"] == "https://example.com/blog/"

    def test_missing_home_url_falls_back_to_root(self):
        assert search_settings("CN", None)["searchBaseUrl"] == "/"


class TestSearchPageSmoke:
    @staticmethod
    def _render(template, blog_base):
        env = Environment(loader=FileSystemLoader("templates"))
        return env.get_template(template).render(blogBase=blog_base, postListJson={}, i18n=i18nCN, IconList=IconList, IconViewBox=IconViewBox, IconStrokeWidth=IconStrokeWidth)

    @staticmethod
    def _plist_base(**overrides):
        base = {
            "title": "T", "homeUrl": "https://example.com/blog", "nightTheme": "dark", "dayTheme": "light",
            "faviconUrl": "", "GMEEK_VERSION": "v2.4", "avatarUrl": "https://example.com/a.png",
            "displayTitle": "T", "subTitle": "s", "issuesUrl": "https://github.com/x/y/issues",
            "lang": "zh-CN", "searchBaseUrl": "https://example.com/blog/",
            "singeListJson": {}, "labelHueDict": {}, "commentLabelColor": "#006b75",
            "prevUrl": "disabled", "nextUrl": "disabled", "firstUrl": "disabled", "lastUrl": "disabled",
        }
        base.update(overrides)
        return base

    def test_html_lang_comes_from_config(self):
        html = self._render("plist.html", self._plist_base())
        assert '<html lang="zh-CN"' in html

    def test_search_page_loads_bundle_and_prefills_term(self):
        html = self._render("search.html", self._plist_base())
        assert "pagefind/pagefind-ui.css" in html
        assert "pagefind/pagefind-ui.js" in html
        # 子路径部署: 结果链接必须按 homeUrl 补全
        assert 'baseUrl: "https://example.com/blog/"' in html
        assert "triggerSearch" in html

    def test_plist_search_targets_local_page(self):
        html = self._render("plist.html", self._plist_base())
        form = re.search(r"<form[^>]*>", html).group(0)
        assert 'action="https://example.com/blog/search.html"' in form
        # 负向控制: 不得再跳转到 GitHub issue 搜索
        assert "issuesUrl" not in form
        assert "target=" not in form


class TestSearchBoxSizing:
    """搜索框尺寸必须经 Pagefind 的 --pagefind-ui-scale 统一缩放。

    回归: 曾经只覆盖 .pagefind-ui__search-input 的 height/font-size, 而放大镜图标
    (.pagefind-ui__form::before, top:23*scale) 与清除按钮 (.pagefind-ui__search-clear,
    top:3*scale / height:58*scale) 都是按 scale 绝对定位的, 不跟着变 → 偏出垂直中心、甚至溢出。
    """

    @staticmethod
    def _html():
        return TestSearchPageSmoke._render("search.html", TestSearchPageSmoke._plist_base())

    def test_scales_via_pagefind_variable(self):
        html = self._html()
        m = re.search(r"--pagefind-ui-scale:\s*([0-9.]+)", html)
        assert m, "search.html 必须设置 --pagefind-ui-scale"
        assert 0.5 <= float(m.group(1)) <= 1.0

    def test_does_not_override_input_height(self):
        # 负向控制: 不得单独改输入框高度/字号(会破坏 scale 几何)
        compact = self._html().replace(" ", "").replace("\n", "")
        assert "pagefind-ui__search-input{" not in compact

    def test_internal_geometry_vertically_centered(self):
        # 按 Pagefind 的几何公式验证: 图标与清除按钮在所选 scale 下确实居中
        html = self._html()
        scale = float(re.search(r"--pagefind-ui-scale:\s*([0-9.]+)", html).group(1))
        input_h = 64 * scale                       # .pagefind-ui__search-input height
        icon_top, icon_size = 23 * scale, 18 * scale
        clear_top, clear_h = 3 * scale, 58 * scale
        assert abs((icon_top + icon_size / 2) - input_h / 2) < 0.01
        assert abs((clear_top + clear_h / 2) - input_h / 2) < 0.01
        # 清除按钮不得溢出输入框
        assert clear_top + clear_h <= input_h + 0.01


class TestSearchResultMeta:
    """检索结果展示标签与 issue 入口: 依赖文章页输出的 Pagefind meta。"""

    @staticmethod
    def _post(**over):
        return TestTemplateSmoke._render("post.html", TestTemplateSmoke._post_base(**over))

    def test_post_emits_pagefind_meta(self):
        html = self._post(labels=["前端", "blog"], postSourceUrl="https://github.com/x/y/issues/7")
        # 必须写成 [content] 形式: 默认取元素 textContent, 而 <meta> 的 textContent 为空
        assert 'data-pagefind-meta="labels[content]"' in html
        assert 'data-pagefind-meta="source[content]"' in html
        assert "https://github.com/x/y/issues/7" in html

    def test_labels_merged_into_single_json_value(self):
        # 同名 meta 出现多个元素时只保留最后一个, 故标签必须合并成一个值
        html = self._post(labels=["前端", "blog"])
        m = re.search(r'data-pagefind-meta="labels\[content\]" content=\'([^\']*)\'', html)
        assert m, "标签 meta 缺失"
        assert json.loads(m.group(1)) == ["前端", "blog"]
        assert html.count('data-pagefind-meta="labels[content]"') == 1

    def test_search_page_decorates_results(self):
        html = TestSearchPageSmoke._render("search.html", TestSearchPageSmoke._plist_base())
        assert "processResult" in html
        assert "pagefind-ui__result-meta" in html
        assert "pagefind-ui__result-labels" in html
        # 元信息挂在标题元素内, 使其紧随标题同排(标题行已改为 flex)
        assert 'card.querySelector(".pagefind-ui__result-title")' in html
        # 图标与文章页 Issue 按钮同款(icons.py 单一数据源)
        assert 'renderIcon("github"' in html


class TestSearchResultLabelLink:
    """检索结果的标签 chip 必须同时高亮 + 可点击跳到 tag.html。

    视觉与交互契约(详见 docs/adr/ 下检索结果 meta 相关 ADR):
      - 每个标签渲染为 <a class="Label">, 复用 base.html 的主题化色相样式
      - <a> 的 --label-hue 自定义属性由 blogBase['labelHueDict'] 派生, 缺失回退 210
      - href 形如 <homeUrl>/tag.html#<encodeURIComponent(name)>, 与 tag.html
        的 setClassDisplay(decodeURIComponent(...)) 闭环
    """

    @staticmethod
    def _html(label_hues=None):
        # 显式 None/没传 → 用非空示例字典; 显式传 dict(即使空)→ 直接用, 验证空字典注入场景
        hues = {"前端": 17, "blog": 42, "Tech?": 7} if label_hues is None else label_hues
        base = TestSearchPageSmoke._plist_base(labelHueDict=hues)
        return TestSearchPageSmoke._render("search.html", base)

    def test_labelHues_injected_from_blogBase(self):
        html = self._html({"前端": 17, "blog": 42})
        # 整段字典经 |tojson 注入, JS 端按名查表
        # 注意: |tojson 会把非 ASCII 字符转义成 \uXXXX, 这是 JSON 序列化规范, JS 端可正常解析
        m = re.search(r'var labelHues = (\{[^;]*\});', html)
        assert m, "未注入 labelHues 字典"
        import json as _json
        parsed = _json.loads(m.group(1))
        assert parsed == {"前端": 17, "blog": 42}

    def test_labelHues_missing_falls_back_to_empty_dict(self):
        # 旧状态文件无 labelHueDict: 模板应注入空字典, 由 JS 端统一回退默认色相 210
        html = self._html({})
        assert "var labelHues = {};" in html

    def test_decorator_creates_label_anchors(self):
        html = self._html()
        # 标签渲染为 <a class="Label">, 不再是纯 <span>; 这是高亮 + 跳转的前置
        assert 'a.className = "Label";' in html
        # --label-hue 走 setProperty 而不是 style.cssText, 便于与其它样式规则叠加
        assert 'setProperty("--label-hue"' in html
        # href 指向 tag.html 的 hash 锚点, URL 编码由 encodeURIComponent 负责
        # (homeUrl 由 Jinja 渲染期替换, 这里断言渲染后的绝对 URL 拼接)
        assert '"https://example.com/blog/tag.html#" + encodeURIComponent(name)' in html

    def test_anchor_reuses_Label_class_for_hue_styling(self):
        # 与 post.html / plist.html 的标签样式同源: base.html 的 .Label 已提供
        # 背景/字色/边框/主题色相; search.html 只补 hover 与尺寸, 不重写底色
        html = self._html()
        assert ".Label" in html   # CSS 出现 .Label 选择器, 走 base.html 的色相主题
        assert ":hover" in html   # 仅补一个 hover 反馈, 不替换底色

    def test_chinese_label_urlencoded_in_href(self):
        # 中文字符经 encodeURIComponent 后是 %E5%89%8D%E7%AB%AF; 真正端到端
        # URI 编码由浏览器/Node 在运行时执行, 这里只验模板渲染后的字面拼接结构
        html = self._html()
        assert '"https://example.com/blog/tag.html#" + encodeURIComponent(name)' in html
        assert "encodeURIComponent(name)" in html

    def test_meta_still_attaches_alongside_label_anchor(self):
        # 决策 2 的约定: 元信息(标签 + issue 入口)整块挂在标题行内
        # 这里钉死装饰函数仍会把整块 meta 挂到 title 元素
        html = self._html()
        assert 'card.querySelector(".pagefind-ui__result-title")' in html
        assert 'pagefind-ui__result-labels' in html
        assert 'pagefind-ui__result-source' in html


class TestSearchPerformance:
    """检索性能优化: 加载链去阻塞 + 每查询渲染减负 + 装饰器 raf 节流 + 加载状态视觉提示。"""

    @staticmethod
    def _html():
        return TestSearchPageSmoke._render("search.html", TestSearchPageSmoke._plist_base())

    def test_pagefind_ui_script_is_deferred(self):
        # 加载链去阻塞: pagefind-ui.js 必须 async/defer 加载, 不再同步阻塞 HTML 解析
        html = self._html()
        m = re.search(r'<script\s+([^>]*src="[^"]*pagefind-ui\.js"[^>]*)>', html)
        assert m, "pagefind-ui.js <script> 未找到"
        attrs = m.group(1)
        # 允许 defer 或 async; 同步(无修饰)会被这条规则挡住, 触发即代表阻塞回归
        assert ("defer" in attrs) or ("async" in attrs), attrs

    def test_pagefind_ui_is_preloaded(self):
        # 加载链去阻塞: head 内必须有 <link rel="preload" as="script"> 提前声明,
        # 让浏览器在解析 head 时就开始拉包, 与 HTML 解析并行
        html = self._html()
        m = re.search(r'<link\s+[^>]*rel="preload"[^>]*as="script"[^>]*>', html)
        assert m, "缺少 <link rel=preload as=script> 提前声明"
        assert "pagefind-ui.js" in m.group(0), "preload 必须指向 pagefind-ui.js"

    def test_page_size_is_twenty(self):
        # 每查询 DOM 量级决策: pageSize 由 Pagefind 默认 5 上调到 20,
        # "Load more" 触发频次下降(200 篇索引经验值 ~30% → ~10%)
        html = self._html()
        m = re.search(r"pageSize:\s*(\d+)", html)
        assert m, "PagefindUI.pageSize 未声明"
        assert int(m.group(1)) == 20, m.group(1)

    def test_sub_results_kept_true(self):
        # showSubResults 显式 true, 不被 Pagefind 默认 (false) 吞掉;
        # 用户确认保留段落级匹配高亮, 相关性线索优先于每查询 DOM 成本
        html = self._html()
        m = re.search(r"showSubResults:\s*(true|false)", html)
        assert m, "PagefindUI.showSubResults 未声明"
        assert m.group(1) == "true", m.group(1)

    def test_debounce_timeout_is_250ms(self):
        # debounceTimeoutMs=250 略紧于 Pagefind 默认 300, 减少连续键入时的冗余查询
        html = self._html()
        m = re.search(r"debounceTimeoutMs:\s*(\d+)", html)
        assert m, "PagefindUI.debounceTimeoutMs 未声明"
        assert int(m.group(1)) == 250, m.group(1)

    def test_process_result_uses_single_abs_url_key(self):
        # processResult 体内不再调用 urlKeys 双键索引, 只用 absUrl 单键写入 metaByUrl
        html = self._html()
        # 捕获锚定到 return 语句: 非贪婪 \} 会停在 `result.meta || {}` 的首个 }, 捕获不到赋值行
        m = re.search(r"processResult:\s*function\s*\(result\)\s*\{(.*?)\n\s*return result;", html, re.S)
        assert m, "PagefindUI.processResult 未找到"
        body = re.sub(r"//[^\n]*", "", m.group(1))   # 去注释, 断言只依赖代码
        assert "urlKeys(" not in body, "processResult 不应再调用 urlKeys 双键冗余"
        assert "metaByUrl[absUrl(result.url)] = info" in body, "processResult 应直接用 absUrl(result.url) 写入 metaByUrl"

    def test_lookup_no_longer_falls_back_to_pathname(self):
        # lookup 体内不再依赖 urlKeys 的 pathname 兜底分支, 单查 abs URL
        html = self._html()
        m = re.search(r"function lookup\(u\)\s*\{(.*?)\n\s*\}", html, re.S)
        assert m, "lookup 函数未找到"
        body = re.sub(r"//[^\n]*", "", m.group(1))
        assert "urlKeys" not in body, "lookup 不应再依赖 urlKeys 的 pathname 兜底"
        assert "absUrl" in body and "metaByUrl" in body

    def test_mutation_observer_uses_raf_throttle(self):
        # MutationObserver 回调必须用 requestAnimationFrame 节流,
        # 同一帧内多次触发合并为一次 decorate; 避免 Pagefind 渲染时反复 querySelectorAll
        html = self._html()
        # .observe( 前允许空白: 兼容单行 `}).observe(` 与多行 `})\n  .observe(` 两种形态
        m = re.search(r"new MutationObserver\(function\s*\(\)\s*\{(.*?)\}\)\s*\.observe\(", html, re.S)
        assert m, "MutationObserver 创建语句未找到"
        body = m.group(1)
        assert "requestAnimationFrame" in body, "observer 回调必须包含 requestAnimationFrame 节流"
        # pending flag 防止同帧多次入队, 断言收敛到回调体内
        assert re.search(r"rafPending|\bpending\b", body), "observer 回调内缺少 raf pending flag"

    def test_loading_state_styled(self):
        # spinner 只作用于 loading 态的消息: 计数/零结果消息后恒接 .pagefind-ui__results,
        # 故必须用 :not(:has(+ ...)) 把终态排除, 否则终态会出现永不停止的加载指示器
        html = self._html()
        assert ".pagefind-ui__message" in html
        assert ":not(:has(+ .pagefind-ui__results))" in html, "spinner 必须限定在 loading 态, 不得作用于计数/零结果消息"
        assert "::before" in html
        assert "rotate(360deg)" in html, "spinner 旋转动画未声明"


class TestIdlePrefetch:
    """首页 idle 预拉 pagefind-ui.js: 让"首页 → 检索页"路径省下 ~250KB 冷下载。"""

    @staticmethod
    def _html(template="base.html"):
        return TestSearchPageSmoke._render(template, TestSearchPageSmoke._plist_base())

    def test_base_html_prefetches_pagefind_ui_on_idle(self):
        # base.html 必须在 window load 后用 requestIdleCallback 插入 prefetch 链
        # (无 requestIdleCallback 时降级 setTimeout, 不阻塞首屏)
        html = self._html()
        assert "requestIdleCallback" in html
        assert "prefetch" in html
        # 监听 window load 事件而非 DOMContentLoaded, 保证主路径渲染完毕后再预拉
        assert re.search(r"window\.addEventListener\(\s*['\"]load['\"]", html)

    def test_idle_prefetch_targets_pagefind_ui_bundle(self):
        # prefetch 链是动态创建, 不在静态渲染结果里出现 —— 校验 JS 内 createElement("link")
        # 的属性赋值正确: rel=prefetch, as=script, href 含 pagefind-ui.js
        html = self._html()
        # 找到 idle callback 函数体内 createElement 块
        m = re.search(r"ric\(function\s*\(\)\s*\{(.*?)\}\);", html, re.S)
        assert m, "requestIdleCallback 函数体未找到"
        body = m.group(1)
        assert 'createElement("link")' in body or "createElement('link')" in body
        assert "l.rel" in body and "prefetch" in body
        assert "l.as" in body and "script" in body
        assert "l.href" in body and "pagefind-ui.js" in body


class TestSearchIndexBuilder:
    """中文短词子串索引生成器: 只抽「标题 + 正文容器内小节标题」, 跳过非正文页。"""

    _PAGE = (
        "<!DOCTYPE html><html><head><title>标题 A</title></head><body>"
        "<h1>页眉标题(正文外)</h1>"
        '<div class="markdown-body" data-pagefind-body>'
        "<h2>小节一</h2><p>正文</p><h3>小节二</h3>"
        "</div></body></html>"
    )

    @staticmethod
    def _mod():
        import importlib.util
        path = os.path.join(ROOT, "scripts", "build_search_index.py")
        spec = importlib.util.spec_from_file_location("build_search_index", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_extracts_title_and_body_headings(self):
        e = self._mod().extract_entry(self._PAGE, "post/1.html")
        assert e == {"u": "post/1.html", "t": "标题 A", "h": "小节一 小节二"}

    def test_headings_outside_body_are_ignored(self):
        e = self._mod().extract_entry(self._PAGE, "post/1.html")
        assert "页眉标题" not in e["h"]

    def test_page_without_body_is_skipped(self):
        html = "<html><head><title>x</title></head><body><h2>y</h2></body></html>"
        assert self._mod().extract_entry(html, "a.html") is None

    def test_empty_headings_yield_empty_string(self):
        html = "<html><head><title>T</title></head><body><div data-pagefind-body><p>只有正文</p></div></body></html>"
        e = self._mod().extract_entry(html, "a.html")
        assert e["t"] == "T" and e["h"] == ""

    def test_whitespace_is_collapsed(self):
        html = "<html><head><title>  A\n  B </title></head><body><div data-pagefind-body><h2> x\n  y </h2></div></body></html>"
        e = self._mod().extract_entry(html, "a.html")
        assert e["t"] == "A B" and e["h"] == "x y"

    def test_build_writes_sorted_index_and_skips_output_dir(self, tmp_path):
        mod = self._mod()
        (tmp_path / "post").mkdir()
        for slug, title in (("b", "B"), ("a", "A")):
            (tmp_path / "post" / f"{slug}.html").write_text(
                f"<html><head><title>{title}</title></head><body>"
                f'<div data-pagefind-body><h2>h{slug}</h2></div></body></html>',
                encoding="utf-8")
        # 无 data-pagefind-body 的页面(列表页/检索页)不进索引
        (tmp_path / "list.html").write_text(
            "<html><head><title>列表</title></head><body>no body</body></html>", encoding="utf-8")

        payload = mod.build(str(tmp_path))
        assert payload["v"] == 1 and payload["count"] == 2
        assert [e["u"] for e in payload["entries"]] == ["post/a.html", "post/b.html"]
        out = tmp_path / "search-index" / "index.json"
        assert out.is_file()
        assert json.loads(out.read_text(encoding="utf-8"))["count"] == 2


class TestExactMatchSearch:
    """中文短词精确匹配: 独立容器 + processTerm 挂接 + 懒加载子串索引 + 不隐藏 Pagefind 结果。"""

    @staticmethod
    def _html():
        return TestSearchPageSmoke._render("search.html", TestSearchPageSmoke._plist_base())

    def test_exact_container_is_declared_outside_pagefind_root(self):
        html = self._html()
        assert 'id="exactMatches"' in html
        # 容器先声明在 #search 之外(默认 hidden), 再由脚本移入结果抽屉
        assert html.index('id="exactMatches"') < html.index('<div id="search"></div>')

    def test_process_term_hook_present(self):
        html = self._html()
        assert "processTerm:" in html
        assert "loadExactIndex()" in html and "renderExact(" in html

    def test_index_url_derived_from_home_url(self):
        html = self._html()
        assert 'fetch("https://example.com/blog/search-index/index.json")' in html

    def test_injection_targets_drawer_before_results_area(self):
        html = self._html()
        assert ".pagefind-ui__drawer" in html
        assert ".pagefind-ui__results-area" in html
        # 插到 results-area 之前 => 位于输入框之下、Pagefind 结果之上
        assert "insertBefore(exactHost" in html

    def test_short_query_guard(self):
        html = self._html()
        assert "EXACT_MIN_LEN = 2" in html
        assert "q.length < EXACT_MIN_LEN" in html

    def test_pagefind_results_are_not_hidden(self):
        # 两轨并列: 脚本只切换自身容器的 hidden, 不得隐藏/清空 Pagefind 结果容器
        html = self._html()
        compact = html.replace(" ", "").replace("\n", "")
        assert "pagefind-ui__results-area{display:none" not in compact
        assert "pagefind-ui__results-area').hidden" not in compact
        assert "exactHost.hidden=false" in compact


class TestThemeSwitch:
    """主题切换: modeSwitch 必须按名读取 data-color-mode。

    约束: <html> 首个属性是 lang, 按下标取属性读不到明暗值, 切换会只能单向生效。
    """

    @staticmethod
    def _html():
        return TestSearchPageSmoke._render("plist.html", TestSearchPageSmoke._plist_base())

    def test_mode_switch_reads_attribute_by_name(self):
        html = self._html()
        m = re.search(r"function modeSwitch\(\)\s*\{(.*?)\n\}", html, re.S)
        assert m, "modeSwitch 未找到"
        body = re.sub(r"//[^\n]*", "", m.group(1))   # 去掉注释, 只看实际代码
        assert 'getAttribute("data-color-mode")' in body
        # 负向控制: 不得再按下标取属性
        assert "attributes[0]" not in body

    def test_index_lookup_would_miss_color_mode(self):
        # 记录「为何不能用下标」: <html> 首个属性不是明暗开关, 取 attributes[0] 拿不到 light/dark
        html = self._html()
        tag = re.search(r"<html\s+([^>]*)>", html).group(1)
        names = re.findall(r"([\w-]+)=", tag)
        assert "data-color-mode" in names
        assert names[0] != "data-color-mode"

    def test_toggle_can_reach_dark(self):
        # changeDark 必须存在且被 modeSwitch 分支引用, 否则无法切到深色
        html = self._html()
        assert "function changeDark()" in html and "function changeLight()" in html
        m = re.search(r"function modeSwitch\(\)\s*\{(.*?)\n\}", html, re.S).group(1)
        assert "changeDark()" in m and "changeLight()" in m


class TestDarkModeContrast:
    """深色模式兼容: 不得残留只在浅色底上可读的硬编码颜色。"""

    @staticmethod
    def _post(**over):
        return TestTemplateSmoke._render("post.html", TestTemplateSmoke._post_base(postNumber="1", **over))

    def test_post_meta_uses_theme_vars(self):
        html = self._post()
        # 元信息取主题变量, 深色底上仍可读(不得回落为固定深色字)
        for bad in ("color: #333", "color:#333", "color: #666", "color:#666"):
            assert bad not in html, bad
        assert "post-meta" in html
        assert "var(--color-fg-muted)" in html
        assert "var(--color-fg-default)" in html

    def test_summary_box_border_is_themed(self):
        html = self._post(description="摘要内容")
        assert "post-summary" in html
        assert "1px dashed #ccc" not in html
        assert "var(--color-border-default)" in html

    def test_markdown_body_tokens_follow_site_toggle(self):
        # github-markdown-css 只按 prefers-color-scheme 切换, 必须按 data-color-mode 重绑,
        # 否则「系统浅色 + 站点深色」时正文黑字压黑底
        html = self._post()
        assert '[data-color-mode="dark"] .markdown-body' in html
        assert '[data-color-mode="light"] .markdown-body' in html
        for tok in ("--color-fg-default", "--color-canvas-default",
                    "--color-canvas-subtle", "--color-border-default"):
            assert tok in html, tok

    def test_hardcoded_tokens_match_vendored_source(self):
        # 防止 github-markdown-css 升级后 token 值漂移(取值须逐字来自该文件)
        css = open(os.path.join(ROOT, "assets", "github-markdown-css@5.2.0",
                                "github-markdown.min.css"), encoding="utf-8").read()
        for v in ("#c9d1d9", "#8b949e", "#6e7681", "#0d1117", "#161b22", "#30363d", "#21262d",
                  "rgba(110,118,129,0.4)", "#58a6ff", "#1f6feb", "rgba(187,128,9,0.15)", "#f85149",
                  "#24292f", "#57606a", "#ffffff", "#f6f8fa", "#d0d7de", "hsla(210,18%,87%,1)",
                  "rgba(175,184,193,0.2)", "#0969da", "#fff8c5", "#cf222e"):
            assert v in css, v

    def test_dark_tokens_use_warm_neutral_palette(self):
        # 暗色 token 沿 WorkBuddy AI 客户端的暖灰中性方向, 不复刻 GitHub 冷蓝深
        html = self._post()
        # 暖灰中性深底(替代 GitHub 冷蓝深 #0d1117 / #21262d)
        assert "#1a1c20" in html, "canvas-default 应为暖灰 #1a1c20"
        assert "#22262c" in html, "canvas-subtle 应为 #22262c"
        assert "#383d45" in html, "border-default 应为 #383d45"
        assert "#2b2f37" in html, "border-muted 应为 #2b2f37"
        # 偏暖的浅字(替代 GitHub 冷调 #c9d1d9 / #8b949e / #6e7681)
        assert "#dde2e8" in html, "fg-default 应为 #dde2e8"
        assert "#9aa1ab" in html, "fg-muted 应为 #9aa1ab"
        # 柔和蓝调重音(替代 GitHub 鲜蓝 #58a6ff / 深蓝 #1f6feb)
        assert "#7ab8ff" in html, "accent-fg 应为 #7ab8ff"
        assert "#5a8fe6" in html, "accent-emphasis 应为 #5a8fe6"
        # 暖灰中性 token 抑制: 旧的冷蓝调值不得再出现在模板
        assert "#0d1117" not in html
        assert "#161b22" not in html
        assert "#30363d" not in html
        assert "#21262d" not in html
        assert "#c9d1d9" not in html
        assert "#8b949e" not in html
        assert "#58a6ff" not in html
        assert "#1f6feb" not in html
        assert "#f85149" not in html

    def test_floating_button_uses_theme_var(self):
        # 悬浮按钮不再硬编码 #007bff / #0056b3 / color:white, 改走主题变量
        html = self._post()
        assert "#007bff" not in html
        assert "#0056b3" not in html
        # 主题变量在浅深两态都被 .floating-button 消费
        assert "var(--color-accent-fg)" in html
        assert "var(--color-accent-emphasis)" in html
        # 暗色下加柔光描边, 体现 WorkBuddy 暗色按钮特征
        assert "[data-color-mode=\"dark\"] .floating-button" in html
        assert "rgba(255, 255, 255, 0.12)" in html

    def test_toc_uses_theme_vars(self):
        src = open(os.path.join(ROOT, "assets", "toc.js"), encoding="utf-8").read()
        code = re.sub(r"/\*[\s\S]*?\*/", "", src)   # 去掉注释, 只看实际样式
        for bad in ("#e1e4e8", "#ddd", "#b6e3ff"):
            assert bad not in code, bad
        assert "var(--color-border-default)" in code
        assert "var(--color-border-muted)" in code
        assert "var(--color-accent-subtle)" in code


class TestAdrBoundary:
    """架构决策记录的编号与文档链接只在 docs/ 内流转, 代码侧用自描述文本表达设计意图。"""

    # 本用例守护「代码中不得出现该编号前缀」, 自身遂由片段拼出, 避免自指误报
    _PREFIX = "A" + "DR"
    _REF = re.compile(_PREFIX + r"-\d{4}")

    @staticmethod
    def _code_files():
        pats = ["templates/**/*.py", "templates/**/*.html", "assets/**/*.js",
                "tests/**/*.py", "*.py"]
        files = []
        for pat in pats:
            files += [p for p in glob.glob(os.path.join(ROOT, pat), recursive=True)
                      if os.path.isfile(p)]
        return files

    def test_no_decision_record_number_in_code(self):
        hits = []
        for path in self._code_files():
            with open(path, encoding="utf-8") as fh:
                for lineno, line in enumerate(fh, 1):
                    if self._REF.search(line):
                        hits.append(f"{os.path.relpath(path, ROOT)}:{lineno}")
        assert not hits, hits


class TestCreateSearchHtml:
    def test_writes_search_page(self, tmp_path):
        fake = SimpleNamespace()
        fake.root_dir = str(tmp_path) + os.sep
        fake.i18n = i18nCN
        fake.renderHtml = lambda *a: GMEEK.renderHtml(fake, *a)
        fake.blogBase = {
            "title": "T", "homeUrl": "https://example.com/blog", "nightTheme": "dark", "dayTheme": "light",
            "faviconUrl": "", "GMEEK_VERSION": "v2.4", "lang": "zh-CN",
            "searchBaseUrl": "https://example.com/blog/",
            "labelHueDict": {},   # search.html 注入色相字典用, 旧测试夹具漏了
        }
        GMEEK.createSearchHtml(fake)
        html = (tmp_path / "search.html").read_text(encoding="utf-8")
        assert "pagefind/pagefind-ui.js" in html
        assert 'baseUrl: "https://example.com/blog/"' in html


class TestSearchIndexWorkflow:
    @staticmethod
    def _workflow():
        with open(os.path.join(".github", "workflows", "Gmeek.yml"), encoding="utf-8") as f:
            return f.read()

    def test_index_built_on_merged_site(self):
        content = self._workflow()
        assert "pagefind" in content
        # 索引必须建在合并后的完整站点上: 增量构建时 /opt/Gmeek/docs 只含本次重渲染的文章
        assert content.index("cp -a /opt/Gmeek/docs") < content.index("pagefind")
        # 非站点内容(ADR 等)先移除, 避免被索引
        assert content.index("rm -rf ${{ github.workspace }}/docs/adr") < content.index("pagefind")


class TestDeletedPruning:
    def test_prune_one_removes_entry_and_html(self, tmp_path):
        html = tmp_path / "docs" / "post" / "1.html"
        html.parent.mkdir(parents=True)
        html.write_text("<p>x</p>", encoding="utf-8")
        fake = SimpleNamespace()
        fake.blogBase = {"postListJson": {"P1": {"htmlDir": str(html)}}, "singeListJson": {}}
        GMEEK.prune_one(fake, "1")
        assert "P1" not in fake.blogBase["postListJson"]
        assert not html.exists()

    def test_runOne_handles_deleted_404(self, tmp_path):
        html = tmp_path / "docs" / "post" / "5.html"
        html.parent.mkdir(parents=True)
        html.write_text("x", encoding="utf-8")
        fake = SimpleNamespace()
        fake.blogBase = {"postListJson": {"P5": {"htmlDir": str(html)}}, "singeListJson": {}}
        fake.checkDir = lambda: None
        rendered = []
        fake.createPlistHtml = lambda: rendered.append("plist")
        fake.createFeedXml = lambda: rendered.append("feed")
        fake.createNavJson = lambda: rendered.append("nav")
        fake.createSearchHtml = lambda: rendered.append("search")
        fake.prune_one = lambda n: GMEEK.prune_one(fake, n)

        def _raise(*_a):
            raise GithubException(404, {"message": "Not Found"})

        fake.repo = SimpleNamespace(get_issue=_raise)
        # 404 必须被当作删除处理, 不得向上抛异常
        GMEEK.runOne(fake, "5")
        assert "P5" not in fake.blogBase["postListJson"]
        assert not html.exists()
        assert set(rendered) == {"plist", "feed", "nav", "search"}

    def test_prune_stale_removes_deleted(self, tmp_path):
        p1 = tmp_path / "docs" / "post" / "1.html"
        p2 = tmp_path / "docs" / "post" / "2.html"
        p1.parent.mkdir(parents=True)
        p1.write_text("x", encoding="utf-8")
        p2.write_text("x", encoding="utf-8")
        fake = SimpleNamespace()
        fake.blogBase = {
            "postListJson": {"P1": {"htmlDir": str(p1)}, "P2": {"htmlDir": str(p2)}},
            "singeListJson": {},
        }
        # 实况仅含 #1, #2 视为已删除
        live = SimpleNamespace(number=1, pull_request=None, user=SimpleNamespace(name="anaer"))
        fake.repo = SimpleNamespace(
            owner=SimpleNamespace(name="anaer"),
            get_issues=lambda state: iter([live]),
        )
        removed = GMEEK.prune_stale(fake)
        assert removed == ["2"]
        assert "P1" in fake.blogBase["postListJson"]
        assert "P2" not in fake.blogBase["postListJson"]
        assert p1.exists() and not p2.exists()


def _make_issue(num, title, body, owner="anaer", labels=(), state="open"):
    return SimpleNamespace(
        pull_request=None,
        user=SimpleNamespace(name=owner, login=owner),
        labels=[SimpleNamespace(name=l) for l in labels],
        number=num, title=title, body=body, state=state,
        created_at=datetime(2025, 1, 1), updated_at=datetime(2025, 1, 2),
        get_comments=lambda: SimpleNamespace(totalCount=0),
        get_events=lambda: [],
    )


def _build_runall_fake(issues):
    """构造最小 GMEEK 替身, get_issues 返回一次性生成器(复现 PyGithub PaginatedList
    被 list() 耗尽后再次迭代为空的陷阱)。渲染方法置为 no-op, 仅验证迭代修复。
    路径用相对形式(与线上一致), 调用方须 chdir 到隔离目录。"""
    fake = SimpleNamespace()
    fake.root_dir = "docs/"
    fake.post_folder = "post/"
    fake.post_dir = "docs/post/"
    fake.backup_dir = "backup/"
    fake.desc_retry_budget = 10
    fake.rebuild_cache = None
    fake.options = SimpleNamespace(repo_name="anaer/blog")
    fake.i18n = i18nCN
    fake.blogBase = {
        "postListJson": {}, "singeListJson": {},
        "singlePage": ["link", "about"], "homeUrl": "http://x",
        "i18n": "CN", "onePageListNum": 15, "title": "T", "subTitle": "S",
        "avatarUrl": "", "labelHueDict": {},
    }
    fake.labelHueDict = {}
    one_shot = (_ for _ in issues)  # 一次性生成器
    fake.repo = SimpleNamespace(
        owner=SimpleNamespace(name="anaer", login="anaer"),
        get_labels=lambda: [],
        full_name="anaer/blog",
        get_issues=lambda state: one_shot,
    )
    for m in ("addOnePostJson", "cleanFile", "checkDir", "renderHtml",
              "get_cached", "prune_one", "normalize_title", "decimal_to_hex"):
        setattr(fake, m, (lambda *a, _m=m, **k: getattr(GMEEK, _m)(fake, *a, **k)))
    fake.createPostHtml = lambda post: None
    fake.createPlistHtml = lambda: None
    fake.createFeedXml = lambda: None
    fake.createNavJson = lambda: None
    fake.createSearchHtml = lambda: None
    return fake


class TestResolveRunMode:
    def test_default_int_zero_is_full_rebuild(self):
        # 回归: argparse 缺省为整数 0, 手动触发(不传 --issue_number)必须走全量重建,
        # 不得因 0 != "0" 被误判为 runOne(0) 而报「issue #0 不存在」。
        assert resolve_run_mode(0) == "all"

    def test_string_zero_is_full_rebuild(self):
        assert resolve_run_mode("0") == "all"

    def test_empty_string_is_full_rebuild(self):
        assert resolve_run_mode("") == "all"

    def test_whitespace_is_full_rebuild(self):
        assert resolve_run_mode("  ") == "all"

    def test_number_is_single(self):
        assert resolve_run_mode(42) == "one"
        assert resolve_run_mode("42") == "one"

    def test_prune_takes_precedence(self):
        assert resolve_run_mode(0, prune=True) == "prune"


class TestRunAllIteration:
    def test_runAll_processes_all_issues_one_shot_iterable(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)  # addOnePostJson 写相对路径 backup/, 隔离到 tmp_path
        issues = [
            _make_issue(1, "A", "body A"),
            _make_issue(2, "B", "body B"),
            _make_issue(3, "C", "body C"),
        ]
        fake = _build_runall_fake(issues)
        GMEEK.runAll(fake)
        assert set(fake.blogBase["postListJson"].keys()) == {"P1", "P2", "P3"}


class TestCodeLangLabel:
    def test_extract_fence_langs(self):
        md = "前言\n\n```python\nx\n```\n\n```\nplain\n```\n\n~~~bash\necho\n~~~\n"
        assert Markdown2GithubHtml()._extract_fence_langs(md) == ["python", "", "bash"]

    def test_convert_adds_language_label(self):
        html = Markdown2GithubHtml().convert("```python\nprint(1)\n```")
        assert '<div class="code-block-wrapper has-lang">' in html
        assert ">python<" in html

    def test_convert_no_label_for_plain(self):
        html = Markdown2GithubHtml().convert("```\nplain\n```")
        assert '<div class="code-block-wrapper has-lang">' not in html

    def test_convert_label_alignment_two_fences(self):
        html = Markdown2GithubHtml().convert("```python\na\n```\n\n```bash\nb\n```")
        assert html.count('code-block-wrapper has-lang') == 2
        assert html.find(">python<") < html.find(">bash<")


class TestTocIndicators:
    @staticmethod
    def _js():
        with open(os.path.join(ROOT, "assets", "toc.js"), encoding="utf-8") as f:
            return f.read()

    def test_toggle_button_created(self):
        js = self._js()
        assert "toc-toggle" in js
        assert "itemByWrapper" in js

    def test_open_class_drives_collapse(self):
        js = self._js()
        assert ".toc-item:not(.open) > .toc-children" in js
        assert "classList.toggle('open'" in js

    def test_toggle_slot_reserved_for_all_items(self):
        # 切换按钮已右对齐; 槽位必须**无条件**预留, 不能只给带子节点的项
        # (否则同级里有/无子节点的项文字会差一个槽位、无法对齐).
        # 注意: 现在槽位挪到右侧(paddingRight), 左侧不再预留
        js = self._js()
        line = [l for l in js.splitlines() if "paddingLeft" in l][0]
        # 左侧只放缩进, 不含 TOGGLE_SLOT
        assert "TOGGLE_SLOT" not in line
        # 同时钉死「不带子节点也预留槽位」— 搜索 paddingRight 那行
        right_line = [l for l in js.splitlines() if "paddingRight" in l][0]
        assert "TOGGLE_SLOT" in right_line
        assert "children.length" not in right_line
        assert js.count("const TOGGLE_SLOT") == 1

    def test_toggle_anchored_to_right(self):
        # 切换按钮绝对定位到右侧 (right: 2px), 左侧不再有 left: -2px 锚点
        js = self._js()
        assert "right: 2px;" in js
        # 旧版的 left: -2px 不得再出现(若用 left, 改 right 也行; 但为了清晰统一用 right)
        assert "left: -2px;" not in js


class TestSectionsFold:
    @staticmethod
    def _js():
        with open(os.path.join(ROOT, "assets", "sections.js"), encoding="utf-8") as f:
            return f.read()

    def test_section_wrap_and_toggle_present(self):
        js = self._js()
        assert "heading-section" in js
        assert "section-toggle" in js
        assert "classList.toggle('collapsed')" in js

    def test_sections_script_loaded_in_post(self):
        with open(os.path.join(ROOT, "templates", "post.html"), encoding="utf-8") as f:
            assert "assets/sections.js" in f.read()

    def test_toggle_selector_matches_insertion_point(self):
        # 按钮插在标题内部(h > .section-toggle), 选择器必须跨过标题层级;
        # 若写成直系子代则一条都不匹配, 按钮退回浏览器原生样式
        js = self._js()
        css = re.sub(r"/\*[\s\S]*?\*/", "", js)   # 去掉注释, 只看实际样式
        assert "h.insertBefore(toggle, h.firstChild)" in js
        assert ":is(h1,h2,h3,h4,h5,h6) > .section-toggle" in css
        assert ".heading-section > .section-toggle" not in css
        assert ".heading-section.collapsed > .section-toggle" not in css


class TestPostSearchBox:
    def test_post_header_has_search_form(self):
        html = TestTemplateSmoke._render("post.html", TestTemplateSmoke._post_base())
        assert 'class="site-search"' in html
        assert 'name="q"' in html
        # 提交到站内检索页(读取 ?q= 触发), 而非跳转 GitHub
        assert "https://example.com/blog/search.html" in html


class TestSearchBoxUnification:
    """三处搜索框(列表页 / 标签页 / 文章页)共用 base.html 的 .site-search 组件。"""

    @staticmethod
    def _plist_base(**overrides):
        base = {
            "title": "T", "homeUrl": "https://example.com/blog", "nightTheme": "dark", "dayTheme": "light",
            "faviconUrl": "", "GMEEK_VERSION": "v2.4", "avatarUrl": "https://example.com/a.png",
            "displayTitle": "T", "subTitle": "s", "issuesUrl": "https://github.com/x/y/issues",
            "lang": "zh-CN", "searchBaseUrl": "https://example.com/blog/",
            "singeListJson": {}, "labelHueDict": {}, "commentLabelColor": "#006b75",
            "tagListJson": {}, "themeMode": "auto",
            "prevUrl": "disabled", "nextUrl": "disabled", "firstUrl": "disabled", "lastUrl": "disabled",
        }
        base.update(overrides)
        return base

    def _render(self, tpl, base):
        return TestTemplateSmoke._render(tpl, base)

    def test_all_three_pages_use_shared_component(self):
        for tpl in ("plist.html", "tag.html", "post.html"):
            base = TestTemplateSmoke._post_base(postNumber="1") if tpl == "post.html" else self._plist_base()
            html = self._render(tpl, base)
            assert 'class="site-search' in html, tpl

    def test_component_defined_once_in_base(self):
        # 样式只在 base.html 定义一次, 各页不得再自带搜索框样式
        base_html = self._render("plist.html", self._plist_base())
        assert ".site-search input[type=\"search\"]" in base_html
        for tpl in ("plist.html", "tag.html", "post.html"):
            base = TestTemplateSmoke._post_base(postNumber="1") if tpl == "post.html" else self._plist_base()
            html = self._render(tpl, base)
            assert ".post-search" not in html, tpl
            assert ".subnav-search" not in html, tpl

    def test_legacy_hooks_removed(self):
        # 旧类名与死图标(searchSVG 无任何 JS 引用)不得残留
        for tpl in ("plist.html", "tag.html"):
            html = self._render(tpl, self._plist_base())
            assert "subnav-search" not in html, tpl
            assert "searchSVG" not in html, tpl

    def test_search_kept_on_narrow_screens(self):
        # 窄屏保留搜索框(不再整块隐藏), 仅收窄
        compact = self._render("plist.html", self._plist_base()).replace(" ", "")
        assert ".site-search{display:none}" not in compact
        assert "site-searchform{display:none" not in compact
        assert "width:104px" in compact

    def test_tag_js_uses_new_hook(self):
        html = self._render("tag.html", self._plist_base())
        assert 'class="site-search-input"' in html
        assert 'querySelector(".site-search-input")' in html
        assert "subnav-search-input" not in html


class TestIconRegistry:
    # 模板 / 代码块 / 前端引用的图标名必须全部登记在单一数据源 icons.py 中
    REQUIRED = {
        "post", "link", "about", "sun", "moon", "search", "rss", "upload", "github", "home", "subway",
        "plus", "minus", "chevron", "copy", "check", "wrap", "lines", "fold", "eye", "pen",
    }

    def test_all_referenced_icons_registered(self):
        assert self.REQUIRED <= set(ICONS)

    def test_render_shape(self):
        svg = render_icon("home", cls="octicon", svg_id="pathHome")
        assert svg.startswith('<svg class="octicon" id="pathHome" width="16" height="16" viewBox="0 0 24 24"')
        assert 'id="pathHome"' in svg
        assert 'fill="none"' in svg                 # 线性描边: 不填充
        assert 'stroke="currentColor"' in svg
        assert 'stroke-width="1.5"' in svg
        assert 'stroke-linecap="round"' in svg
        assert svg.endswith("</svg>")

    def test_render_has_no_single_quotes(self):
        # 需可安全嵌入 JS 单引号字符串(复制/成功图标在 EXTRA_JS 中回填)
        for name in self.REQUIRED:
            assert "'" not in render_icon(name)

    def test_all_icons_use_24_viewbox(self):
        # 统一画布: 所有图标(含原 16 画布)现均为 24x24
        for name in self.REQUIRED:
            assert viewbox(name) == "0 0 24 24"
            assert 'viewBox="0 0 24 24"' in render_icon(name)

    def test_theme_switch_icon_has_id(self):
        # 主题切换图标: id 在 svg 上, 内层标记即 changeDark/Light 回填内容
        svg = render_icon("sun", svg_id="themeSwitch")
        assert 'id="themeSwitch"' in svg
        assert ICONS["sun"].strip() in svg

    def test_render_without_class(self):
        assert render_icon("plus", cls="").startswith("<svg width=")


class TestIconFillOverride:
    """描边图标必须压过第三方 CSS 的 fill:currentcolor, 否则正文区(代码块控件/标题折叠)图标会被填实。"""

    VENDOR_CSS = os.path.join(ROOT, "assets", "github-markdown-css@5.2.0", "github-markdown.min.css")

    @staticmethod
    def _specificity(selector):
        """(id, 类/伪类, 类型) 三元组; 只覆盖本例涉及的选择器形态(无属性选择器、无伪元素)。"""
        ids = len(re.findall(r"#[-\w]+", selector))
        classes = len(re.findall(r"[-\w]*\.[-\w]+", selector)) + len(re.findall(r":(?!:)[-a-z]+", selector))
        rest = re.sub(r"#[-\w]+|[-\w]*\.[-\w]+|::[-a-z]+|:(?!:)[-a-z]+", " ", selector)
        return (ids, classes, len(re.findall(r"[A-Za-z][-a-z0-9]*", rest)))

    @classmethod
    def _fill_selectors(cls, path, value):
        with open(path, encoding="utf-8") as fh:
            css = fh.read()
        found = [" ".join(m.group(1).split())
                 for m in re.finditer(r"([^{}]+)\{[^{}]*fill:%s[^{}]*\}" % value, css, re.I)]
        assert found, "未找到 fill:%s 规则(%s)" % (value, path)
        return found

    def test_vendor_fills_octicons_inside_markdown_body(self):
        # 成因: 高特异性来自 .markdown-body 前缀, 而非 .octicon 本身
        assert any("markdown-body" in s and "octicon" in s
                   for s in self._fill_selectors(self.VENDOR_CSS, "currentcolor"))

    def test_override_outweighs_every_vendor_rule(self):
        ours = max(self._specificity(s)
                   for s in self._fill_selectors(os.path.join(ROOT, "templates", "base.html"), "none"))
        for vendor in self._fill_selectors(self.VENDOR_CSS, "currentcolor"):
            assert ours > self._specificity(vendor), (ours, vendor)

    def test_bare_element_selector_would_have_lost(self):
        # 负向控制: 单用 svg.octicon(0,1,1) 压不过 .markdown-body .octicon(0,2,0), 正是图标糊掉的成因
        assert self._specificity("svg.octicon") < self._specificity(".markdown-body .octicon")

    def test_override_keeps_bare_svg_for_outside_body(self):
        # 正文之外(头部图标、tag 页列表)同样要保持描边
        selectors = self._fill_selectors(os.path.join(ROOT, "templates", "base.html"), "none")
        assert any("svg.octicon" in s for s in selectors), selectors



class TestIconTemplates:
    # 模板必须经统一宏渲染: 不得残留 Jinja 标记, 图标在服务端填充
    def _render(self, template, blog_base, post_list=None):
        env = Environment(loader=FileSystemLoader("templates"))
        return env.get_template(template).render(
            blogBase=blog_base, postListJson=post_list or {}, i18n=i18nCN,
            IconList=IconList, IconViewBox=IconViewBox, IconStrokeWidth=IconStrokeWidth,
        )

    def test_post_no_raw_jinja_and_icons_filled(self):
        html = self._render("post.html", TestTemplateSmoke._post_base(postNumber="1"))
        assert "{{" not in html and "{%" not in html
        assert 'id="pathHome"' in html and 'm3 9 9-7 9 7v11' in html  # home 已服务端填充(线性描边)
        assert 'stroke-width="1.5"' in html
        assert 'id="themeSwitch"' in html

    def test_post_ui_glyphs_are_svg_not_emoji(self):
        # 浏览量 / 编辑 / 新增按钮走图标注册表, 不留表情与文本字符
        html = self._render("post.html", TestTemplateSmoke._post_base(postNumber="1"))
        assert "👁" not in html and "🖋" not in html
        assert 'class="octicon vercount-icon"' in html
        assert 'edit-post"><svg' in html and 'new-post"><svg' in html
        assert 'new-post">+<' not in html

    def test_plist_subway_and_single_page_icons(self):
        base = {
            "title": "T", "homeUrl": "https://example.com/blog", "displayTitle": "T", "subTitle": "s",
            "faviconUrl": "", "GMEEK_VERSION": "v2.4", "avatarUrl": "https://example.com/a.png",
            "issuesUrl": "https://github.com/x/y/issues", "labelHueDict": {}, "commentLabelColor": "#006b75",
            "singeListJson": {"S1": {"label": "about", "postTitle": "About"}},
            "prevUrl": "disabled", "nextUrl": "disabled", "firstUrl": "disabled", "lastUrl": "disabled",
        }
        html = self._render("plist.html", base)
        assert "{{" not in html and "{%" not in html
        assert 'viewBox="0 0 24 24"' in html                 # 统一 24 画布
        assert 'id="About"' in html and 'M20 21v-2a4 4 0 0 0-4-4H8' in html  # 单页 about 图标服务端填充

    def test_search_and_tag_no_raw_jinja(self):
        base = {
            "title": "T", "homeUrl": "https://example.com/blog", "displayTitle": "T",
            "faviconUrl": "", "GMEEK_VERSION": "v2.4", "issuesUrl": "https://github.com/x/y/issues",
            "labelHueDict": {}, "tagListJson": {}, "themeMode": "auto",
            "searchBaseUrl": "https://example.com/blog/",
        }
        for tpl in ("search.html", "tag.html"):
            html = self._render(tpl, base)
            assert "{{" not in html and "{%" not in html, tpl
            assert 'id="pathHome"' in html and 'id="themeSwitch"' in html

    def test_code_block_controls_use_registry(self):
        html = Markdown2GithubHtml().convert("```python\nprint(1)\n```")
        assert "__ICON_CHECK__" not in html and "__ICON_COPY__" not in html
        assert "M20 6 9 17l-5-5" in html          # check 图标(线性描边)
        assert "M5 15H4a2 2 0 0 1-2-2V4" in html  # copy 图标(线性描边)
        assert 'viewBox="0 0 24 24"' in html
        assert 'viewBox="0 0 20 20"' not in html  # 旧 20x20 复制图标已移除


class TestSinglePageLabel:
    def test_single_page_entry_has_label(self, tmp_path, monkeypatch):
        # 回归: singeListJson 条目必须带 label, 否则 plist 的 href 与图标取值落空
        monkeypatch.chdir(tmp_path)
        fake = _build_runall_fake([])
        GMEEK.checkDir(fake)
        issue = _make_issue(7, "About", "content", labels=["about"])
        post = GMEEK.addOnePostJson(fake, issue)
        assert post is not None
        assert post["label"] == "about"
        assert post["postUrl"] == "about.html"
        assert "P7" in fake.blogBase["singeListJson"]


class TestCodeCopyFeedback:
    def test_copy_button_color_matches_controls_and_feedback(self):
        html = Markdown2GithubHtml().convert("```python\nx\n```")
        # 控件共用同一套图标按钮语言(主题 muted 色), 成功时短暂转绿(主题 success 色)
        assert ".fold-btn, .copy-btn, .code-toggle" in html
        assert "color: var(--fgColor-muted, var(--color-fg-muted))" in html
        assert ".copy-btn.copied" in html and "var(--color-success-fg)" in html
        assert "classList.add('copied')" in html
        assert "classList.remove('copied')" in html


class TestRelatedArticlesContract:
    """关联文章由 assets/nav.js 在运行时填充: 模板提供的属性名必须与脚本读取的一致。"""

    @staticmethod
    def _sources():
        with open(os.path.join(ROOT, "assets", "nav.js"), encoding="utf-8") as fh:
            js = fh.read()
        with open(os.path.join(ROOT, "templates", "post.html"), encoding="utf-8") as fh:
            tpl = fh.read()
        return js, tpl

    def test_attribute_names_match_template(self):
        js, tpl = self._sources()
        for attr in ("data-nav-url", "data-post-number", "data-labels", "data-heading"):
            assert 'getAttribute("%s")' % attr in js, attr
            assert "%s=" % attr in tpl, attr

    def test_selector_targets_related_container(self):
        js, tpl = self._sources()
        assert 'querySelector(".related-posts[data-nav-url]")' in js
        assert 'class="related-posts"' in tpl

    def test_related_block_has_no_box(self):
        # 关联区块与正文同层: 不借 Primer 容器底色与 border 工具类, 条目间也不要横线
        _, tpl = self._sources()
        rule = re.search(r"\.related-posts\{([^}]*)\}", tpl).group(1)
        assert "background:none" in rule and "border:0" in rule
        assert "border-radius" not in rule
        item = re.search(r"\.related-posts \.SideNav-item\{([^}]*)\}", tpl).group(1)
        assert "background:none" in item and "padding-left:0" in item
        assert "border-top:0" in item          # 条目间也不要横线
        assert ".related-posts .SideNav-item:last-child{box-shadow:none;}" in tpl
        # 负向控制: 容器上不得再出现 SideNav / border 类(那两者正是底色与边框的来源)
        assert 'class="SideNav related-posts"' not in tpl
        assert 'related-posts border' not in tpl

    def test_no_prev_next_leftover(self):
        # 负向控制: 上一页/下一页的实现痕迹不得残留在脚本或模板里
        js, tpl = self._sources()
        for name in ("previous_page", "next_page", "paginate-container", "rel=\"previous\""):
            assert name not in js, name
            assert name not in tpl, name

    def test_empty_result_removes_block(self):
        # 无标签 / 无命中 / 数据非数组 / 拉取失败都不应留下空壳区块
        js, _ = self._sources()
        assert "box.remove()" in js
        assert js.count("hide();") == 3
        assert ".catch(hide)" in js

    def test_heading_comes_from_i18n(self):
        js, tpl = self._sources()
        assert "i18n['relatedPosts']" in tpl
        assert "相关文章" in i18nCN["relatedPosts"]
        assert i18n["relatedPosts"] == "Related posts"


class TestIconButtonUnification:
    """内容区图标按钮(标题折叠 / 目录 +− / 代码块控件)共用同一套交互与配色语言。"""

    @staticmethod
    def _sources():
        def read(*parts):
            with open(os.path.join(ROOT, *parts), encoding="utf-8") as fh:
                return fh.read()
        return {
            "sections.js": read("assets", "sections.js"),
            "toc.js": read("assets", "toc.js"),
            "md2html": read("md2html.py"),
        }

    def test_no_hardcoded_grey_palette(self):
        # 旧的两级硬编码灰(#6e7681 浅色 / #8b949e 深色)不得再出现, 一律走主题变量
        for name, src in self._sources().items():
            code = re.sub(r"/\*[\s\S]*?\*/", "", src)
            assert "#6e7681" not in code, name
            assert "#8b949e" not in code, name

    def test_shared_idiom_present_in_all_three(self):
        src = self._sources()
        for name in ("sections.js", "toc.js", "md2html"):
            assert "var(--fgColor-muted, var(--color-fg-muted))" in src[name], name
            assert "opacity: .6" in src[name], name

    def test_hover_background_exempts_section_toggle(self):
        # hover 背景为具名豁免: 标题折叠是行内文本控件, 不设背景
        src = self._sources()
        for name in ("toc.js", "md2html"):
            assert "var(--bgColor-muted, var(--color-canvas-subtle))" in src[name], name
        assert "var(--bgColor-muted, var(--color-canvas-subtle))" not in src["sections.js"]

    def test_hover_reveals_opacity(self):
        src = self._sources()
        assert ".section-toggle:hover" in src["sections.js"]
        assert ".toc-toggle:hover" in src["toc.js"]
        assert ".code-toggle:hover" in src["md2html"]

    def test_section_toggle_has_no_box(self):
        # 无背景框 → 不需要内边距与圆角(否则 chevron 会无理由缩进标题)
        css = re.search(r"\.heading-section > :is\(h1,h2,h3,h4,h5,h6\) > \.section-toggle\s*\{[^}]*\}",
                        self._sources()["sections.js"]).group(0)
        assert "padding: 0" in css
        assert "border-radius" not in css
        assert "background: transparent" in css

    def test_code_toolbar_has_no_container_opacity(self):
        # 容器级透明度会与按钮级 .6 叠加成 .27; 统一后由按钮自身承担
        src = self._sources()["md2html"]
        block = re.search(r"\.code-block-controls\s*\{[^}]*\}", src).group(0)
        assert "opacity" not in block


class TestOnekoListPageOnly:
    """oneko 仅列表页加载: base.html 不再全站引入, 文章/标签/检索页不加载。"""

    @staticmethod
    def _render(tpl, base, post_list=None):
        env = Environment(loader=FileSystemLoader("templates"))
        return env.get_template(tpl).render(
            blogBase=base, postListJson=post_list or {}, i18n=i18nCN,
            IconList=IconList, IconViewBox=IconViewBox, IconStrokeWidth=IconStrokeWidth)

    @staticmethod
    def _base():
        return {
            "title": "T", "homeUrl": "https://example.com/blog", "nightTheme": "dark", "dayTheme": "light",
            "faviconUrl": "", "GMEEK_VERSION": "v2.4", "avatarUrl": "https://example.com/a.png",
            "displayTitle": "T", "subTitle": "s", "issuesUrl": "https://github.com/x/y/issues",
            "lang": "zh-CN", "singeListJson": {}, "labelHueDict": {}, "commentLabelColor": "#006b75",
            "prevUrl": "disabled", "nextUrl": "disabled", "firstUrl": "disabled", "lastUrl": "disabled",
        }

    def test_plist_loads_oneko(self):
        html = self._render("plist.html", self._base())
        assert "assets/oneko.js/oneko.js" in html

    def test_base_has_no_oneko(self):
        # 负向控制: base.html 不得再全站加载 oneko
        with open(os.path.join(ROOT, "templates", "base.html"), encoding="utf-8") as fh:
            assert "oneko" not in fh.read()

    def test_post_tag_search_do_not_load_oneko(self):
        base = self._base()
        post_base = TestTemplateSmoke._post_base(postNumber="1")
        for tpl, b in (("post.html", post_base), ("tag.html", base), ("search.html", base)):
            html = self._render(tpl, b)
            assert "oneko" not in html, tpl


class TestListItemIssueEntry:
    """列表项标题后插入 issue 入口: 指向 postSourceUrl, 沿用低对比图标语言。"""

    @staticmethod
    def _render(post_list):
        env = Environment(loader=FileSystemLoader("templates"))
        base = {
            "title": "T", "homeUrl": "https://example.com/blog", "nightTheme": "dark", "dayTheme": "light",
            "faviconUrl": "", "GMEEK_VERSION": "v2.4", "avatarUrl": "https://example.com/a.png",
            "displayTitle": "T", "subTitle": "s", "issuesUrl": "https://github.com/x/y/issues",
            "lang": "zh-CN", "singeListJson": {}, "labelHueDict": {}, "commentLabelColor": "#006b75",
            "prevUrl": "disabled", "nextUrl": "disabled", "firstUrl": "disabled", "lastUrl": "disabled",
        }
        return env.get_template("plist.html").render(
            blogBase=base, postListJson=post_list, i18n=i18nCN,
            IconList=IconList, IconViewBox=IconViewBox, IconStrokeWidth=IconStrokeWidth)

    @staticmethod
    def _post(number, source_url):
        return {
            "number": str(number), "postTitle": "T%d" % number, "postUrl": "post/%d.html" % number,
            "labels": [], "commentNum": 0, "top": 0, "postSourceUrl": source_url,
            "createdAt": 100 * number, "updatedAt": 100 * number,
        }

    def test_issue_link_present_with_source_url(self):
        url = "https://github.com/x/y/issues/42"
        html = self._render({"P42": self._post(42, url)})
        assert 'class="list-issue-link"' in html
        assert 'href="%s"' % url in html
        assert 'target="_blank"' in html

    def test_issue_link_nested_anchor_wrapped_in_object(self):
        # 负向控制: 列表项外层已是 <a>, 内嵌 issue 链接必须经 <object> 包裹, 否则 HTML 非法嵌套
        html = self._render({"P1": self._post(1, "https://github.com/x/y/issues/1")})
        assert '<object><a class="list-issue-link"' in html

    def test_issue_icon_uses_github_registry(self):
        html = self._render({"P1": self._post(1, "https://github.com/x/y/issues/1")})
        # github 图标已在 icons.py 登记, 模板经 macro 渲染为线性描边 svg
        assert 'stroke="currentColor"' in html
        assert 'stroke-width="1.5"' in html

    def test_issue_link_not_on_post_or_search(self):
        # 负向控制: 该入口只在列表页; 文章页/检索页不得出现 list-issue-link
        post_html = TestTemplateSmoke._render("post.html", TestTemplateSmoke._post_base(postNumber="1"))
        assert "list-issue-link" not in post_html
        search_html = TestSearchPageSmoke._render("search.html", TestSearchPageSmoke._plist_base())
        assert "list-issue-link" not in search_html
