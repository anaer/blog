---
title: VSCode相关记录
date: "2023-05-16T11:17:30.000Z"
description: VSCode相关记录
tags:
  - vscode
last_updated: "2023-05-16T11:17:30.000Z"
---

```toc
# This code block gets replaced with the TOC
```

### 正则替换记录

1. 删除中文超过6个的码表
```
^[\u4e00-\u9fa5]{6,}.*\n
```

2. 非中文开头

```
^[^\u4e00-\u9fa5].*\n
```

3. 包含特殊符号 如: `:`, `：`, `-` 等

```
.*[:：-]+.*\n
```