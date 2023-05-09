---
title: 查询系统当前网络连接数
date: "2023-05-09T10:53:02.000Z"
description: 查询系统当前网络连接数
tags:
  - netstat
last_updated: "2023-05-09T10:53:02.000Z"
---

```toc
# This code block gets replaced with the TOC
```

## 查询系统当前网络连接数

```sh
netstat -n | awk '/^tcp/ {++S[$NF]} END {for(a in S) print a, S[a]}'

# CLOSE_WAIT 15
# ESTABLISHED 715
# FIN_WAIT2 1
# TIME_WAIT 1394
```

### 状态说明

| 连接状态    | 说明                                                                 |
| ----------- | -------------------------------------------------------------------- |
| CLOSED      | 表示连接已经关闭或不存在。                                           |
| LISTEN      | 表示服务器正在等待客户端的连接请求。                                 |
| SYN_RECV    | 表示服务器已经收到了客户端的连接请求，并正在等待确认。               |
| SYN_SENT    | 表示客户端已经发送了连接请求，正在等待服务器的确认。                 |
| ESTABLISHED | 表示连接已经建立，正在进行正常的数据传输。                           |
| FIN_WAIT1   | 表示应用程序已经完成发送数据，正在等待另一端的确认。                 |
| FIN_WAIT2   | 表示另一端已经同意释放连接。                                         |
| TIME_WAIT   | 表示连接已经关闭，但是还需要等待一段时间，以确保所有分组都已经死亡。 |
| CLOSING     | 表示两端同时尝试关闭连接。                                           |
| LAST_ACK    | 表示等待所有分组死亡。                                               |
