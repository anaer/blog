# -*- coding: utf-8 -*-
import os
import re
import json
import time
import calendar
import hashlib
import shutil
import urllib
import requests
import argparse
from datetime import datetime, timedelta, timezone
from github import Github, Auth, GithubException
from feedgen.feed import FeedGenerator
from jinja2 import Environment, FileSystemLoader
from bs4 import BeautifulSoup
from Summary import generate_summary, summary_configured
from md2html import Markdown2GithubHtml
from icons import ICONS as IconList, VIEWBOX as IconViewBox, STROKE_WIDTH as IconStrokeWidth

######################################################################################
i18n={"Search":"Search","switchTheme":"switch theme","link":"link","home":"home","comments":"comments","run":"run ","days":" days","Previous":"Previous","Next":"Next", "First": "First", "Last": "Last"}
i18nCN={"Search":"搜索","switchTheme":"切换主题","link":"友情链接","home":"首页","comments":"评论","run":"网站运行","days":"天","Previous":"上一页","Next":"下一页", "First": "首页", "Last":"末页"}

# 渲染器版本: 渲染逻辑变更时递增, 使全站帖子 HTML 缓存失效并重转
RENDER_VERSION = 13

# 摘要补重试的每构建上限, 防 API 故障时超时叠加拖死构建
MAX_DESC_RETRY = 10

def should_include_issue(issue, owner_name):
    """仅收录仓库主创建、且非 PR 的 issue。"""
    return issue.pull_request is None and issue.user is not None and issue.user.name == owner_name

def resolve_top(state, events):
    """置顶状态: 1=置顶 0=普通 -1=已关闭; 按最新一条 pin/unpin 事件判定。"""
    if state == "closed":
        return -1
    pin_events = [e for e in events if e.event in ("pinned", "unpinned")]
    if not pin_events:
        return 0
    latest = max(pin_events, key=lambda e: e.created_at)
    return 1 if latest.event == "pinned" else 0

def carry_cache(post, old_entry):
    """更新时间未变时携带摘要与构建缓存, 避免重复转换与摘要调用。"""
    if not old_entry or old_entry.get("updatedAt") != post["updatedAt"]:
        return post
    for key in ("description", "buildedAt", "renderVersion"):
        if key in old_entry:
            post[key] = old_entry[key]
    return post

def is_html_stale(md_file_exists, post):
    """帖子 HTML 缓存是否失效: 文件缺失 / 内容更新 / 渲染器版本变更。"""
    return (not md_file_exists) or post.get("buildedAt") != post["updatedAt"] or post.get("renderVersion") != RENDER_VERSION

def resolve_regen_mode(html_stale, description, api_configured, retry_budget):
    """决定重建方式: rebuild=重转HTML(顺带补摘要) summary=仅补空摘要 None=复用缓存。"""
    if html_stale:
        return "rebuild"
    if (not description) and api_configured and retry_budget > 0:
        return "summary"
    return None

def resolve_run_mode(issue_number, prune=False):
    """命令行路由归一化: prune=对账, 缺省/0=全量重建, 其余=单篇增量。

    关键: --issue_number 的 argparse 缺省是【整数】0, 而命令行传入是【字符串】;
    若直接与 "0" 比较, 手动触发(不传该参数)会因 0 != "0" 被误判为单篇 runOne(0),
    进而 get_issue(0) 报 404。此处统一 str 归一化, 覆盖 int/str/空白。
    """
    if prune:
        return "prune"
    if str(issue_number).strip() in ("", "0"):
        return "all"
    return "one"

def slim_state(blogBase):
    """落盘只保留内容索引, 不落展示态。"""
    return {"postListJson": blogBase["postListJson"], "singeListJson": blogBase["singeListJson"]}

def migrate_state(blogBase):
    """一次性迁移老状态文件: 把派生字段就地补全, 让历史条目与新帖走同一条消费路径。

    背景: blogBase.json 由历史 build 累积; 后续新增的「派生字段」(dateLabelHue、createdDate 等)
    在被加上之前的 build 不会有, 加载后直接消费会 KeyError 或 Jinja Undefined 渲染成空、
    视觉退化。处理模式: 派生字段必须能从 baseline 字段(number/createdAt)确定性重算,
    这种就在迁移步骤里就地补, 不依赖散落的 .get() 防御。

    后续若新增其它「可派生字段」, 在 field_migrations 字典里加一项即可, 单点扩展。
    """
    field_migrations = {
        # 日期标签色相: 由帖子号确定性派生, 与 addOnePostJson 一致
        "dateLabelHue": lambda post: deterministic_hue(post.get("number", "0")),
        # 日期字符串: 由 createdAt 派生, 与 addOnePostJson 一致
        "createdDate": lambda post: format_date_utc8(post.get("createdAt", 0)),
    }
    for list_name in ("postListJson", "singeListJson"):
        bucket = blogBase.get(list_name)
        if not isinstance(bucket, dict):
            continue
        for num, post in bucket.items():
            if not isinstance(post, dict):
                continue
            for key, derive in field_migrations.items():
                if key not in post:
                    post[key] = derive(post)


def tag_data(postListJson):
    """tag 页内联数据投影: 仅保留客户端筛选与展示所需字段。
    字段缺失时走兜底: 老状态文件(blogBase.json)可能包含在本特性加入前已存的帖子, 缺少 dateLabelHue 等;
    其余四字段(labels/postUrl/postTitle/createdDate)同样按需兜底, 不让单条缺失导致整页构建崩溃。"""
    fields = ("labels", "postUrl", "postTitle", "dateLabelHue", "createdDate")
    defaults = {"labels": [], "postUrl": "", "postTitle": "", "dateLabelHue": 210, "createdDate": ""}
    return {num: {k: post.get(k, defaults[k]) for k in fields} for num, post in postListJson.items()}

def search_settings(i18n_name, home_url=None):
    """检索相关派生配置: 站点语言标记, 以及结果链接前缀。

    索引内的链接是站点根相对路径, 站点托管在子路径时需按 homeUrl 补全;
    未配置 homeUrl 时退回根路径。
    """
    return {
        "lang": "zh-CN" if i18n_name == "CN" else "en",
        "searchBaseUrl": str(home_url or "").rstrip("/") + "/",
    }

# 展示用固定时区: UTC+8
TZ8 = timezone(timedelta(hours=8))

def list_order(postListJson):
    """列表顺序: 置顶优先, 再按更新时间降序, 同刻按编号兜底(已关闭 top=-1 排最后)。

    列表页、文章页导航(nav.json 与静态兜底)、runAll 预排共用此序列, 三处不得各写一套。
    """
    return dict(sorted(postListJson.items(),
                       key=lambda x: (x[1]["top"], x[1]["updatedAt"], int(x[1]["number"])),
                       reverse=True))

def nav_order(postListJson):
    """导航序列: 与列表页同序, 使文章页的上一篇/下一篇与列表中的上下相邻一致。"""
    return list(list_order(postListJson))

def nav_neighbors(nav_keys, postListJson, number):
    """按导航序列取相邻文章: (上一篇=列表中的上一条, 下一篇=下一条), 端点返回 None。"""
    postNum = "P" + str(number)
    if postNum not in nav_keys:
        return None, None
    index = nav_keys.index(postNum)
    prev_key = nav_keys[index - 1] if index > 0 else None
    next_key = nav_keys[index + 1] if index < len(nav_keys) - 1 else None
    return (postListJson[prev_key] if prev_key else None, postListJson[next_key] if next_key else None)

def neighbor_keys(old_keys, new_keys, target):
    """变更文章在旧/新导航序中的相邻项(去重、排除自身、保持先后)。"""
    result = []
    for keys in (old_keys, new_keys):
        if target in keys:
            index = keys.index(target)
            for j in (index - 1, index + 1):
                if 0 <= j < len(keys) and keys[j] != target and keys[j] not in result:
                    result.append(keys[j])
    return result

def format_datetime_utc8(epoch):
    return datetime.fromtimestamp(epoch, tz=TZ8).strftime("%Y-%m-%d %H:%M:%S")

def format_date_utc8(epoch):
    return datetime.fromtimestamp(epoch, tz=TZ8).strftime("%Y-%m-%d")

def deterministic_hue(seed):
    """按种子确定性派生色相(0-359), 供标签与日期标签配色使用。"""
    digest = hashlib.md5(str(seed).encode("utf-8")).digest()
    return int.from_bytes(digest[0:2], "big") % 360

def hex_to_hue(value):
    """十六进制颜色 → HSL 色相(0-359); 无法解析时返回 None。"""
    h = str(value).strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        return None
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    mx, mn = max(r, g, b), min(r, g, b)
    if mx == mn:
        return 0
    d = mx - mn
    if mx == r:
        hue = ((g - b) / d) % 6
    elif mx == g:
        hue = (b - r) / d + 2
    else:
        hue = (r - g) / d + 4
    return round(hue * 60) % 360

def label_hue(name, color=None, mode="derived"):
    """标签色相来源: derived 按名称派生; github 取 GitHub 标签色的色相(无法解析则回退派生)。"""
    if mode == "github" and color:
        hue = hex_to_hue(color)
        if hue is not None:
            return hue
    return deterministic_hue(name)

def resolve_label_color_mode(value):
    """标签色相来源归一化: 仅 "github" 走 GitHub 标签色, 其余(缺省/非法)一律名称派生。"""
    return "github" if value == "github" else "derived"

def replace_issue_refs(content, resolve):
    """替换正文中的 #数字 引用(跳过围栏代码块与行内代码); resolve 返回 None 时保持原样。"""
    in_fence = False
    out_lines = []
    for line in content.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            out_lines.append(line)
            continue
        if in_fence:
            out_lines.append(line)
            continue
        parts = line.split("`")
        for i in range(0, len(parts), 2):
            parts[i] = re.sub(r"#(\d+)", lambda m: resolve(m.group(1)) or m.group(0), parts[i])
        out_lines.append("`".join(parts))
    return "\n".join(out_lines)

######################################################################################
class GMEEK():
    def __init__(self,options):
        self.options=options

        self.root_dir='docs/'
        self.post_folder='post/'
        self.post_dir=self.root_dir+self.post_folder

        self.backup_dir='backup/'

        # 获取Github仓库信息
        user = Github(auth=Auth.Token(self.options.github_token))
        self.repo = user.get_repo(self.options.repo_name)

        # 全量构建的重建快照(None=增量)与摘要补重试预算
        self.rebuild_cache = None
        self.desc_retry_budget = MAX_DESC_RETRY
        self._nav_keys = None

        # 占位默认值, 供 defaultConfig 引用; 具体值在 defaultConfig 之后按 GitHub 标签重算后覆盖
        self.labelHueDict = {}

        self.defaultConfig()

        # 标签色相来源由 labelColorMode 决定: derived=按名称派生(默认), github=取 GitHub 标签色的色相。
        # 两种模式共用同一套主题自适应渲染, 故都兼容明暗
        mode = resolve_label_color_mode(self.blogBase.get("labelColorMode"))
        self.labelHueDict = {
            label.name: label_hue(label.name, label.color, mode)
            for label in self.repo.get_labels()
        }
        # 同步回 blogBase: 模板(plist/post/tag)读取 blogBase['labelHueDict'];
        # defaultConfig 早些时候已拿占位空 dict 写过一次, 这里用真值覆盖, 否则模板全回退到默认色相
        self.blogBase["labelHueDict"] = self.labelHueDict

    def defaultConfig(self):
        '''
        初始化配置, 主要用于runAll
        runOne 因为有重新赋值, 没用到
        '''
        # 内置默认值始终参与合并(状态文件瘦身后不再携带这些键)
        defaults={"startSite":"","filingNum":"","onePageListNum":15,"commentLabelColor":"#006b75","i18n":"CN","dayTheme":"light","nightTheme":"dark","labelColorMode":"derived"}
        if os.path.exists("blogBase.json"):
            with open('blogBase.json', 'r', encoding='utf-8') as f:
                dconfig = json.loads(f.read())
        else:
            dconfig = {}

        if os.path.exists("config.json"):
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.loads(f.read())
        else:
            config = {}

        self.blogBase={**defaults,**dconfig,**config}.copy()

        if "postListJson" not in self.blogBase:
            self.blogBase["postListJson"] = {}
        if "singeListJson" not in self.blogBase:
            self.blogBase["singeListJson"] = {}

        # 派生字段迁移: 老状态文件可能缺日期/日期色相等; 在此就地补, 一次构建后落盘,
        # 后续消费者(plist/tag_data/...)就能统一消费, 不再依赖散落 .get() 兜底
        migrate_state(self.blogBase)

        self.i18n=i18nCN if self.blogBase["i18n"]=="CN" else i18n
        self.blogBase["labelHueDict"]=self.labelHueDict
        self.blogBase["issuesUrl"]="https://github.com/"+self.repo.full_name+"/issues"
        self.blogBase.update(search_settings(self.blogBase["i18n"], self.blogBase.get("homeUrl")))

    def cleanFile(self):
        if os.path.exists(self.root_dir):
            shutil.rmtree(self.root_dir)

        os.mkdir(self.root_dir)
        os.mkdir(self.post_dir)
        if not os.path.exists(self.backup_dir):
            os.mkdir(self.backup_dir)

    def checkDir(self):
        # 检查目录是否存在, 如不存在则创建
        if not os.path.exists(self.backup_dir):
             os.mkdir(self.backup_dir)

        if not os.path.exists(self.root_dir):
            os.mkdir(self.root_dir)

        if not os.path.exists(self.post_dir):
            os.mkdir(self.post_dir)

    def markdown2html(self, mdstr, retries=3):
        """
        调用github api将markdown文本转为html格式代码, 请求失败时 重试3次
        """
        payload = {"text": mdstr, "mode": "markdown"}
        headers = {"Authorization": "token {}".format(self.options.github_token)}
        for attempt in range(retries):
            try:
                ret = requests.post("https://api.github.com/markdown", json=payload, headers=headers, timeout=10)
                if ret.status_code == 200:
                    return ret.text
                else:
                    print(f"Attempt {attempt + 1} failed with status code {ret.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt < retries - 1:
                time.sleep(1)  # Wait for 1 second before retrying
        raise Exception("markdown2html error after {} retries, status_code={}".format(retries, ret.status_code))

    def renderHtml(self,template,blogBase,postListJson,htmlDir):
        """
        渲染模版 生成html页面
        """
        file_loader = FileSystemLoader('templates')
        env = Environment(loader=file_loader)
        template = env.get_template(template)
        output = template.render(blogBase=blogBase,postListJson=postListJson,i18n=self.i18n,IconList=IconList,IconViewBox=IconViewBox,IconStrokeWidth=IconStrokeWidth)
        with open(htmlDir, 'w', encoding='UTF-8') as f:
            f.write(output)

    def createPostHtml(self, post):
        with open(post["markdown"]+".html", 'r', encoding='UTF-8') as f:
            post_body=f.read()

        postBase=self.blogBase.copy()
        postBase["postTitle"]=post["postTitle"]
        postBase["postNumber"]=post["number"]
        postBase["labels"]=post["labels"]
        postBase["commentNum"]=post["commentNum"]
        postBase["style"]=post["style"]
        postBase["script"]=post["script"]
        postBase["top"]=post["top"]
        postBase["postSourceUrl"]=post["postSourceUrl"]
        postBase["repoName"]=self.options.repo_name
        postBase["description"]=post["description"] if "description" in post else ""
        postBase["postBody"]=post_body
        postBase["createdAt"] = format_datetime_utc8(post["createdAt"])
        postBase["updatedAt"] = format_datetime_utc8(post["updatedAt"])

        for key in ("prevUrl", "prevTitle", "nextUrl", "nextTitle"):
            postBase.pop(key, None)

        prevPost, nextPost = nav_neighbors(self.get_nav_keys(), self.blogBase["postListJson"], post["number"])
        if prevPost:
            postBase["prevUrl"]=self.blogBase["homeUrl"] + "/" + prevPost["postUrl"]
            postBase["prevTitle"]=prevPost["postTitle"]

        if nextPost:
            postBase["nextUrl"]=self.blogBase["homeUrl"] + "/" + nextPost["postUrl"]
            postBase["nextTitle"]=nextPost["postTitle"]

        self.renderHtml('post.html',postBase,{},post["htmlDir"])

    def createPlistHtml(self):
        """
        生成列表页面
        """
        # 排序规则见 list_order: 置顶优先, 再按更新时间降序
        self.blogBase["postListJson"]=list_order(self.blogBase["postListJson"])

        postNum = len(self.blogBase["postListJson"])
        totalPages = (postNum + self.blogBase["onePageListNum"] - 1) // self.blogBase["onePageListNum"]
        pageFlag = 0
        while postNum > 0:
            topNum = pageFlag * self.blogBase["onePageListNum"]
            onePageList = dict(list(self.blogBase["postListJson"].items())[topNum:topNum + self.blogBase["onePageListNum"]])
            htmlDir = self.root_dir + ("index.html" if pageFlag == 0 else f"page{pageFlag + 1}.html")

            if pageFlag == 0:
                self.blogBase["prevUrl"] = "disabled"
                self.blogBase["nextUrl"] = self.blogBase["homeUrl"] + "/page2.html" if postNum > self.blogBase["onePageListNum"] else "disabled"
            else:
                self.blogBase["prevUrl"] = self.blogBase["homeUrl"] + ("/index.html" if pageFlag == 1 else f"/page{pageFlag}.html")
                self.blogBase["nextUrl"] = self.blogBase["homeUrl"] + f"/page{pageFlag + 2}.html" if postNum > self.blogBase["onePageListNum"] else "disabled"

            self.blogBase["firstUrl"] = self.blogBase["homeUrl"] + "/index.html" if pageFlag != 0 else "disabled"
            self.blogBase["lastUrl"] = self.blogBase["homeUrl"] + f"/page{totalPages}.html" if pageFlag != totalPages - 1 else "disabled"

            self.renderHtml('plist.html', self.blogBase, onePageList, htmlDir)
            print(f"create {htmlDir}")

            postNum -= self.blogBase["onePageListNum"]
            pageFlag += 1

        # 生成标签页面(内联数据只保留客户端所需字段)
        self.blogBase["tagListJson"] = tag_data(self.blogBase["postListJson"])
        self.renderHtml('tag.html',self.blogBase,onePageList,self.root_dir+"tag.html")
        print("create tag.html")

    def createFeedXml(self):
        """
        生成rss文件
        """
        # 按照创建时间排序
        self.blogBase["postListJson"]=dict(sorted(self.blogBase["postListJson"].items(),key=lambda x:x[1]["createdAt"],reverse=False))

        feed = FeedGenerator()
        feed.title(self.blogBase["title"])
        feed.description(self.blogBase["subTitle"])
        feed.link(href=self.blogBase["homeUrl"])
        feed.image(url=self.blogBase["avatarUrl"],title="avatar", link=self.blogBase["homeUrl"])
        feed.pubDate(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))
        feed.copyright(self.blogBase["title"])
        feed.managingEditor(self.blogBase["title"])
        feed.webMaster(self.blogBase["title"])
        feed.ttl("60")

        for listJsonName in ["singeListJson", "postListJson"]:
            for num in self.blogBase[listJsonName]:
                item=feed.add_item()
                item.guid(self.blogBase["homeUrl"]+"/"+self.blogBase[listJsonName][num]["postUrl"],permalink=True)
                item.title(self.blogBase[listJsonName][num]["postTitle"])
                item.description(self.blogBase[listJsonName][num]["description"])
                item.link(href=self.blogBase["homeUrl"]+"/"+self.blogBase[listJsonName][num]["postUrl"])
                item.pubDate(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(self.blogBase[listJsonName][num]["createdAt"])))

        feed.rss_file(self.root_dir+'rss.xml')

    def createNavJson(self):
        """生成全站导航数据(按导航序), 供文章页运行时计算上一页/下一页。"""
        nav = []
        for key in nav_order(self.blogBase["postListJson"]):
            post = self.blogBase["postListJson"][key]
            nav.append({
                "number": post["number"],
                "title": post["postTitle"],
                "url": self.blogBase["homeUrl"] + "/" + post["postUrl"],
            })
        with open(self.root_dir + "nav.json", "w", encoding="UTF-8") as f:
            f.write(json.dumps(nav, ensure_ascii=False))

    def createSearchHtml(self):
        """生成站内搜索页; 检索数据由构建期索引步骤产出, 页面本身不含数据。"""
        self.renderHtml('search.html',self.blogBase,{},self.root_dir+"search.html")
        print("create search.html")

    def build_desc(self, content):
        return generate_summary(content)

    def get_cached(self, postNum):
        """旧条目缓存: 全量构建用重建前快照, 增量构建用当前索引。"""
        if self.rebuild_cache is not None:
            return self.rebuild_cache.get(postNum)
        for listJsonName in ("postListJson", "singeListJson"):
            entry = self.blogBase[listJsonName].get(postNum)
            if entry:
                return entry
        return None

    def get_nav_keys(self):
        """导航序列(按时间升序), 一次渲染批次内只计算一次。"""
        if self._nav_keys is None:
            self._nav_keys = nav_order(self.blogBase["postListJson"])
        return self._nav_keys

    def normalize_title(self, title):
        """
        定义方法 规范标题, 替换文件名不支持的符号为_
        """
        return re.sub(r'[\\/*?:"<>|]', '_', title)

    def decimal_to_hex(self, decimal_value):
        if not isinstance(decimal_value, int) or decimal_value < 0:
            return decimal_value

        # 使用 Python 内置函数 hex 进行转换
        hex_value = hex(decimal_value)

        # 确保十六进制字母大写
        hex_value = hex_value.upper()

        return hex_value

    def addOnePostJson(self,issue):
        if not should_include_issue(issue, self.repo.owner.name):
            # 有需要可以设置白名单
            print("非仓库主创建或 PR 的 issue, 不进行生成")
            return

        # 因为当前没用单页, 暂不处理这块逻辑
        if len(issue.labels) == 1 and issue.labels[0].name in self.blogBase["singlePage"]:
            listJsonName='singeListJson'
            gen_Html = 'docs/{}.html'.format(issue.labels[0].name)
        else:
            listJsonName='postListJson'
            gen_Html = self.post_dir+'{}.html'.format(issue.number)

        mdPath = "backup/"+str(issue.number)+"-"+self.normalize_title(issue.title)+".md"

        labels = [label.name for label in issue.labels]

        postNum="P"+str(issue.number)
        post = {}
        post["number"]=str(issue.number)
        post["htmlDir"]=gen_Html
        post["markdown"]=mdPath
        post["labels"]=labels
        # post["postTitle"]="%s %s" % (self.decimal_to_hex(issue.number), issue.title)
        post["postTitle"]=issue.title # 评论需要根据标题搜索, 所以简单的就不修改标题了
        if listJsonName=='singeListJson':
            post["postUrl"]=urllib.parse.quote('{}.html'.format(issue.labels[0].name))
            # 单页专属标签名: 模板据此生成 href 与选取图标(见 plist.html)
            post["label"]=issue.labels[0].name
        else:
            post["postUrl"]=urllib.parse.quote(self.post_folder+'{}.html'.format(issue.number))
        post["postSourceUrl"]="https://github.com/"+self.options.repo_name+"/issues/"+str(issue.number)
        post["commentNum"]=issue.get_comments().totalCount
        post["createdAt"]=int(calendar.timegm(issue.created_at.utctimetuple()))
        post["updatedAt"]=int(calendar.timegm(issue.updated_at.utctimetuple()))

        # 如果issue为关闭状态, 显示在最后
        if issue.state=="closed":
            post["top"]=-1
        else:
            post["top"] = resolve_top(issue.state, issue.get_events())

        post["style"]=""
        post["script"]=""
        post["description"]=""
        # 读取postConfig: 约定正文最后一行以 ## 前缀跟 JSON(如 ##{"timestamp":...}); 无此约定则跳过
        postConfig={}
        last_line = issue.body.splitlines()[-1] if issue.body else ""
        if "##" in last_line:
            try:
                postConfig=json.loads(last_line.split("##", 1)[1])
                print("Has Custom JSON parameters")
                print(postConfig)
                if "timestamp" in postConfig:
                    post["createdAt"]=postConfig["timestamp"]

                if "style" in postConfig:
                    post["style"]=str(postConfig["style"])

                if "script" in postConfig:
                    post["script"]=str(postConfig["script"])
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error parsing post config: {e}")
                postConfig={}

        post["createdDate"]=format_date_utc8(post["createdAt"])
        post["dateLabelHue"]=deterministic_hue(post["number"])

        content = issue.body
        # 如果没有正文, 直接返回
        if not content:
            return
        # 处理正文中的#数字链接(跳过围栏代码块与行内代码)
        def resolve_ref(number_str):
            matchPostNum = "P"+str(number_str)
            # 全量重建时索引逐步填充, 目标尚未收录则不替换, 与最新数据可能有差异
            if matchPostNum in self.blogBase[listJsonName]:
                entry = self.blogBase[listJsonName][matchPostNum]
                return " ["+entry["postTitle"]+"]("+self.blogBase["homeUrl"]+"/"+entry["postUrl"]+") "
            return None

        content = replace_issue_refs(content, resolve_ref)

        with open(mdPath, 'w', encoding='UTF-8') as f:
            f.write(content)

        mdHtmlPath = mdPath + ".html"
        # 未变更的帖子携带旧摘要与构建缓存, 按需重建
        cached = self.get_cached(postNum)
        if cached:
            carry_cache(post, cached)

        api_configured = summary_configured()
        html_stale = is_html_stale(os.path.isfile(mdHtmlPath), post)
        mode = resolve_regen_mode(html_stale, post["description"], api_configured, self.desc_retry_budget)
        if mode:
            if mode == "rebuild":
                tool = Markdown2GithubHtml()
                mdHtml = tool.convert(content)
                with open(mdHtmlPath, 'w', encoding='UTF-8') as fp:
                    fp.write(mdHtml)
                post["buildedAt"] = post["updatedAt"]
                post["renderVersion"] = RENDER_VERSION

            if not post["description"] and api_configured:
                if mode == "summary":
                    # 仅为补历史空摘要的重试, 计入预算
                    self.desc_retry_budget -= 1
                with open(mdHtmlPath, 'r', encoding='UTF-8') as fp:
                    mdHtml = fp.read()
                soup = BeautifulSoup(mdHtml, "html.parser")
                post["description"] = self.build_desc(soup.get_text()) or ""

        self.blogBase[listJsonName][postNum] = post
        return post

    def runAll(self):
        print("====== start create static html ======")
        self.cleanFile()

        # 全量重建索引: 快照旧索引供缓存携带, 已删除/改判的条目随重建清除
        self.rebuild_cache = {**self.blogBase["postListJson"], **self.blogBase["singeListJson"]}
        self.blogBase["postListJson"] = {}
        self.blogBase["singeListJson"] = {}

        issues=self.repo.get_issues(state="all")
        issue_list = list(issues)
        print("issue count:%d"%(len(issue_list)))
        # 注意: 必须在 issue_list(已物化的列表)上迭代, 不得再迭代 issues 本身。
        # PyGithub 的 PaginatedList 被 list() 耗尽后再次迭代会产生 0 个元素,
        # 会导致全量重建一篇帖子都不生成、进而清空线上 post 目录。
        for issue in issue_list:
            try:
                self.addOnePostJson(issue)
            except Exception as e:
                print(f"skip issue #{getattr(issue, 'number', '?')}: {e}")

        # 与列表页同序(见 list_order), 便于 post 中获取上一篇和下一篇
        self.blogBase["postListJson"]=list_order(self.blogBase["postListJson"])

        for post in self.blogBase["postListJson"].values():
            self.createPostHtml(post)

        for post in self.blogBase["singeListJson"].values():
            self.createPostHtml(post)

        self.createPlistHtml()
        self.createFeedXml()
        self.createNavJson()
        self.createSearchHtml()
        print("====== create static html end ======")

    def runOne(self,number_str):
        print("====== start create static html ======")
        self.checkDir()

        # 变更前的导航序快照: 用于定位「旧相邻」文章
        old_keys = list(self.get_nav_keys())

        try:
            issue=self.repo.get_issue(int(number_str))
        except GithubException as e:
            # 404 表示 issue 已被删除: 清理残留索引并重渲染列表页, 不中断构建
            if getattr(e, "status", None) == 404:
                print(f"issue #{number_str} 不存在(可能已删除), 清理残留索引并重渲染列表")
                self.prune_one(number_str)
                self.createPlistHtml()
                self.createFeedXml()
                self.createNavJson()
                self.createSearchHtml()
                print("====== create static html end ======")
                return
            raise
        post = self.addOnePostJson(issue)
        if post:
            # 索引已更新, 导航序缓存失效需重算(必须在渲染前失效, 否则沿用旧序)
            self._nav_keys = None
            new_keys = self.get_nav_keys()
            self.createPostHtml(post)
            # 新增/编辑会改变导航序, 相邻文章的上一页/下一页需一并重渲染
            for key in neighbor_keys(old_keys, new_keys, "P"+str(post["number"])):
                neighbor = self.blogBase["postListJson"].get(key)
                if neighbor:
                    self.createPostHtml(neighbor)
            self.createPlistHtml()
            self.createFeedXml()
            self.createNavJson()
            self.createSearchHtml()
        print("====== create static html end ======")

    def runLatest(self):
        print("====== start create static html ======")
        self.checkDir()

        issues=self.repo.get_issues(state="open", sort="updated", direction="desc")
        for issue in issues:
            post = self.addOnePostJson(issue)
            if post:
                self.createPostHtml(post)
                self.createPlistHtml()
                self.createFeedXml()
                self.createNavJson()
                self.createSearchHtml()
            break
        print("====== create static html end ======")

    def prune_one(self, number_str):
        """移除单个 issue 的索引条目与 HTML(供 runOne 处理 404 删除事件)。"""
        postNum = "P" + str(number_str)
        for listJsonName in ("postListJson", "singeListJson"):
            entry = self.blogBase[listJsonName].pop(postNum, None)
            if entry:
                html_path = entry.get("htmlDir")
                if html_path and os.path.isfile(html_path):
                    try:
                        os.remove(html_path)
                    except OSError:
                        pass
        self._nav_keys = None

    def prune_stale(self):
        """对账索引与仓库实况: 删除索引中存在但仓库已不存在(被删)的条目及其 HTML; 返回被移除的文章编号列表。"""
        live = set()
        for issue in self.repo.get_issues(state="all"):
            if should_include_issue(issue, self.repo.owner.name):
                live.add(str(issue.number))
        removed = []
        for listJsonName in ("postListJson", "singeListJson"):
            for key in list(self.blogBase[listJsonName].keys()):
                num = key[1:]  # 单页与普通文章均用 'P' 前缀
                if num not in live:
                    entry = self.blogBase[listJsonName].pop(key)
                    html_path = entry.get("htmlDir")
                    if html_path and os.path.isfile(html_path):
                        try:
                            os.remove(html_path)
                        except OSError:
                            pass
                    removed.append(num)
        return removed

#########################################################################
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("github_token", help="github_token")
    parser.add_argument("repo_name", help="repo_name")
    parser.add_argument("--issue_number", help="issue_number", default=0, required=False)
    parser.add_argument("--prune", action="store_true", help="reconcile index with repo and drop deleted issues", default=False)
    options = parser.parse_args()

    blog=GMEEK(options)

    mode = resolve_run_mode(options.issue_number, options.prune)
    if mode == "prune":
        print("prune stale")
        blog.prune_stale()
        blog.createPlistHtml()
        blog.createFeedXml()
        blog.createNavJson()
        blog.createSearchHtml()
    elif mode == "all":
        print("runAll")
        blog.runAll()
    else:
        number_str = str(options.issue_number).strip()
        print(f"runOne {number_str}")
        blog.runOne(number_str)

    with open("blogBase.json","w",encoding='utf-8') as listFile:
        listFile.write(json.dumps(slim_state(blog.blogBase), indent=4))

if __name__ == "__main__":
    main()
#########################################################################
