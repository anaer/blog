# -*- coding: utf-8 -*-
"""外链校验脚本的纯函数单测: 链接抽取 / 外链判定 / 状态分类。"""
from scripts.check_links import extract_links, is_external, classify


class TestExtractLinks:
    def test_collects_anchor_hrefs(self):
        html = '<a href="https://a.com">A</a><a href="/rel">R</a>'
        assert extract_links(html) == ["https://a.com", "/rel"]

    def test_ignores_non_anchor(self):
        # 负向控制: 图片/样式等非 <a> 的链接不计入
        html = '<img src="https://a.com/x.png"><link href="https://a.com/y.css">'
        assert extract_links(html) == []

    def test_empty(self):
        assert extract_links("<p>no links</p>") == []


class TestIsExternal:
    def test_http_is_external(self):
        assert is_external("https://a.com", "https://me.com")

    def test_site_prefix_excluded(self):
        assert not is_external("https://me.com/blog/post/1.html", "https://me.com/blog")

    def test_relative_excluded(self):
        assert not is_external("/post/1.html", "https://me.com")

    def test_mailto_excluded(self):
        assert not is_external("mailto:a@b.com", "https://me.com")

    def test_no_prefix_keeps_http(self):
        assert is_external("https://a.com", "")


class TestClassify:
    def test_ok(self):
        assert classify(200) == "ok"
        assert classify(301) == "ok"

    def test_broken(self):
        assert classify(404) == "broken"
        assert classify(500) == "broken"

    def test_suspicious(self):
        # 负向控制: 403/429 多为反爬, 不应直接判为失效
        assert classify(403) == "suspicious"
        assert classify(429) == "suspicious"
