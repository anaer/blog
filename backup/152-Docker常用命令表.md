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
