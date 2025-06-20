## 使用 Git 配置强制识别大小写变化
Git 默认在 大小写不敏感的系统（如 Windows/macOS 默认设置）中不会提交 仅大小写不同的文件名更改。

```sh
# 临时设置
git config core.ignorecase false
```

## 查询Git提交用户记录

```sh
git log --format="%an <%ae>" --all | sort | uniq
```

--all：包括所有分支的提交。

sort | uniq：对结果排序并去重。

输出示例：
```
random <r@n.dom>
```

## 修改历史提交用户信息

```sh
git filter-repo --name-callback "return b\"random\"" --email-callback "return b\"r@n.dom\"" --force

git push --force
```

PS: 在 Windows 的 CMD 中，单引号可能不被识别，建议用双引号

## depth=1 拉取其他分支 

当你使用 git clone --depth 1 克隆仓库时，Git 只会克隆最新的提交历史（浅克隆），并且默认只拉取默认分支（通常是 main 或 master）。如果你需要获取其他分支, 执行以下命令

```sh
git config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"
git fetch --depth=1
git checkout branch-name
```

将浅克隆转换为完整克隆
```sh
git fetch --unshallow
```

## 比较分支并导出变更文件

```sh
git diff 6db1256718a184ece757df2b7d8bf22444801661 8906e42d5aeff10b70086bd7aece0f3663edbddd --name-only | xargs zip update.zip

# 比较文件并导出为zip压缩包, 根据本机情况可以选择zip或者7zip
git diff feature/xxx-0719 origin/master --name-only | xargs zip user.zip

git diff feature/xxx-0719 origin/master --name-only | xargs 7z a -tzip user.zip
```

## 删除敏感文件历史提交记录
以`.vscode/settings.json`文件为例

```sh
git filter-branch --force --index-filter  "git rm --cached --ignore-unmatch .vscode/settings.json" --prune-empty --tag-name-filter cat -- --all

git add .
git commit -am "commit"
git push origin --force --all
```

 [067 Git删除大文件](https://anaer.github.io/blog/post/67.html)  