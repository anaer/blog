
## 循环执行脚本
判断参数命令执行结果, 如果失败则重复执行
`retry.cmd git push origin main`

```sh
@echo off
chcp 65001
echo %*
for /l %%a in (1,1,100) do (echo %%a------------------- && %* && goto :EOF; sleep 5)

:EOF
echo -------------------end
```

## git推拉脚本

因github容易连不上, 所以pull, push时, 有时需要循环执行
暂定间隔5秒循环执行, 一般10次以内能成功 这里设置了100次, 如果需要永久循环 设置为(0,0,1)

用法: 将pull.cmd, push.cmd脚本放到PATH目录下, 使用时直接在仓库目录, 执行pull, push即可

### pull.cmd

```sh
@echo off
chcp 65001
rem 因github容易连不上, 所以间隔5秒循环执行, 一般10次以内都能成功 这里设置了100次, 如果需要永久循环 设置为(0,0,1)
echo git pull
git rev-parse --is-inside-work-tree >nul 2>nul
if %errorlevel% equ 0 (
    for /l %%a in (1,1,100) do (echo %%a----------------------- && git pull && goto :EOF; sleep 5)
) else (
    echo 当前目录不是git仓库
)
:EOF
echo -------------------------end
```

### push.cmd

```sh
@echo off
chcp 65001
rem 因github容易连不上, 所以间隔5秒循环执行, 一般10次以内都能成功 这里设置了100次, 如果需要永久循环 设置为(0,0,1)
echo git push
git rev-parse --is-inside-work-tree >nul 2>nul
if %errorlevel% equ 0 (
    for /l %%a in (1,1,100) do (echo %%a------------------- && git push && goto :EOF; sleep 5)
) else (
    echo 当前目录不是git仓库
)

:EOF
echo -------------------end
```

### apull.cmd 先暂存本地变更, 再pull, 最后恢复变更

```sh
@echo off
chcp 65001 >nul
echo 正在检查本地变更...
git update-index -q --refresh
:: 判断是否有未暂存/未提交的修改
git diff --quiet HEAD -- 2>nul
if %errorlevel% equ 0 (
    echo █ 没有本地修改，直接拉取更新...
) else (
    echo █ 检测到未保存的修改，正在临时存储...
    git stash push -m "AutoStash_%DATE%_%TIME%" --quiet
    echo █ 已暂存本地修改： && git stash list | findstr "AutoStash"
)
:: 执行拉取操作
echo █ 正在从远程仓库拉取更新...
git pull
:: 如果有暂存则恢复
if %errorlevel% equ 0 if exist .git/refs/stash (
    echo █ 正在恢复暂存的修改...
    git stash pop --index --quiet
    echo 本地修改已恢复 ^!
)
echo █ 操作完成 ^!

```

## Mac添加alias实现

```
pull='for i in `seq 1 100`; do echo $i && git pull && break; sleep 5; done'
push='for i in `seq 1 100`; do echo $i && git push && break; done'
```

## chcp
修改cmd编码

```sh
chcp 936  #GBK
chcp 65001 #UTF-8
```