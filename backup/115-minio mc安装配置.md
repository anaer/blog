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

## mc命令


| **分类**       | **命令**               | **功能说明**                                                 | **示例**                                                                        |
| -------------- | ---------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| **配置管理**   | `mc alias`             | 添加/管理云存储服务别名                                      | `mc alias set myminio http://localhost:9000 ACCESS_KEY SECRET_KEY`              |
| **配置管理**   | `mc config host list`  | 列出所有已配置的别名                                         | `mc config host list`                                                           |
| **存储桶操作** | `mc mb`                | 创建存储桶                                                   | `mc mb myminio/mybucket`                                                        |
| **存储桶操作** | `mc ls`                | 列出存储桶或对象（支持 `--recursive` 递归）                  | `mc ls myminio/mybucket/docs/`                                                  |
| **存储桶操作** | `mc rb`                | 删除空存储桶                                                 | `mc rb myminio/mybucket`                                                        |
| **存储桶操作** | `mc du`                | 显示存储桶/目录占用空间                                      | `mc du myminio/mybucket --recursive`                                            |
| **存储桶操作** | `mc mirror`            | 同步本地目录到存储桶                                         | `mc mirror ./local_dir myminio/mybucket`                                        |
| **对象操作**   | `mc cp`                | 上传/下载文件或目录                                          | `mc cp file.txt myminio/mybucket/docs/`<br>`mc cp myminio/mybucket/file.txt ./` |
| **对象操作**   | `mc mv`                | 移动对象                                                     | `mc mv myminio/mybucket/old.txt myminio/mybucket/new.txt`                       |
| **对象操作**   | `mc rm`                | 删除对象（支持 `--recursive` 递归）                          | `mc rm myminio/mybucket/temp --recursive`                                       |
| **对象操作**   | `mc stat`              | 查看对象详细信息                                             | `mc stat myminio/mybucket/file.zip`                                             |
| **对象操作**   | `mc cat`               | 直接输出对象内容到控制台                                     | `mc cat myminio/mybucket/logs/app.log`                                          |
| **对象操作**   | `mc diff`              | 比较两个存储桶/目录内容差异                                  | `mc diff myminio/mybucket myminio/anotherbucket`                                |
| **权限管理**   | `mc policy`            | 设置存储桶访问策略（`none`, `download`, `upload`, `public`） | `mc policy set public myminio/mybucket`                                         |
| **权限管理**   | `mc admin policy`      | 管理用户权限策略（需管理员权限）                             | `mc admin policy create myminio mypolicy policy.json`                           |
| **权限管理**   | `mc admin user`        | 管理用户（添加/删除/启用/禁用）                              | `mc admin user add myminio newuser newpassword`                                 |
| **分享与访问** | `mc share download`    | 生成文件临时下载链接（默认7天有效期）                        | `mc share download myminio/mybucket/file.pdf --expire=72h`                      |
| **分享与访问** | `mc share upload`      | 生成文件上传链接                                             | `mc share upload myminio/mybucket/ --expire=24h`                                |
| **运维与监控** | `mc admin info`        | 显示服务器健康状态                                           | `mc admin info myminio`                                                         |
| **运维与监控** | `mc admin server info` | 查看单个节点详细信息                                         | `mc admin server info myminio/`                                                 |
| **运维与监控** | `mc support diag`      | 生成诊断报告                                                 | `mc support diag myminio`                                                       |
| **运维与监控** | `mc watch`             | 实时监控存储桶事件                                           | `mc watch myminio/mybucket`                                                     |
| **其他实用**   | `mc find`              | 根据条件查找文件（名称、大小、时间等）                       | `mc find myminio/mybucket --name "*.log" --size "+10MB"`                        |
| **其他实用**   | `mc sql`               | 使用 SQL 查询对象数据（需配置）                              | `mc sql myminio/mybucket "SELECT * FROM S3Object"`                              |
| **其他实用**   | `mc encrypt`           | 配置存储桶加密                                               | `mc encrypt set sse-s3 myminio/mybucket`                                        |

## 相关文档
1. [minio sdk](https://min.io/docs/minio/linux/developers/minio-drivers.html)