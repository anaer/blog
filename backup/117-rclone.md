### 配置

```sh
# 交互式配置
rclone config   

# 显示当前配置
rclone config show 

# 列出存储空间中的文件
rclone ls remote:path

# 同步本地文件夹到远程
rclone sync /path/to/local/folder remote:path

# 将文件或文件夹复制到远程
rclone copy /path/to/local/folder remote:path

# 从远程复制到本地
rclone copy remote:path /path/to/local/folder

# 移动文件或文件夹
rclone move /path/to/local/folder remote:path

# 检查远程路径的内容
rclone size remote:path

# 检查文件夹之间的差异
rclone check /path/to/local/folder remote:path

# 清除远程路径中的文件
rclone purge remote:path
```

## 相关链接
1. [rclone用户手册](https://www.cnblogs.com/cyl048/p/16635341.html)
2. [rclone命令索引](https://www.rclone.cn/index/rclone%E5%91%BD%E4%BB%A4%E7%B4%A2%E5%BC%95/)