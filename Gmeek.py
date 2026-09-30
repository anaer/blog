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
from github import Github
from feedgen.feed import FeedGenerator
from jinja2 import Environment, FileSystemLoader
from bs4 import BeautifulSoup
from Summary import generate_summary, summary_configured
from md2html import Markdown2GithubHtml

######################################################################################
i18n={"Search":"Search","switchTheme":"switch theme","link":"link","home":"home","comments":"comments","run":"run ","days":" days","Previous":"Previous","Next":"Next", "First": "First", "Last": "Last"}
i18nCN={"Search":"搜索","switchTheme":"切换主题","link":"友情链接","home":"首页","comments":"评论","run":"网站运行","days":"天","Previous":"上一页","Next":"下一页", "First": "首页", "Last":"末页"}
IconList={
    "post":"M0 3.75C0 2.784.784 2 1.75 2h12.5c.966 0 1.75.784 1.75 1.75v8.5A1.75 1.75 0 0 1 14.25 14H1.75A1.75 1.75 0 0 1 0 12.25Zm1.75-.25a.25.25 0 0 0-.25.25v8.5c0 .138.112.25.25.25h12.5a.25.25 0 0 0 .25-.25v-8.5a.25.25 0 0 0-.25-.25ZM3.5 6.25a.75.75 0 0 1 .75-.75h7a.75.75 0 0 1 0 1.5h-7a.75.75 0 0 1-.75-.75Zm.75 2.25h4a.75.75 0 0 1 0 1.5h-4a.75.75 0 0 1 0-1.5Z",
    "link":"m7.775 3.275 1.25-1.25a3.5 3.5 0 1 1 4.95 4.95l-2.5 2.5a3.5 3.5 0 0 1-4.95 0 .751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018 1.998 1.998 0 0 0 2.83 0l2.5-2.5a2.002 2.002 0 0 0-2.83-2.83l-1.25 1.25a.751.751 0 0 1-1.042-.018.751.751 0 0 1-.018-1.042Zm-4.69 9.64a1.998 1.998 0 0 0 2.83 0l1.25-1.25a.751.751 0 0 1 1.042.018.751.751 0 0 1 .018 1.042l-1.25 1.25a3.5 3.5 0 1 1-4.95-4.95l2.5-2.5a3.5 3.5 0 0 1 4.95 0 .751.751 0 0 1-.018 1.042.751.751 0 0 1-1.042.018 1.998 1.998 0 0 0-2.83 0l-2.5 2.5a1.998 1.998 0 0 0 0 2.83Z",
    "about":"M10.561 8.073a6.005 6.005 0 0 1 3.432 5.142.75.75 0 1 1-1.498.07 4.5 4.5 0 0 0-8.99 0 .75.75 0 0 1-1.498-.07 6.004 6.004 0 0 1 3.431-5.142 3.999 3.999 0 1 1 5.123 0ZM10.5 5a2.5 2.5 0 1 0-5 0 2.5 2.5 0 0 0 5 0Z",
    "sun":"M8 10.5a2.5 2.5 0 100-5 2.5 2.5 0 000 5zM8 12a4 4 0 100-8 4 4 0 000 8zM8 0a.75.75 0 01.75.75v1.5a.75.75 0 01-1.5 0V.75A.75.75 0 018 0zm0 13a.75.75 0 01.75.75v1.5a.75.75 0 01-1.5 0v-1.5A.75.75 0 018 13zM2.343 2.343a.75.75 0 011.061 0l1.06 1.061a.75.75 0 01-1.06 1.06l-1.06-1.06a.75.75 0 010-1.06zm9.193 9.193a.75.75 0 011.06 0l1.061 1.06a.75.75 0 01-1.06 1.061l-1.061-1.06a.75.75 0 010-1.061zM16 8a.75.75 0 01-.75.75h-1.5a.75.75 0 010-1.5h1.5A.75.75 0 0116 8zM3 8a.75.75 0 01-.75.75H.75a.75.75 0 010-1.5h1.5A.75.75 0 013 8zm10.657-5.657a.75.75 0 010 1.061l-1.061 1.06a.75.75 0 11-1.06-1.06l1.06-1.06a.75.75 0 011.06 0zm-9.193 9.193a.75.75 0 010 1.06l-1.06 1.061a.75.75 0 11-1.061-1.06l1.06-1.061a.75.75 0 011.061 0z",
    "moon":"M9.598 1.591a.75.75 0 01.785-.175 7 7 0 11-8.967 8.967.75.75 0 01.961-.96 5.5 5.5 0 007.046-7.046.75.75 0 01.175-.786zm1.616 1.945a7 7 0 01-7.678 7.678 5.5 5.5 0 107.678-7.678z",
    "search":"M15.7 13.3l-3.81-3.83A5.93 5.93 0 0 0 13 6c0-3.31-2.69-6-6-6S1 2.69 1 6s2.69 6 6 6c1.3 0 2.48-.41 3.47-1.11l3.83 3.81c.19.2.45.3.7.3.25 0 .52-.09.7-.3a.996.996 0 0 0 0-1.41v.01zM7 10.7c-2.59 0-4.7-2.11-4.7-4.7 0-2.59 2.11-4.7 4.7-4.7 2.59 0 4.7 2.11 4.7 4.7 0 2.59-2.11 4.7-4.7 4.7z",
    "rss":"M2.002 2.725a.75.75 0 0 1 .797-.699C8.79 2.42 13.58 7.21 13.974 13.201a.75.75 0 0 1-1.497.098 10.502 10.502 0 0 0-9.776-9.776.747.747 0 0 1-.7-.798ZM2.84 7.05h-.002a7.002 7.002 0 0 1 6.113 6.111.75.75 0 0 1-1.49.178 5.503 5.503 0 0 0-4.8-4.8.75.75 0 0 1 .179-1.489ZM2 13a1 1 0 1 1 2 0 1 1 0 0 1-2 0Z",
    "upload":"M2.75 14A1.75 1.75 0 0 1 1 12.25v-2.5a.75.75 0 0 1 1.5 0v2.5c0 .138.112.25.25.25h10.5a.25.25 0 0 0 .25-.25v-2.5a.75.75 0 0 1 1.5 0v2.5A1.75 1.75 0 0 1 13.25 14Z M11.78 4.72a.749.749 0 1 1-1.06 1.06L8.75 3.811V9.5a.75.75 0 0 1-1.5 0V3.811L5.28 5.78a.749.749 0 1 1-1.06-1.06l3.25-3.25a.749.749 0 0 1 1.06 0l3.25 3.25Z",
    "github":"M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z",
    "home":"M6.906.664a1.749 1.749 0 0 1 2.187 0l5.25 4.2c.415.332.657.835.657 1.367v7.019A1.75 1.75 0 0 1 13.25 15h-3.5a.75.75 0 0 1-.75-.75V9H7v5.25a.75.75 0 0 1-.75.75h-3.5A1.75 1.75 0 0 1 1 13.25V6.23c0-.531.242-1.034.657-1.366l5.25-4.2Zm1.25 1.171a.25.25 0 0 0-.312 0l-5.25 4.2a.25.25 0 0 0-.094.196v7.019c0 .138.112.25.25.25H5.5V8.25a.75.75 0 0 1 .75-.75h3.5a.75.75 0 0 1 .75.75v5.25h2.75a.25.25 0 0 0 .25-.25V6.23a.25.25 0 0 0-.094-.195Z",
    "subway":"M7.01 9h10v5h-10zM17.8 2.8C16 2.09 13.86 2 12 2c-1.86 0-4 .09-5.8.8C3.53 3.84 2 6.05 2 8.86V22h20V8.86c0-2.81-1.53-5.02-4.2-6.06zm.2 13.08c0 1.45-1.18 2.62-2.63 2.62l1.13 1.12V20H15l-1.5-1.5h-2.83L9.17 20H7.5v-.38l1.12-1.12C7.18 18.5 6 17.32 6 15.88V9c0-2.63 3-3 6-3 3.32 0 6 .38 6 3v6.88z"
}

# starry-night支持的样式
starryNightStyles = ["both", "colorblind-dark", "colorblind-light", "colorblind", "dark", "dimmed-dark", "dimmed", "high-contrast-dark", "high-contrast-light", "high-contrast", "light", "tritanopia-dark", "tritanopia-light", "tritanopia"]

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
    for key in ("description", "buildedAt"):
        if key in old_entry:
            post[key] = old_entry[key]
    return post


def resolve_regen_mode(html_stale, description, api_configured, retry_budget):
    """决定重建方式: rebuild=重转HTML(顺带补摘要) summary=仅补空摘要 None=复用缓存。"""
    if html_stale:
        return "rebuild"
    if (not description) and api_configured and retry_budget > 0:
        return "summary"
    return None


def slim_state(blogBase):
    """落盘只保留内容索引, 不落展示态。"""
    return {"postListJson": blogBase["postListJson"], "singeListJson": blogBase["singeListJson"]}


def tag_data(postListJson):
    """tag 页内联数据投影: 仅保留客户端筛选与展示所需字段。"""
    fields = ("labels", "postUrl", "postTitle", "dateLabelColor", "createdDate")
    return {num: {k: post[k] for k in fields} for num, post in postListJson.items()}


# 展示用固定时区: UTC+8
TZ8 = timezone(timedelta(hours=8))


def nav_order(postListJson):
    """导航序列: 全部文章按 (createdAt, number) 升序, 不受置顶/关闭影响。"""
    return sorted(postListJson, key=lambda k: (postListJson[k]["createdAt"], int(postListJson[k]["number"])))


def nav_neighbors(nav_keys, postListJson, number):
    """按导航序列取相邻文章: (上一篇=更早, 下一篇=更晚), 端点返回 None。"""
    postNum = "P" + str(number)
    if postNum not in nav_keys:
        return None, None
    index = nav_keys.index(postNum)
    prev_key = nav_keys[index - 1] if index > 0 else None
    next_key = nav_keys[index + 1] if index < len(nav_keys) - 1 else None
    return (postListJson[prev_key] if prev_key else None, postListJson[next_key] if next_key else None)


def format_datetime_utc8(epoch):
    return datetime.fromtimestamp(epoch, tz=TZ8).strftime("%Y-%m-%d %H:%M:%S")


def format_date_utc8(epoch):
    return datetime.fromtimestamp(epoch, tz=TZ8).strftime("%Y-%m-%d")


def deterministic_color(seed):
    """按种子确定性派生日期标签颜色, hsl 区间与历史一致。"""
    digest = hashlib.md5(str(seed).encode("utf-8")).digest()
    hue = int.from_bytes(digest[0:2], "big") % 360
    saturation = 30 + int.from_bytes(digest[2:4], "big") % 41
    lightness = 10 + int.from_bytes(digest[4:6], "big") % 31
    return f"hsl({hue}, {saturation}%, {lightness}%)"


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
        user = Github(self.options.github_token)
        self.repo = user.get_repo(self.options.repo_name)

        # 读取仓库的labels标签颜色
        self.labelColorDict = {}
        for label in self.repo.get_labels():
            self.labelColorDict[label.name]='#'+label.color

        # 全量构建的重建快照(None=增量)与摘要补重试预算
        self.rebuild_cache = None
        self.desc_retry_budget = MAX_DESC_RETRY
        self._nav_keys = None

        self.defaultConfig()

    def defaultConfig(self):
        '''
        初始化配置, 主要用于runAll
        runOne 因为有重新赋值, 没用到
        '''
        if os.path.exists("blogBase.json"):
            with open('blogBase.json', 'r', encoding='utf-8') as f:
                dconfig = json.loads(f.read())
        else:
            dconfig={"startSite":"","filingNum":"","onePageListNum":15,"commentLabelColor":"#006b75","i18n":"CN","dayTheme":"light","nightTheme":"dark"}

        if os.path.exists("config.json"):
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.loads(f.read())
        else:
            config = {}

        self.blogBase={**dconfig,**config}.copy()

        if "postListJson" not in self.blogBase:
            self.blogBase["postListJson"] = {}
        if "singeListJson" not in self.blogBase:
            self.blogBase["singeListJson"] = {}

        self.i18n=i18nCN if self.blogBase["i18n"]=="CN" else i18n
        self.blogBase["labelColorDict"]=self.labelColorDict
        self.blogBase["issuesUrl"]="https://github.com/"+self.repo.full_name+"/issues"

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
        output = template.render(blogBase=blogBase,postListJson=postListJson,i18n=self.i18n,IconList=IconList)
        with open(htmlDir, 'w', encoding='UTF-8') as f:
            f.write(output)

    def createPostHtml(self, post):
        with open(post["markdown"]+".html", 'r', encoding='UTF-8') as f:
            post_body=f.read()

        postBase=self.blogBase.copy()
        postBase["postTitle"]=post["postTitle"]
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

        if 'class="highlight"' in post_body:
            postBase["highlight"]=1
            index = int(post["number"]) % len(starryNightStyles)
            postBase["starryNight"] = starryNightStyles[index]
        else:
            postBase["highlight"]=0

        self.renderHtml('post.html',postBase,{},post["htmlDir"])

    def createPlistHtml(self):
        """
        生成列表页面
        """
        # 排序规则: 1-是否置顶 2: 按更新时间降序
        self.blogBase["postListJson"]=dict(sorted(self.blogBase["postListJson"].items(),key=lambda x:(x[1]["top"],x[1]["updatedAt"]),reverse=True))

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
        # 读取postConfig配置, 暂时没有这块 先不处理
        try:
            postConfig=json.loads(issue.body.split("\r\n")[-1:][0].split("##")[1])
            print("Has Custom JSON parameters")
            print(postConfig)
            if "timestamp" in postConfig:
                post["createdAt"]=postConfig["timestamp"]

            if "style" in postConfig:
                post["style"]=str(postConfig["style"])

            if "script" in postConfig:
                post["script"]=str(postConfig["script"])
        except (IndexError, json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing post config: {e}")
            postConfig={}

        post["createdDate"]=format_date_utc8(post["createdAt"])
        post["dateLabelColor"]=deterministic_color(post["number"])

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
        html_stale = (not os.path.isfile(mdHtmlPath)) or post.get("buildedAt") != post["updatedAt"]
        mode = resolve_regen_mode(html_stale, post["description"], api_configured, self.desc_retry_budget)
        if mode:
            if mode == "rebuild":
                tool = Markdown2GithubHtml()
                mdHtml = tool.convert(content)
                with open(mdHtmlPath, 'w', encoding='UTF-8') as fp:
                    fp.write(mdHtml)
                post["buildedAt"] = post["updatedAt"]

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
        for issue in issues:
            self.addOnePostJson(issue)

        # 同plist排序, 便于post中获取上一篇和下一篇
        self.blogBase["postListJson"]=dict(sorted(self.blogBase["postListJson"].items(),key=lambda x:(x[1]["top"],x[1]["createdAt"]),reverse=True))

        for post in self.blogBase["postListJson"].values():
            self.createPostHtml(post)

        for post in self.blogBase["singeListJson"].values():
            self.createPostHtml(post)

        self.createPlistHtml()
        self.createFeedXml()
        print("====== create static html end ======")

    def runOne(self,number_str):
        print("====== start create static html ======")
        self.checkDir()

        issue=self.repo.get_issue(int(number_str))
        post = self.addOnePostJson(issue)
        if post:
            self.createPostHtml(post)
            self.createPlistHtml()
            self.createFeedXml()
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
            break
        print("====== create static html end ======")

#########################################################################
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("github_token", help="github_token")
    parser.add_argument("repo_name", help="repo_name")
    parser.add_argument("--issue_number", help="issue_number", default=0, required=False)
    options = parser.parse_args()

    blog=GMEEK(options)

    if options.issue_number=="0" or options.issue_number=="":
        print("runAll")
        blog.runAll()
    else:
        print(f"runOne {options.issue_number}")
        blog.runOne(options.issue_number)

    with open("blogBase.json","w",encoding='utf-8') as listFile:
        listFile.write(json.dumps(slim_state(blog.blogBase), indent=4))


if __name__ == "__main__":
    main()
#########################################################################
