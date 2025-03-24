
## 清理日志目录超过1G的日志文件
不删文件只清空

```sh
find /data/app_log -type f -name "*.log" -size +1G -exec truncate -s 0 {} \;
```