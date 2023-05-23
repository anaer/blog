---
title: VSCode的Thunder Client扩展
date: "2023-05-23T10:12:02.000Z"
description: VSCode的Thunder Client扩展
tags:
  - vscode
  - thunderclient
last_updated: "2023-05-23T10:12:02.000Z"
---

```toc
# This code block gets replaced with the TOC
```

# 说明

v2.6.2之后版本, git同步转为订阅功能, 需要先订阅
因为平时只是简单用用, 所以已转用Rest Client, 这里记录下相关说明, 以备后期有换回来的可能.

## 文件说明

| 文件名                  | 说明              |
| ----------------------- | ----------------- |
| thunderActivity.json    | 活动记录/历史记录 |
| thunderclient.json      | 请求记录          |
| thunderCollection.json  | 集合列表及配置    |
| thunderEnvironment.json | 环境变量配置      |
| thunderResponses.json   | 响应记录          |

## 系统变量

| 变量名                               | 说明                                  |
| ------------------------------------ | ------------------------------------- |
| {{#guid}}                            | 生成 guid                             |
| {{#string}}                          | 生成随机字符串                        |
| {{#number}}                          | 生成随机数字                          |
| {{#number, min, max}}                | 生成指定范围的随机数                  |
| {{#date}}                            | 生成时间戳 毫秒                       |
| {{#date, 'X'}}                       | 生成时间戳 秒                         |
| {{#date, 'YYYY-MM-DD hh:mm:ss.fff'}} | 生成指定格式的日期                    |
| {{#dateISO}}                         | 生成日期 ISO 格式                     |
| {{#bool}}                            | 生成随机布尔值 true/false             |
| {{#enum, val1, val2, val3}}          | 枚举中取一个值 eg: {{#enum, 1, 2, 3}} |
