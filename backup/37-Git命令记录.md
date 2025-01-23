## depth=1 拉取其他分支 

当你使用 git clone --depth 1 克隆仓库时，Git 只会克隆最新的提交历史（浅克隆），并且默认只拉取默认分支（通常是 main 或 master）。如果你需要获取其他分支, 执行以下命令

```sh
git config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"
git fetch --depth=1
git checkout branch-name
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

#67 