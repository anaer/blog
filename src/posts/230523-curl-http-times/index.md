---
title: Curl查询Http请求各阶段耗时
date: "2023-05-23T15:39:07.000Z"
description: Https请求耗时分析
tags:
  - http
  - curl
last_updated: "2023-05-23T15:39:07.000Z"
---

```toc
# This code block gets replaced with the TOC
```

## 通过curl命令来查询https请求各阶段的耗时

curl命令支持以下阶段的时间统计：

| 阶段               | 说明                                                                   |
| ------------------ | ---------------------------------------------------------------------- |
| time_namelookup    | 从请求开始到DNS解析完成的耗时                                          |
| time_connect       | 从请求开始到TCP三次握手完成耗时                                        |
| time_appconnect    | 从请求开始到TLS握手完成的耗时                                          |
| time_pretransfer   | 从请求开始到向服务器发送第一个GET请求开始之前的耗时                    |
| time_redirect      | 重定向时间，包括到内容传输前的重定向的DNS解析、TCP连接、内容传输等时间 |
| time_starttransfer | 从请求开始到内容传输前的时间                                           |
| time_total         | 从请求开始到完成的总耗时                                               |

HTTP性能指标：

| 指标               | 说明                                         |
| ------------------ | -------------------------------------------- |
| DNS请求耗时        | 域名的NS及本地使用DNS的解析速度              |
| TCP建立耗时        | 服务器网络层面的速度                         |
| SSL握手耗时        | 服务器处理HTTPS等协议的速度                  |
| 服务器处理请求时间 | 服务器处理HTTP请求的速度                     |
| TTFB               | 服务器从接收请求到开始到收到第一个字节的耗时 |
| 服务器响应耗时     | 服务器响应第一个字节到全部传输完成耗时       |
| 请求完成总耗时     | 服务器从请求开始到完成的总耗时               |

DNS请求耗时 = time_namelookup
TCP三次握手耗时 = time_connect - time_namelookup
SSL握手耗时 = time_appconnect - time_connect
服务器处理请求耗时 = time_starttransfer - time_pretransfer
TTFB耗时 = time_starttransfer - time_appconnect
服务器传输耗时 = time_total - time_starttransfer
总耗时 = time_total

curl命令：

```sh
curl -w '
   time_namelookup: %{time_namelookup}
      time_connect: %{time_connect}
   time_appconnect: %{time_appconnect}
     time_redirect: %{time_redirect}
  time_pretransfer: %{time_pretransfer}
time_starttransfer: %{time_starttransfer}
        ------------------------
        time_total: %{time_total}' -o /dev/null -s -L 'https://www.baidu.com/'
```