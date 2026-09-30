#!/usr/bin/env python3
"""校验文章中的外链可用性, 结果输出到标准输出(供 CI 日志查看)。

扫描指定目录下的文章 HTML, 抽取其中的外链(排除本站前缀), 并发探测可用性,
按「失效 / 可能被拦截」分类打印。仅输出, 不修改任何文件。

用法:
    python scripts/check_links.py --dir site/docs/post
    python scripts/check_links.py --dir docs/post --exclude https://example.com --fail-on-broken
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser

UA = "Mozilla/5.0 (compatible; Gmeek-LinkChecker/1.0)"


class _AnchorParser(HTMLParser):
    """收集 HTML 中所有 <a href> 的值。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        for name, value in attrs:
            if name == "href" and value:
                self.links.append(value)


def extract_links(html_text):
    """抽取 HTML 中所有 <a href> 的值。"""
    parser = _AnchorParser()
    parser.feed(html_text)
    return parser.links


def is_external(url, exclude_prefix):
    """是否为需校验的外链: http(s) 且不属于本站前缀。"""
    if not url.startswith(("http://", "https://")):
        return False
    if exclude_prefix and url.startswith(exclude_prefix):
        return False
    return True


def classify(status):
    """按状态码分类: ok / broken / suspicious(403、429 多为反爬)。"""
    if 200 <= status < 400:
        return "ok"
    if status in (403, 429):
        return "suspicious"
    return "broken"


def probe(url, timeout):
    """探测单个 URL, 返回 (url, status 或 None, 错误信息)。"""
    last_err = "请求失败"
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return url, resp.status, ""
        except urllib.error.HTTPError as e:
            # 部分站点禁用 HEAD(405/501)或对 HEAD 返回 403/429, 退回 GET 再试
            if method == "HEAD" and e.code in (403, 405, 429, 501):
                last_err = "HTTP %d" % e.code
                continue
            return url, e.code, ""
        except Exception as e:  # URLError / socket.timeout / 其它
            last_err = str(e)
            if method == "HEAD":
                continue
            return url, None, last_err
    return url, None, last_err


def collect(directory, exclude_prefix):
    """递归扫描目录下所有 .html, 返回 {url: [来源文件相对路径, ...]}。"""
    found = {}
    for root, _, files in os.walk(directory):
        for name in sorted(files):
            if not name.endswith(".html"):
                continue
            path = os.path.join(root, name)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    html = f.read()
            except OSError:
                continue
            rel = os.path.relpath(path, directory)
            for url in extract_links(html):
                if is_external(url, exclude_prefix):
                    sources = found.setdefault(url, [])
                    if rel not in sources:
                        sources.append(rel)
    return found


def _resolve_exclude(explicit, config_path):
    if explicit:
        return explicit
    if config_path and os.path.isfile(config_path):
        try:
            with open(config_path, encoding="utf-8") as f:
                return json.load(f).get("homeUrl", "") or ""
        except (OSError, json.JSONDecodeError):
            return ""
    return ""


def main(argv=None):
    ap = argparse.ArgumentParser(description="校验文章中的外链可用性")
    ap.add_argument("--dir", required=True, help="文章 HTML 所在目录(递归扫描 *.html)")
    ap.add_argument("--exclude", default="", help="排除的站内前缀(默认读取 config.json 的 homeUrl)")
    ap.add_argument("--config", default="config.json", help="配置文件路径(用于取 homeUrl)")
    ap.add_argument("--timeout", type=float, default=15.0, help="单个请求超时秒数")
    ap.add_argument("--workers", type=int, default=16, help="并发数")
    ap.add_argument("--fail-on-broken", action="store_true", help="发现失效链接时以非零码退出")
    args = ap.parse_args(argv)

    exclude = _resolve_exclude(args.exclude, args.config)

    if not os.path.isdir(args.dir):
        print(f"目录不存在: {args.dir}")
        return 1

    found = collect(args.dir, exclude)
    urls = sorted(found)

    print("=" * 64)
    print(f"外链校验 | 目录: {args.dir}")
    print(f"排除站内前缀: {exclude or '(无)'}")
    print(f"去重后待校验外链: {len(urls)} 条")
    print("=" * 64)

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(probe, u, args.timeout) for u in urls]
        for fut in concurrent.futures.as_completed(futures):
            results.append(fut.result())

    broken, suspicious = [], []
    for url, status, err in results:
        if status is None:
            broken.append((url, err))
        else:
            kind = classify(status)
            if kind == "broken":
                broken.append((url, "HTTP %d" % status))
            elif kind == "suspicious":
                suspicious.append((url, "HTTP %d" % status))

    ok = len(urls) - len(broken) - len(suspicious)
    print(f"\n结果: 正常 {ok} 条 / 失效 {len(broken)} 条 / 可能被拦截 {len(suspicious)} 条")

    def dump(title, items):
        print(f"\n【{title}】{len(items)} 条")
        for url, reason in sorted(items):
            print(f"  - {url}  ->  {reason}")
            for src in found[url]:
                print(f"      来源: {src}")

    dump("失效链接", broken)
    dump("可能被拦截(403/429, 多为反爬, 需人工确认)", suspicious)

    if args.fail_on_broken and broken:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
