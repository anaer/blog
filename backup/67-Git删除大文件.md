## 使用 git repo-clean 工具清理
git repo-clean是用 Golang 开发的具备 Git 仓库大文件扫描，清理，并重写 commit 提交记录功能的 Git 拓展工具。

### 下载
https://gitee.com/oschina/git-repo-clean/releases/
下载git-repo-clean-1.4.2-Windows-64.zip, 并解压将git-repo-clean.exe程序拷贝到环境变量PATH目录下

### 命令行

命令参数：
```
  -v, --verbose		显示处理的详细过程
  -V, --version		显示 git-repo-clean 版本号
  -h, --help		显示使用信息
  -p, --path		指定Git仓库的路径, 默认是当前目录，即'.'
  -s, --scan		扫描Git仓库数据，默认是扫描所有分支中的数据
  -f, --file		直接指定仓库中的文件或目录，与'--scan'不兼容
  -b, --branch		设置需要删除文件的分支, 默认是从所有分支中删除文件
  -l, --limit		设置扫描文件阈值, 比如: '--limit=10m'
  -n, --number		设置显示扫描结果的数量
  -t, --type		设置扫描文件后缀名，即文件类型
  -i, --interactive 	开启交互式操作
  -d, --delete		执行文件删除和历史重写过程
  -L, --lfs		将大文件转换为Git LFS指针文件
```
命令行式用法：

```
git repo-clean --verbose --scan --limit=10m --type=yaml --number=5

git repo-clean --verbose --scan --limit=50m --type=db3 --number=5
```

加上 --delete 选项，则会批量删除扫描出的文件，并重写相关提交历史(包括HEAD)

```
git repo-clean --verbose --scan --limit=10m --type=yaml --number=5 --delete
```

PS: 若直接在git项目的根目录进入 bash 命令窗口使用 repo-clean 命令时，显示无 repo-clean 命令，则可以通过左下角【开始】输入 cmd 进入命令窗口，然后使用命令切换至 git 项目的根目录，再使用 repo-clean 命令
目前扫描操作和删除操作都是默认在所有分支上进行，而--branch 选项只是指定删除时的分支，不能指定扫描时的分支。因此如果使用了这个选项指定了某个分支，可能从扫描结果中选择了另一个分支中的文件，因此不会有文件真正被删除。

**注意备份 可能存在误删的情况**
