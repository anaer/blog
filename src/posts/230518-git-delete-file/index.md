---
title: Git删除敏感文件的历史记录
date: "2023-05-18T17:26:12.000Z"
description: Git删除敏感文件的历史记录
tags:
  - git
last_updated: "2023-05-18T17:26:12.000Z"
---

```toc
# This code block gets replaced with the TOC
```

## 删除文件历史提交记录
以`.vscode/settings.json`文件为例

```sh
git filter-branch --force --index-filter  "git rm --cached --ignore-unmatch .vscode/settings.json" --prune-empty --tag-name-filter cat -- --all

git add .
git commit -am "commit"
git push origin --force --all
```