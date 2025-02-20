# -*- coding: utf-8 -*-
import os
import random
import re
import json
import time
import shutil
import urllib
import requests
import argparse
from datetime import datetime, timedelta
from github import Github
from feedgen.feed import FeedGenerator
from jinja2 import Environment, FileSystemLoader
from bs4 import BeautifulSoup
from Summary import generate_summary

######################################################################################
i18n={"Search":"Search","switchTheme":"switch theme","link":"link","home":"home","comments":"comments","run":"run ","days":" days","Previous":"Previous","Next":"Next"}
i18nCN={"Search":"搜索","switchTheme":"切换主题","link":"友情链接","home":"首页","comments":"评论","run":"网站运行","days":"天","Previous":"上一页","Next":"下一页"}
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
######################################################################################
class GMEEK():
    def __init__(self,options):
        self.options=options

        self.post_folder='post/'

        self.root_dir='docs/'
        self.backup_dir='backup/'
        self.post_dir=self.root_dir+self.post_folder

        # 获取Github仓库信息
        user = Github(self.options.github_token)
        self.repo = user.get_repo(options.repo_name)

        # 读取仓库的labels标签颜色
        self.labelColorDict=json.loads('{}')
        for label in self.repo.get_labels():
            self.labelColorDict[label.name]='#'+label.color
        # print(self.labelColorDict)

        self.defaultConfig()

    def cleanFile(self):
        # if os.path.exists(self.backup_dir):
            # shutil.rmtree(self.backup_dir)

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

    def defaultConfig(self):
        '''
        初始化配置, 主要用于runAll
        runOne 因为有重新赋值, 没用到
        '''
        dconfig={"startSite":"","filingNum":"","onePageListNum":15,"commentLabelColor":"#006b75","i18n":"CN","dayTheme":"light","nightTheme":"dark"}
        config=json.loads(open('config.json', 'r', encoding='utf-8').read())
        self.blogBase={**dconfig,**config}.copy()
        self.blogBase["postListJson"]=json.loads('{}')
        self.blogBase["singeListJson"]=json.loads('{}')
        if self.blogBase["i18n"]=="CN":
            self.i18n=i18nCN
        else:
            self.i18n=i18n

        self.blogBase["labelColorDict"]=self.labelColorDict
        self.blogBase["issuesUrl"]="https://github.com/"+self.repo.full_name+"/issues"

        self.cacheBlogBase=self.blogBase

    def markdown2html(self, mdstr, retries=3):
        """
        调用github api将markdown文本转为html格式代码, 请求失败时 重试3次
        """
        payload = {"text": mdstr, "mode": "markdown"}
        headers = {"Authorization": "token {}".format(self.options.github_token)}
        for attempt in range(retries):
            ret = requests.post("https://api.github.com/markdown", json=payload, headers=headers)
            if ret.status_code == 200:
                return ret.text
            else:
                print(f"Attempt {attempt + 1} failed with status code {ret.status_code}")
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
        f = open(htmlDir, 'w', encoding='UTF-8')
        f.write(output)
        f.close()

    def createPostHtml(self, post):
        f = open(post["markdown"]+".html", 'r', encoding='UTF-8')
        post_body=f.read()
        f.close()

        postBase=self.blogBase.copy()
        postBase["postTitle"]=post["postTitle"]
        postBase["labels"]=post["labels"]
        postBase["commentNum"]=post["commentNum"]
        postBase["style"]=post["style"]
        postBase["script"]=post["script"]
        postBase["top"]=post["top"]
        postBase["postSourceUrl"]=post["postSourceUrl"]
        postBase["repoName"]=options.repo_name
        postBase["description"]=post["description"]
        postBase["postBody"]=post_body
        postBase["createdAt"]=time.strftime("%Y-%m-%d", time.gmtime(post["createdAt"]))
        postBase["updatedAt"]=time.strftime("%Y-%m-%d", time.gmtime(post["updatedAt"]))

        prevPost = self.get_prev_post(post["number"])
        if prevPost:
            postBase["prevUrl"]=self.blogBase["homeUrl"] + "/" + prevPost["postUrl"]
            postBase["prevTitle"]=prevPost["postTitle"]

        nextPost = self.get_next_post(post["number"])
        if nextPost:
            postBase["nextUrl"]=self.blogBase["homeUrl"] + "/" + nextPost["postUrl"]
            postBase["nextTitle"]=nextPost["postTitle"]

        if "highlight" in post_body:
            postBase["highlight"]=1
            # 随机使用高亮样式
            index = int(post["number"]) % len(starryNightStyles)
            postBase["starryNight"] = starryNightStyles[index]
        else:
            postBase["highlight"]=0

        self.renderHtml('post.html',postBase,{},post["htmlDir"])
        # print("create postPage title=%s file=%s " % (issue["postTitle"],issue["htmlDir"]))

    def createPlistHtml(self):
        """
        生成列表页面
        """
        # 排序规则: 1-是否置顶 2: 按更新时间降序
        self.blogBase["postListJson"]=dict(sorted(self.blogBase["postListJson"].items(),key=lambda x:(x[1]["top"],x[1]["updatedAt"]),reverse=True))

        postNum = len(self.blogBase["postListJson"])
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

            self.renderHtml('plist.html', self.blogBase, onePageList, htmlDir)
            print(f"create {htmlDir}")

            postNum -= self.blogBase["onePageListNum"]
            pageFlag += 1

        # 生成标签页面
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
        summary = generate_summary(content)

        if summary == "" and len(content) > 100:
            summary = content[:100] + "..."

        return summary

    def get_background_color(self, createdAt, updatedAt):
        # 色相：0 到 360
        hue = (140 + (updatedAt - createdAt).days) % 360
        # 饱和度：30% 到 70%
        saturation = random.randint(30, 70)
        # 明度：10% 到 40%
        lightness = random.randint(10, 40)
        return f"hsl({hue}, {saturation}%, {lightness}%)"

    def normalize_title(self, title):
        """
        定义方法 规范标题, 替换文件名不支持的符号为_
        """
        return re.sub(r'[\\/*?:"<>|]', '_', title)

    def get_prev_post(self, issuenumber):
        keys = list(self.blogBase["postListJson"])
        try:
            index = keys.index("P" + str(issuenumber))
            if index > 0:
                prev_key = keys[index - 1]
            else:
                prev_key = keys[len(keys) - 1]
            return self.blogBase["postListJson"][prev_key]
        except:
            return None

    def get_next_post(self, issuenumber):
        keys = list(self.blogBase["postListJson"])
        try:
            index = keys.index("P" + str(issuenumber))
            if index < len(keys) - 1:
                next_key = keys[index + 1]
            else:
                next_key = keys[0]
            return self.blogBase["postListJson"][next_key]
        except:
            return None

    def addOnePostJson(self,issue):
        if self.repo.owner.name != issue.user.name:
            # 有需要可以设置白名单
            print("非仓库主创建的issue, 不进行生成")
            return

        # 因为当前没用单页, 暂不处理这块逻辑
        if len(issue.labels) >= 1 and issue.labels[0].name in self.blogBase["singlePage"]:
            listJsonName='singeListJson'
            gen_Html = 'docs/{}.html'.format(issue.labels[0].name)
        else:
            listJsonName='postListJson'
            gen_Html = self.post_dir+'{}.html'.format(issue.number)

        mdPath = "backup/"+str(issue.number)+"-"+self.normalize_title(issue.title)+".md"

        labels = []
        for label in issue.labels:
            labels.append(label.name)

        postNum="P"+str(issue.number)
        post=json.loads('{}')
        post["number"]=str(issue.number)
        post["htmlDir"]=gen_Html
        post["markdown"]=mdPath
        post["labels"]=labels
        post["postTitle"]="%d %s" % (issue.number, issue.title)
        post["postUrl"]=urllib.parse.quote(self.post_folder+'{}.html'.format(issue.number))
        post["postSourceUrl"]="https://github.com/"+options.repo_name+"/issues/"+str(issue.number)
        post["commentNum"]=issue.get_comments().totalCount
        post["createdAt"]=int(time.mktime(issue.created_at.timetuple()))
        post["updatedAt"]=int(time.mktime(issue.updated_at.timetuple()))

        post["top"]=0
        # 如果issue为关闭状态, 显示在最后
        if issue.state=="closed":
            post["top"]=-1
        else:
            for event in issue.get_events():
                if event.event=="pinned":
                    post["top"]=1
                    break
                elif event.event=="unpinned":
                    break

        post["style"]=""
        post["script"]=""
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
        except:
            postConfig={}

        createdAt=datetime.fromtimestamp(post["createdAt"])
        updatedAt=datetime.fromtimestamp(post["updatedAt"])
        dateLabelColor = self.get_background_color(createdAt, updatedAt)
        post["createdDate"]=createdAt.strftime("%Y-%m-%d")
        post["dateLabelColor"]= dateLabelColor

        # print(f"日期标签颜色: {issue.title} {createdAt} {updatedAt} {dateLabelColor}")

        # 处理正文中的#数字链接
        content = issue.body
        regex = r"\s*#(\d+)\s*"
        matches = re.findall(regex, content)
        for match in matches:
            # print(f"Found number: {issue.title} {match}")
            matchPostNum = "P"+str(match)
            # 因为postListJson每次执行会先清空, 所以使用缓存处理, 与最新数据可能有差异, 但不太影响
            if matchPostNum in self.cacheBlogBase[listJsonName]:
                content = content.replace("#"+match, " ["+self.cacheBlogBase[listJsonName][matchPostNum]["postTitle"]+"]("+self.blogBase["homeUrl"]+"/"+self.cacheBlogBase[listJsonName][matchPostNum]["postUrl"]+") ")
                # print(content)

        f = open(mdPath, 'w', encoding='UTF-8')
        f.write(content)
        f.close()

        mdHtmlPath = mdPath + ".html"
        # 需要使用缓存的buildedAt与当前的updatedAt进行比较
        # print(mdHtmlPath, os.path.isfile(mdHtmlPath), self.cacheBlogBase[listJsonName][postNum]["buildedAt"], post["updatedAt"])
        if (not os.path.isfile(mdHtmlPath) or "buildedAt" not in self.cacheBlogBase[listJsonName][postNum] or self.cacheBlogBase[listJsonName][postNum]["buildedAt"] != post["updatedAt"]):
            mdHtml = self.markdown2html(content)
            fp = open(mdHtmlPath, 'w', encoding='UTF-8')
            fp.write(mdHtml)
            fp.close()

            soup = BeautifulSoup(mdHtml, "html.parser")
            plain_text = soup.get_text()
            post["description"] = self.build_desc(plain_text)
        else:
            print(f"mdHtml {mdHtmlPath} exists and updatedAt is not changed")
            post["description"] = self.cacheBlogBase[listJsonName][postNum]["description"]

        post["buildedAt"]=post["updatedAt"]

        self.blogBase[listJsonName][postNum] = post
        return post

    def runAll(self):
        print("====== start create static html ======")
        self.cleanFile()

        issues=self.repo.get_issues(state="all")
        print("issue count:%d"%(len(list(issues))))
        for issue in issues:
            self.addOnePostJson(issue)

        # 同plist排序, 便于post中获取上一篇和下一篇
        self.blogBase["postListJson"]=dict(sorted(self.blogBase["postListJson"].items(),key=lambda x:(x[1]["top"],x[1]["updatedAt"]),reverse=True))

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

#########################################################################
parser = argparse.ArgumentParser()
parser.add_argument("github_token", help="github_token")
parser.add_argument("repo_name", help="repo_name")
parser.add_argument("--issue_number", help="issue_number", default=0, required=False)
options = parser.parse_args()

blog=GMEEK(options)

if not os.path.exists("blogBase.json"):
    print("blogBase is not exists, runAll")
    blog.runAll()
else:
    f=open("blogBase.json","r")
    blog.cacheBlogBase=json.loads(f.read())
    f.close()
    if options.issue_number=="0" or options.issue_number=="":
        print("issue_number=='0', runAll")
        blog.runAll()
    else:
        print("blogBase is exists and issue_number!=0, runOne")
        blog.blogBase=blog.cacheBlogBase
        blog.blogBase["labelColorDict"]=blog.labelColorDict
        blog.runOne(options.issue_number)

listFile=open("blogBase.json","w")
listFile.write(json.dumps(blog.blogBase, indent=4))
listFile.close()
#########################################################################
