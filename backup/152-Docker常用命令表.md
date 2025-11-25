## Docker常用命令表

| 命令                   | 说明                           | 示例                                      |
|------------------------|--------------------------------|-------------------------------------------|
| docker run             | 运行一个容器                   | docker run ubuntu                         |
| docker ps              | 列出正在运行的容器             | docker ps                                 |
| docker images          | 查看本地镜像列表               | docker images                             |
| docker pull            | 下载镜像                       | docker pull nginx                         |
| docker stop            | 停止容器                       | docker stop mycontainer                   |
| docker rm              | 删除容器                       | docker rm mycontainer                     |
| docker rmi             | 删除镜像                       | docker rmi nginx                          |
| docker build           | 构建镜像                       | docker build -t myimage .                 |
| docker exec            | 在容器中执行命令               | docker exec mycontainer ls                |
| docker logs            | 查看容器日志                   | docker logs mycontainer                   |
| docker inspect         | 查看详细信息                   | docker inspect mycontainer                |
| docker cp              | 文件拷贝（容器与主机间）       | docker cp mycontainer:/tmp/a.txt ./a.txt  |
| docker stats           | 查看资源使用                   | docker stats mycontainer                  |
| docker attach          | 连接到正在运行的容器           | docker attach mycontainer                 |
| docker top             | 查看容器进程                   | docker top mycontainer                    |
| docker commit          | 用容器生成新镜像               | docker commit mycontainer newimage        |
| docker system prune    | 清理无用资源                   | docker system prune                       |
| docker version         | 查看Docker版本                 | docker version                            |
| docker network ls      | 查看docker网络                 | docker network ls                         |
| docker network create  | 创建网络                       | docker network create mynet               |
| docker network connect | 容器加入网络                   | docker network connect mynet mycontainer  |
| docker volume ls       | 查看所有卷                     | docker volume ls                          |
| docker volume create   | 创建卷                         | docker volume create datavol              |
| docker volume rm       | 删除卷                         | docker volume rm datavol                  |
| docker-compose up      | 启动Compose项目                | docker-compose up                         |
| docker-compose down    | 停止并移除Compose项目          | docker-compose down                       |


## Docker镜像

[DockerHub国内镜像列表](https://github.com/dongyubin/DockerHub)

[国内 Docker 服务状态 & 镜像加速监控](https://status.1panel.top/status/docker)


## Docker镜像源检测

```sh
#!/bin/bash

# 设置要检测的镜像源列表
REGISTRIES=(
    "docker.io"                       # Docker 官方源
    "docker.1ms.run"
    "docker.m.daocloud.io"
    #"docker.ketches.cn"
    #"hub1.nat.tf"
    #"hub2.nat.tf"
    #"registry.cn-hangzhou.aliyuncs.com"  # 阿里云镜像源
    #"hub-mirror.c.163.com"              # 网易云镜像源
    #"mirror.huaweicloud.com"            # 华为云镜像源
    #"registry.docker-cn.com"            # Docker 官方中国镜像
)

# 检测镜像源是否可用
function check_registry() {
    local registry=$1
    echo "正在检测镜像源: ${registry} ..."

    # 使用 docker pull 拉取一个小镜像（如 hello-world）来检测源的可用性
    if docker pull "${registry}/hello-world" &>/dev/null; then
        echo "镜像源 ${registry} 可用"
    else
        echo "镜像源 ${registry} 不可用"
    fi
}

# 批量检测多个镜像源
function check_all_registries() {
    for registry in "${REGISTRIES[@]}"; do
        check_registry $registry
    done
}

# 执行批量检测
check_all_registries

```