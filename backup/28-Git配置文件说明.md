## git数据传输

```
workspace       index          local repository      remote repository
-------------commit -a---------------->|
--------add------>|--------commit----->|
                                        -------push-------->|
<------------------------pull-------------------------------|
                                       |<------fetch--------|
<--------------checkout head-----------|
<-----checkout----|
<-----------------diff head------------|
<------diff-------|
```

workspace            用户的工作空间
index                数据缓存区
local repository     本地仓库
remote repository    远程仓库

## .git/config

```conf
[core]
	# repositoryformatversion 指定 Git 仓库的版本，默认值为 0，通常不需要修改
	repositoryformatversion = 0  

	# filemode 表示是否跟踪文件的权限变化
	# true: 跟踪权限变化（适用于 Linux/macOS）
	# false: 忽略权限变化（适用于 Windows）
	filemode = false  

	# bare 表示是否为裸仓库（无工作区，仅存储 Git 数据）
	# true: 裸仓库，适用于远程仓库
	# false: 非裸仓库，适用于本地开发
	bare = false  

	# logallrefupdates 表示是否记录所有引用的更新（如分支、标签等的变化）
	# true: 启用，便于日志追踪
	# false: 禁用
	logallrefupdates = true  

	# ignorecase 指定是否忽略文件名的大小写差异
	# true: 忽略大小写（适用于 Windows/Mac）
	# false: 区分大小写（适用于 Linux）
	ignorecase = false  

	# autocrlf 指定是否在换行符转换上启用自动化处理
	# true: 提交时将 CRLF 转换为 LF，检出时将 LF 转换为 CRLF（适用于 Windows）
	# input: 提交时将 CRLF 转换为 LF，检出时不做转换（适用于 Linux/Mac）
	# false: 不进行任何换行符转换
	autocrlf = false  

[remote "origin"]
	# url 是远程仓库的地址，支持 HTTP(S)、SSH 等协议
	url = https://github.com/xxx/xxx.git  

	# fetch 定义从远程仓库抓取分支的规则
	# +refs/heads/main:refs/remotes/origin/main 表示同步远程主分支到本地
	fetch = +refs/heads/main:refs/remotes/origin/main  

[branch "main"]
	# remote 指定当前分支关联的远程仓库
	remote = origin  

	# merge 指定当前分支与远程仓库的哪个分支进行合并
	merge = refs/heads/main  

	# vscode-merge-base 是 Visual Studio Code 的扩展字段，用于记录分支合并基线
	vscode-merge-base = origin/main  

[user]
	# name 是用户的 Git 提交签名用户名
	name = random  

	# email 是用户的 Git 提交签名邮箱地址
	email = a@b.com  
```

## .gitattritubes

```conf
# 设置文本文件的换行符处理规则
# text: 指定文件为文本文件，Git 将自动处理换行符
# eol=lf: 仓库中保存 LF（适用于 Linux/Mac）
# eol=crlf: 仓库中保存 CRLF（适用于 Windows）
# auto: 根据系统自动设置换行符
* text eol=lf

# 为 Markdown 文件强制指定为文本文件，使用 LF 换行符
*.md text eol=lf

# 为批处理脚本文件强制指定为文本文件，使用 CRLF 换行符
*.bat text eol=crlf

# 忽略二进制文件的自动换行符处理
# binary: 指定文件为二进制文件，Git 不会进行任何换行符转换
*.png binary
*.jpg binary
*.zip binary

# 禁用合并策略的处理，防止合并冲突对某些文件类型生效
# merge=ours: 在合并时使用“我们”的版本，忽略对方的更改
*.lock merge=ours

# 为 JSON 文件指定自定义差异工具
# diff=custom_json: 使用自定义工具处理 JSON 文件的差异
*.json diff=custom_json

# 配置大文件的存储，使用 Git LFS
# filter=lfs: 启用 Git LFS（大文件存储）过滤器
*.psd filter=lfs
*.mp4 filter=lfs

# 指定文件在合并时自动接受所有更改
# merge=union: 合并时自动保留双方的更改
*.txt merge=union
```