## 安装配置
```sh
mkdir -p /data/minio/data

docker run \
   -p 9900:9000 \
   -p 9901:9001 \
   --name minio \
   -v /data/minio/data:/data \
   -e "MINIO_ROOT_USER=minio" \
   -e "MINIO_ROOT_PASSWORD=minio123" \
   quay.io/minio/minio server /data --console-address ":9001"
   
 9901: 控制台
 9900: 服务ip


mc alias set oss https://oss-cn-shanghai.aliyuncs.com/ ACCESS_KEY ACCESS_SECRET

mc alias set myminio http://127.0.0.1:9900 ACCESS_KEY ACCESS_SECRET

mc mirror oss/my-oss-bucket/ myminio/my-minio-bucket/

mc --debug mirror --watch myminio/my-minio-bucket/ oss/my-oss-bucket/ 

PS: 貌似--watch的源服务只支持本地文件或者minio服务, 不支持oss, 所以自动sync, 可能需要结合crontab

mc mirror \
  --overwrite \            # 覆盖目标已有文件
  --remove \               # 删除目标端多余文件（保持完全同步）
  --exclude "*.tmp" \      # 排除特定文件（如临时文件）
  --watch \                # 监听文件变化持续同步
  oss/my-oss-bucket/ myminio/my-minio-bucket/


Public库: http://127.0.0.1:9900/my-minio-bucket/path/xxx/name.jpeg
Private库: 需要获取签名链接
http://127.0.0.1:9900/my-minio-bucket/path/xxx/name.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=z8ETVdfI8spMeEhKXngv%2F20250427%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20250427T081624Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=69203ea0b2278062e2fdc67cc6fd82b4c172676a04f2b066c61f8a5eb0fb6cf8

```

## minio防盗链

1. 存储桶配置私有Private模式
2. 添加nginx反代, 添加白名单配置

## minio同步脚本
minio_sync.sh

```sh
#!/bin/bash

# 定义锁文件路径
LOCKFILE=/tmp/minio_sync.lock

# 检查锁文件是否存在
if [ -e "$LOCKFILE" ]; then
  echo "minio sync is already running. Exiting."
  exit 1
fi

# 创建锁文件
touch "$LOCKFILE"

# 捕获脚本退出信号，删除锁文件
trap 'rm -f "$LOCKFILE"; exit' INT TERM EXIT

# 你的任务逻辑
echo "Running task at $(date)" >> /data/minio/minio_sync.log
# 其他任务命令...
/usr/local/bin/mc mirror oss/my-oss-bucket/ myminio/my-minio-bucket/

# 任务完成后，锁文件会在 trap 中自动删除

```

`crontab -e`
```
* * * * * sh /data/minio/minio_sync.sh >> /data/minio/minio_sync.log 2>&1
```


```log
Running task at Mon Apr 28 10:13:02 CST 2025
┌───────┬─────────────┬──────────┬───────┐
│ Total │ Transferred │ Duration │ Speed │
│ 0 B   │ 0 B         │ 00m00s   │ 0 B/s │
└───────┴─────────────┴──────────┴───────┘
```