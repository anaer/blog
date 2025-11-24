# CentOS 7.9 安装RabbitMQ 3.10.0

编译安装下包太慢, 而且可能存在各种问题, 所以简单点直接yum安装

## 添加yum源

```sh
vim /etc/yum.repos.d/rabbitmq.repo
```

配置中的github地址可能因为XX无法访问, 可以更换为加速地址

```conf
# In /etc/yum.repos.d/rabbitmq.repo

##
## Zero dependency Erlang
##

[rabbitmq_erlang]
name=rabbitmq_erlang
baseurl=https://packagecloud.io/rabbitmq/erlang/el/7/$basearch
repo_gpgcheck=1
gpgcheck=1
enabled=1
# PackageCloud's repository key and RabbitMQ package signing key
gpgkey=https://packagecloud.io/rabbitmq/erlang/gpgkey
       https://github.com/rabbitmq/signing-keys/releases/download/2.0/rabbitmq-release-signing-key.asc
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt
metadata_expire=300

[rabbitmq_erlang-source]
name=rabbitmq_erlang-source
baseurl=https://packagecloud.io/rabbitmq/erlang/el/7/SRPMS
repo_gpgcheck=1
gpgcheck=0
enabled=1
gpgkey=https://packagecloud.io/rabbitmq/erlang/gpgkey
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt
metadata_expire=300

##
## RabbitMQ server
##

[rabbitmq_server]
name=rabbitmq_server
baseurl=https://packagecloud.io/rabbitmq/rabbitmq-server/el/7/$basearch
repo_gpgcheck=1
gpgcheck=1
enabled=1
# PackageCloud's repository key and RabbitMQ package signing key
gpgkey=https://packagecloud.io/rabbitmq/rabbitmq-server/gpgkey
       https://github.com/rabbitmq/signing-keys/releases/download/2.0/rabbitmq-release-signing-key.asc
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt
metadata_expire=300

[rabbitmq_server-source]
name=rabbitmq_server-source
baseurl=https://packagecloud.io/rabbitmq/rabbitmq-server/el/7/SRPMS
repo_gpgcheck=1
gpgcheck=0
enabled=1
gpgkey=https://packagecloud.io/rabbitmq/rabbitmq-server/gpgkey
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt
metadata_expire=300
```

## 更新安装

```sh
$ yum update -y
$ yum install socat logrotate -y
$ yum install erlang rabbitmq-server -y
```

## 启动服务

```sh
systemctl enable rabbitmq-server
systemctl start rabbitmq-server
rabbitmqctl status
```


## 添加用户

```sh
$ rabbitmqctl add_user admin 123456 # 添加用户
$ rabbitmqctl set_user_tags admin administrator # 管理员权限
$ rabbitmqctl set_permissions -p "/" admin '.*' '.*' '.*'  # 设置用户权限
$ rabbitmqctl list_user_permissions admin # 查看用户权限
$ rabbitmqctl delete_user guest # 删除guest用户
$ rabbitmqctl list_users # 查看所有用户
```

## 安装插件

```sh
rabbitmq-plugins enable rabbitmq_management # Web管理
rabbitmq-plugins enable rabbitmq_tracing # 日志
```

## 登录测试
访问服务器IP:15672，使用admin/123456登录管理界面