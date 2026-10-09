#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从已生成的站点 HTML 抽取「标题 + 小节标题」，生成中文子串检索索引。

Pagefind 的中文索引是词级切分，对 2 字短词不稳定（实测标题内两字词约 1/3 搜不到
目标文章，而完整标题 / 小节标题 / 多字词 0% 漏检）。本索引按「连续子串」精确匹配
补齐这一档，只收 <title> 与正文容器内的 h1–h6 文本，不含正文，体积约 10KB 量级。

用法：python3 scripts/build_search_index.py <站点目录>
输出：<站点目录>/search-index/index.json
"""
import io
import json
import os
import sys
from html.parser import HTMLParser

HEADINGS = frozenset(("h1", "h2", "h3", "h4", "h5", "h6"))

# 空元素不参与嵌套深度计数（无对应结束标签）
VOID_TAGS = frozenset((
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
))

OUT_DIR = "search-index"
OUT_FILE = "index.json"
SCHEMA_VERSION = 1


def normalize(text):
    """折叠所有空白为单个空格（标题与标题文本可能含换行/缩进）。"""
    return " ".join(text.split())


class PageParser(HTMLParser):
    """抽取 <title> 与 data-pagefind-body 容器内的 h1–h6 文本。

    只认标记了 data-pagefind-body 的页面（与 Pagefind 的索引范围一致）；
    标题取自 <head>，小节标题只取正文容器内的，避免把页眉/页脚纳入。
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.headings = []
        self.has_body = False
        self._stack = []
        self._body_at = None      # data-pagefind-body 所在层级（未含该标签自身）
        self._in_title = False
        self._cap = None          # 正在捕获文本的标题标签名
        self._buf = []

    def _in_body(self):
        return self._body_at is not None and len(self._stack) > self._body_at

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._in_title = True
        if self._body_at is None and any(k == "data-pagefind-body" for k, _ in attrs):
            self.has_body = True
            self._body_at = len(self._stack)
        if tag not in VOID_TAGS:
            self._stack.append(tag)
        if self._cap is None and tag in HEADINGS and self._in_body():
            self._cap = tag
            self._buf = []

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if self._cap is not None and tag == self._cap:
            text = normalize("".join(self._buf))
            if text:
                self.headings.append(text)
            self._cap = None
            self._buf = []
        if self._stack:
            if self._stack[-1] == tag:
                self._stack.pop()
            elif tag in self._stack:
                # 容错：遇到不配对的结束标签时弹到匹配位置
                while self._stack and self._stack.pop() != tag:
                    pass

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._cap is not None:
            self._buf.append(data)


def extract_entry(html, rel_url):
    """从单页 HTML 抽取一条索引记录；页面无 data-pagefind-body 时返回 None。"""
    parser = PageParser()
    parser.feed(html)
    parser.close()
    if not parser.has_body:
        return None
    title = normalize(parser.title)
    headings = parser.headings
    if not title and not headings:
        return None
    return {"u": rel_url, "t": title, "h": " ".join(headings)}


def build(site_dir):
    """扫描站点目录，写出 search-index/index.json，返回索引载荷。"""
    site_dir = os.path.abspath(site_dir)
    skip_root = os.path.join(site_dir, OUT_DIR)
    entries = []
    for dirpath, dirnames, filenames in os.walk(site_dir):
        if os.path.abspath(dirpath) == skip_root:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for name in filenames:
            if not name.endswith(".html"):
                continue
            path = os.path.join(dirpath, name)
            with open(path, encoding="utf-8", errors="replace") as fh:
                html = fh.read()
            rel_url = os.path.relpath(path, site_dir).replace(os.sep, "/")
            entry = extract_entry(html, rel_url)
            if entry:
                entries.append(entry)

    entries.sort(key=lambda e: e["u"])
    payload = {"v": SCHEMA_VERSION, "count": len(entries), "entries": entries}
    out_dir = os.path.join(site_dir, OUT_DIR)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, OUT_FILE), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, separators=(",", ":"))
    return payload


def main(argv):
    # Windows 控制台默认 GBK，输出含中文时须显式切到 UTF-8
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    if len(argv) != 2:
        print("用法: build_search_index.py <站点目录>", file=sys.stderr)
        return 2
    site_dir = argv[1]
    if not os.path.isdir(site_dir):
        print(f"站点目录不存在: {site_dir}", file=sys.stderr)
        return 2
    payload = build(site_dir)
    print(f"子串检索索引: {payload['count']} 条 -> {OUT_DIR}/{OUT_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
