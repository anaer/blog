---
title: Git配置项
date: "2023-05-30T15:14:12.000Z"
description: Git配置项
tags:
  - git
last_updated: "2023-06-30T10:43:16.000Z"
---

```toc
# This code block gets replaced with the TOC
```

## credential.helper

git config credential.helper 是一个Git配置项,用于设置Git的凭据存储助手工具。
它常用的设置值有:

1. cache - 缓存模式,缓存凭据一段时间。默认的缓存时间是15分钟。
2. store - 将凭据永久存储在磁盘上。这需要使用`git credential-store`命令进行初始化设置。
3. forget - 从不记住凭据信息。每次都会提示输入用户名和密码。
4. manager - 使用外部密码管理器工具来存储凭据。需要设置密码管理器的路径,例如:/path/to/my/program。
5. osxkeychain - 使用Mac的钥匙串来存储凭据信息。仅在Mac系统下可用。

设置方法:

```bash
# 设置为store模式,长期存储凭据
git config --global credential.helper store

# 设置为cache模式,凭据信息15分钟过期
git config --global credential.helper cache

# 设置为使用密码管理器程序,路径为"/path/to/my/program"
git config --global credential.helper "/path/to/my/program"
```

设置此配置后,当使用`git pull`或`git push`与远程仓库交互时,Git会根据配置的模式来读取或存储凭据信息,避免每次都手动输入用户名及密码。
例如,设置为`store`模式后,首次推送时会弹出输入框要求输入用户名及密码。输入后会长期存储,下次操作远程仓库时可以直接使用,不再需要输入。

如果重复配置, 会提示以下信息, 可以添加`--replace-all`参数 进行替换
```log
λ git config --global credential.helper store
warning: credential.helper has multiple values
error: cannot overwrite multiple values with a single value
       Use a regexp, --add or --replace-all to change credential.helper.

λ git config --global credential.helper store  --replace-all
```

## 错误处理

1. git credential-'cache store: -c: line 1: unexpected EOF while looking for matching `''

`git config -l --show-origin` 查询当前生效的配置文件以及对应的配置文件, 然后对错误的配置项进行修改

## 参考资源

[Git官方文档](https://git-scm.com/docs/git-config#Documentation/git-config.txt-credentialcache)