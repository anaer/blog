## 自建PyPI仓库

### pypiserver
最简单、最轻量，适合个人、小团队或快速搭建。只需一个目录存放 .whl / .tar.gz 包。

### Docker部署

1. 准备docker-compose.yml

```yml
version: '3.8'
services:
  pypi-server:
    image: pypiserver/pypiserver:latest          # 官方镜像
    container_name: private-pypi
    ports:
      - "8080:8080"                              # 宿主机端口:容器端口，可改成 80 或其他
    volumes:
      - ./packages:/data/packages                # 存放包的目录（持久化）
      - ./auth:/data/auth                        # 可选：存放密码文件
    command:
      - "-p"
      - "8080"
      - "--authenticate=update"                  # 认证方式：上传update、下载download、列表list
      - "--passwords"
      - "/data/auth/.htpasswd"                   # 如果启用认证
      - "/data/packages"
    restart: always
```

2. 创建目录

```sh
mkdir -p packages auth
```

3. 添加认证

确认是否安装htpasswd, 未安装则安装

```sh
# CentOS
yum install httpd-tools
htpasswd -V
```

```sh
cd auth
# 创建用户 需输入两次密码
htpasswd -B -c .htpasswd username
```

4. 启动服务

```
docker compose up -d
```

5. 验证
访问
http://你的服务器IP:8080/
http://你的服务器IP:8080/simple

6. 上传包
只需要将whl包放到packages目录下，然后访问 http://你的服务器IP:8080/simple ，即可看到上传的包。

### 客户端
1. 客户端下载

```sh
pip install some_package --index-url http://你的服务器IP:8080/simple/ --trusted-host 你的服务器IP
```

2. 配置pip
配置后, 下载时无需指定index-url
```sh
pip config set global.extra-index-url http://你的服务器IP:8080/simple/
pip config set global.trusted-host 你的服务器IP
```

3. 查询服务器包版本
```sh
pip index versions some_package
```

4. 升级包

```sh
pip install -U some_package
```