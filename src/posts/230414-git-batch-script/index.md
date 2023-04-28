---
title: Git批处理脚本
date: "2023-04-14T17:07:39.000Z"
description: Git批处理脚本
tags:
  - git
  - cmd
last_updated: "2023-04-14T17:07:39.000Z"
---

```toc
# This code block gets replaced with the TOC
```

## git推拉脚本

因github容易连不上, 所以pull, push时, 有时需要循环执行
暂定间隔5秒循环执行, 一般10次以内能成功 这里设置了100次, 如果需要永久循环 设置为(0,0,1)

用法: 将pull.cmd, push.cmd脚本放到PATH目录下, 使用时直接在仓库目录, 执行pull, push即可

### pull.cmd

```bat
@echo off
chcp 65001
echo git pull
for /l %%a in (1,1,100) do (echo %%a------------------- && git pull && goto :EOF; sleep 5)

:EOF
echo -------------------end
```

### push.cmd

```bat
@echo off
chcp 65001
echo git push
for /l %%a in (1,1,100) do (echo %%a------------------- && git push && goto :EOF; sleep 5)

:EOF
echo -------------------end
```

---

## 历史

### 循环pull

```bat
@echo off
chcp 65001
for /l %%a in (0,0,1) do (git pull && exit; sleep 3)
```

cmd直接执行的话 需要少一个%
```cmd
for /l %a in (0,0,1) do (git pull && exit; sleep 3)
```

### 循环push

```bat
@echo off
chcp 65001
for /l %%a in (0,0,1) do (git push && exit; sleep 3)
```

cmd直接执行的话 需要少一个%
```cmd
for /l %a in (0,0,1) do (git push && exit; sleep 3)
```

创建cmd脚本, 并将脚本放到环境变量PATH目录下, 在git仓库目录下 可以直接执行
