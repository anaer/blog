---
title: VSCode添加文件头片段
date: "2023-04-13T17:33:17.000Z"
description: VSCode添加文件头片段
tags:
  - vscode
last_updated: "2023-04-13T17:33:17.000Z"
---

## 日期变量

在 Visual Studio Code 中，可以使用内置的日期变量来快速插入当前日期、时间等信息。常用的日期变量如下：

1. `${CURRENT_YEAR}` 表示当前年份，比如 `2023`。

2. `${CURRENT_MONTH}` 表示当前月份，是一个数字形式的字符串，可能包含前导零（比如 `04`）。

3. `${CURRENT_DATE}` 表示当前日期，是一个数字形式的字符串，可能包含前导零（比如 `13`）。

4. `${CURRENT_HOUR}` 表示当前小时数，是一个数字形式的字符串，可能包含前导零（比如 `08`）。

5. `${CURRENT_MINUTE}` 表示当前分钟数，是一个数字形式的字符串，可能包含前导零（比如 `20`）。

6. `${CURRENT_SECOND}` 表示当前秒数，是一个数字形式的字符串，可能包含前导零（比如 `02`）。

7. `${CURRENT_SECONDS_UNIX}` 表示当前时间戳，是一个整数。

这些日期变量可以在代码编辑器中直接输入，也可以在 VSCode 中添加自定义代码片段，这样在编辑代码时更加方便快捷。
如果需要指定日期格式，可以在日期变量后面添加格式化参数，比如 `${CURRENT_DATE:YYYY-MM-DD}` 表示以 `yyyy-mm-dd` 的格式展示当前日期。

## snippet模板

```json
	"add blog": {
		"prefix": "blog",
		"body": [
			"---",
			"title: ",
			"date: \"${CURRENT_YEAR}-${CURRENT_MONTH}-${CURRENT_DATE}T${CURRENT_HOUR}:${CURRENT_MINUTE}:${CURRENT_SECOND}.000Z\"",
			"description: ",
			"tags:",
			"  - tag",
			"---"
		],
		"description": "添加blog"
	}
```

PS: 试了指定日期格式 `${CURRENT_DATE:YYYY-MM-DDTHH:mm:ss.SSSZ}` 未成功, 还是输出的当前日期数字(13)

## 用法
`Ctrl+P`选择命令`Snippets:Insert Snippet`, 再选`blog` 选择snippet