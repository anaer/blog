## 当你使用 git clone --depth 1 克隆仓库时，Git 只会克隆最新的提交历史（浅克隆），并且默认只拉取默认分支（通常是 main 或 master）。如果你需要获取其他分支, 执行以下命令

```sh
git config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"
git fetch --depth=1
git checkout branch-name
```