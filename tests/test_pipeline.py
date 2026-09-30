# -*- coding: utf-8 -*-
"""批次 A/B 纯函数单测: 收录过滤 / 置顶判定 / 缓存与重建 / 导航 / 时间 / 引用替换 / 色标 / tag 数据投影 / 图片懒加载 / 行号包裹 / 渲染版本 / 模板冒烟。"""
import calendar
import json
import os
import re
from datetime import datetime, timezone
from types import SimpleNamespace

from jinja2 import Environment, FileSystemLoader

from Gmeek import (
    GMEEK, IconList, i18n, i18nCN, RENDER_VERSION, resolve_top, carry_cache, should_include_issue,
    resolve_regen_mode, slim_state, nav_order, nav_neighbors, neighbor_keys,
    format_datetime_utc8, format_date_utc8,
    deterministic_color, replace_issue_refs, tag_data, is_html_stale,
)
from md2html import Markdown2GithubHtml

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


def mk_post(number, created, updated=None):
    return {"number": str(number), "createdAt": created, "updatedAt": updated if updated else created,
            "postTitle": "T%d" % number, "postUrl": "post/%d.html" % number}


class TestNavNeighbors:
    def _fixture(self):
        return {"P1": mk_post(1, 100), "P2": mk_post(2, 200), "P3": mk_post(3, 300)}

    def test_middle_ok(self):
        pj = self._fixture()
        prev, nxt = nav_neighbors(nav_order(pj), pj, "2")
        assert prev["number"] == "1" and nxt["number"] == "3"

    def test_oldest_hides_prev(self):
        pj = self._fixture()
        prev, nxt = nav_neighbors(nav_order(pj), pj, "1")
        assert prev is None and nxt["number"] == "2"

    def test_newest_hides_next(self):
        pj = self._fixture()
        prev, nxt = nav_neighbors(nav_order(pj), pj, "3")
        assert prev["number"] == "2" and nxt is None

    def test_ignores_top_and_closed(self):
        # 负向控制: 置顶/关闭不改变相邻关系
        pj = self._fixture()
        pj["P2"]["top"] = 1
        pj["P3"]["top"] = -1
        prev, nxt = nav_neighbors(nav_order(pj), pj, "2")
        assert prev["number"] == "1" and nxt["number"] == "3"

    def test_tie_break_by_number(self):
        pj = {"P2": mk_post(2, 100), "P1": mk_post(1, 100)}
        prev, nxt = nav_neighbors(nav_order(pj), pj, "1")
        assert prev is None and nxt["number"] == "2"

    def test_missing_number_returns_none(self):
        pj = self._fixture()
        assert nav_neighbors(nav_order(pj), pj, "99") == (None, None)


class TestNeighborKeys:
    def test_new_post_refreshes_previous_newest(self):
        # 新增文章到末尾: 旧序无该文, 只需刷新新序中的前邻
        assert neighbor_keys(["P1", "P2"], ["P1", "P2", "P3"], "P3") == ["P2"]

    def test_middle_change_refreshes_both_sides(self):
        keys = ["P1", "P2", "P3"]
        assert neighbor_keys(keys, keys, "P2") == ["P1", "P3"]

    def test_reorder_covers_old_and_new_neighbors(self):
        # 负向控制: 位置变化时旧邻(P1)与新邻(P3)都要刷新且去重
        assert set(neighbor_keys(["P1", "P2", "P3"], ["P1", "P3", "P2"], "P2")) == {"P1", "P3"}

    def test_endpoint_has_single_neighbor(self):
        assert neighbor_keys([], ["P1", "P2"], "P1") == ["P2"]

    def test_absent_target_is_empty(self):
        assert neighbor_keys([], [], "P9") == []


class TestRunOneRefreshesNeighbors:
    @staticmethod
    def _fake(post_list):
        fake = SimpleNamespace()
        fake.blogBase = {"postListJson": post_list, "singeListJson": {}}
        fake._nav_keys = None
        fake.checkDir = lambda: None
        fake.get_nav_keys = lambda: GMEEK.get_nav_keys(fake)
        rendered = []
        fake.createPostHtml = lambda post: rendered.append(post["number"])
        fake.createPlistHtml = lambda: None
        fake.createFeedXml = lambda: None
        fake.createNavJson = lambda: None
        fake.repo = SimpleNamespace(get_issue=lambda n: object())
        return fake, rendered

    @staticmethod
    def _install(fake, number, post):
        def add(issue):
            fake.blogBase["postListJson"]["P" + str(number)] = post
            return post
        fake.addOnePostJson = add

    def test_new_post_rerenders_previous_newest(self):
        fake, rendered = self._fake({"P1": mk_post(1, 100), "P2": mk_post(2, 200)})
        self._install(fake, 3, mk_post(3, 300))
        GMEEK.runOne(fake, "3")
        # 新文章本身 + 旧最新(P2) 必须重渲染; P1 不受影响
        assert set(rendered) == {"3", "2"}

    def test_reorder_rerenders_old_neighbors_too(self):
        fake, rendered = self._fake({"P1": mk_post(1, 100), "P2": mk_post(2, 200), "P3": mk_post(3, 300)})
        # 编辑 P2 使其 createdAt 变为最新 -> 导航序变为 P1,P3,P2, 旧邻 P1 也需刷新
        self._install(fake, 2, mk_post(2, 400))
        GMEEK.runOne(fake, "2")
        assert set(rendered) == {"1", "2", "3"}

    def test_first_post_has_no_neighbors(self):
        fake, rendered = self._fake({})
        self._install(fake, 1, mk_post(1, 100))
        GMEEK.runOne(fake, "1")
        assert rendered == ["1"]


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


class TestDeterministicColor:
    def test_stable_for_same_seed(self):
        assert deterministic_color("7") == deterministic_color("7")

    def test_varies_across_seeds(self):
        colors = {deterministic_color(str(i)) for i in range(1, 20)}
        assert len(colors) > 1

    def test_hsl_ranges(self):
        for i in range(1, 40):
            m = re.fullmatch(r"hsl\((\d+), (\d+)%, (\d+)%\)", deterministic_color(str(i)))
            assert m
            hue, sat, light = (int(x) for x in m.groups())
            assert 0 <= hue < 360
            assert 30 <= sat <= 70
            assert 10 <= light <= 40


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


class TestCreatePostHtmlNav:
    @staticmethod
    def _fake(blog_base):
        fake = SimpleNamespace()
        fake.blogBase = blog_base
        fake.options = SimpleNamespace(repo_name="x/y")
        fake.get_nav_keys = lambda: nav_order(blog_base["postListJson"])
        captured = {}
        fake.renderHtml = lambda template, postBase, postListJson, htmlDir: captured.update(postBase)
        return fake, captured

    @staticmethod
    def _post(tmp_path, number):
        md = tmp_path / ("%d.md" % number)
        md.write_text("body", encoding="utf-8")
        (tmp_path / ("%d.md.html" % number)).write_text("<p>body</p>", encoding="utf-8")
        return {"number": str(number), "markdown": str(md), "postTitle": "T%d" % number,
                "labels": [], "commentNum": 0, "style": "", "script": "", "top": 0,
                "postSourceUrl": "u", "description": "", "createdAt": 100 * number, "updatedAt": 100 * number,
                "htmlDir": "docs/post/%d.html" % number}

    @staticmethod
    def _base():
        return {"homeUrl": "https://example.com/blog",
                "postListJson": {"P1": mk_post(1, 100), "P2": mk_post(2, 200), "P3": mk_post(3, 300)}}

    def test_middle_wires_both_neighbors(self, tmp_path):
        fake, captured = self._fake(self._base())
        GMEEK.createPostHtml(fake, self._post(tmp_path, 2))
        assert captured["prevTitle"] == "T1"
        assert captured["nextTitle"] == "T3"
        assert captured["prevUrl"] == "https://example.com/blog/post/1.html"
        assert captured["nextUrl"] == "https://example.com/blog/post/3.html"

    def test_oldest_clears_prev_fields(self, tmp_path):
        # 负向控制: 旧状态文件可能带入的残留 prev 字段必须被清除
        base = self._base()
        base["prevUrl"] = "stale"
        base["prevTitle"] = "stale"
        fake, captured = self._fake(base)
        GMEEK.createPostHtml(fake, self._post(tmp_path, 1))
        assert "prevUrl" not in captured and "prevTitle" not in captured
        assert captured["nextTitle"] == "T2"

    def test_newest_clears_next_fields(self, tmp_path):
        fake, captured = self._fake(self._base())
        GMEEK.createPostHtml(fake, self._post(tmp_path, 3))
        assert "nextUrl" not in captured and "nextTitle" not in captured
        assert captured["prevTitle"] == "T2"


class TestTemplateSmoke:
    @staticmethod
    def _render(template, blog_base):
        env = Environment(loader=FileSystemLoader("templates"))
        return env.get_template(template).render(blogBase=blog_base, postListJson={}, i18n=i18nCN, IconList=IconList)

    @staticmethod
    def _post_base(**overrides):
        base = {
            "title": "T", "homeUrl": "https://example.com/blog", "nightTheme": "dark", "dayTheme": "light",
            "faviconUrl": "", "GMEEK_VERSION": "v2.4", "issuesUrl": "https://github.com/x/y/issues",
            "postTitle": "标题", "labels": [], "labelColorDict": {}, "commentNum": 0, "style": "", "script": "",
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
        html = self._render("post.html", self._post_base(labels=["C++"], labelColorDict={"C++": "#123456"}))
        assert "tag.html#C%2B%2B" in html

    def test_post_nav_exposes_runtime_hooks(self):
        html = self._render("post.html", self._post_base(postNumber="166"))
        assert 'data-nav-url="https://example.com/blog/nav.json"' in html
        assert 'data-post-number="166"' in html
        assert "assets/nav.js" in html

    def test_plist_single_page_link_uses_home_url(self):
        base = {
            "title": "T", "homeUrl": "https://example.com/blog", "nightTheme": "dark", "dayTheme": "light",
            "faviconUrl": "", "GMEEK_VERSION": "v2.4", "avatarUrl": "https://example.com/a.png",
            "displayTitle": "T", "subTitle": "s", "issuesUrl": "https://github.com/x/y/issues",
            "singeListJson": {"S1": {"label": "about", "postTitle": "About"}},
            "labelColorDict": {}, "commentLabelColor": "#006b75",
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
            "postListJson": {"P2": mk_post(2, 200), "P1": mk_post(1, 100)},
        }
        GMEEK.createNavJson(fake)
        data = json.loads((tmp_path / "nav.json").read_text(encoding="utf-8"))
        # 按 createdAt 升序, 与 nav_order 一致
        assert [p["number"] for p in data] == ["1", "2"]
        assert data[0]["title"] == "T1"
        assert data[0]["url"] == "https://example.com/blog/post/1.html"

    def test_empty_posts(self, tmp_path):
        fake = SimpleNamespace()
        fake.root_dir = str(tmp_path) + os.sep
        fake.blogBase = {"homeUrl": "https://example.com/blog", "postListJson": {}}
        GMEEK.createNavJson(fake)
        assert json.loads((tmp_path / "nav.json").read_text(encoding="utf-8")) == []


class TestTagData:
    def test_projects_only_needed_fields(self):
        full = {"labels": ["Life"], "postUrl": "post/1.html", "postTitle": "T1",
                "dateLabelColor": "hsl(1, 30%, 10%)", "createdDate": "2023-09-08",
                "description": "长摘要" * 100, "style": "", "script": "", "markdown": "m.md", "buildedAt": 1}
        out = tag_data({"P1": full})
        assert set(out["P1"].keys()) == {"labels", "postUrl", "postTitle", "dateLabelColor", "createdDate"}

    def test_empty_input(self):
        assert tag_data({}) == {}


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
        assert out == ('<span class="cl"><span class="s">"a</span></span>\n'
                       '<span class="cl"><span class="s">b"</span></span>')

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


class TestDefaultConfig:
    @staticmethod
    def _fake():
        return SimpleNamespace(repo=SimpleNamespace(full_name="x/y"), labelColorDict={})

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
