## 查询系统版本

```sh
# 查 Linux 系统版本
cat /etc/os-release；
# 看内核
uname -a；
# 老系统
lsb_release -a；
```

## 批量替换当前目录下.conf文件中内容
如将内容中的127.0.0.1替换为localhost

```sh
find . -type f -name "*.conf" -exec sed -i 's/127.0.0.1/localhost/g' {} +
```

## 清理日志目录超过1G的日志文件
不删文件只清空

```sh
find /data/app_log -type f -name "*.log" -size +1G -exec truncate -s 0 {} \;
```

## fdupes检测重复文件

```sh
apt install fdupes
fdupes -dN . # 删除重复内容的文件, 只保留一个
```