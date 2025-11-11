# elasticsearch-7.6.2安装

CentOS 7.9

```sh
$ tar xvf elasticsearch-7.6.2.tar.gz -C /data/elasticsearch-7.6.2
```

## 修改config/elasticsearch.yaml文件

```yaml
cluster.name: my-es
node.name: node-1
network.host: 0.0.0.0
http.port: 9200
discovery.seed_hosts: ["0.0.0.0", "[::1]"]
cluster.initial_master_nodes: ["node-1"]
```

## 修改/etc/sysctl.conf文件配置

不修改的话 启动会提示 `max virtual memory areas vm.max_map_count [65530] is too low, increase to at least [262144]`

```sh
$ vim /etc/sysctl.conf
```

```conf
vm.max_map_count = 262144
```

## 启动sysctl配置

```sh
$ sysctl -p
```

## 设置环境变量

```sh
####### elasticsearch ######
export ES_HOME=/data/elasticsearch-7.6.2
export PATH=$PATH:$ES_HOME/bin
```

## 切换用户 

es不能使用root启动 data目录授权

```sh
$ groupadd  es
$ useradd -g es es
$ chown -R es:es /data/elasticsearch-7.6.2
```

## 创建elasticsearch服务

```sh
$ vim /usr/lib/systemd/system/elasticsearch.service
```

```conf
[Unit]
Description=elasticsearch
After=network.target

[Service]
Type=forking
User=es
Group=es
ExecStart=/data/elasticsearch-7.6.2/bin/elasticsearch -d
PrivateTmp=true


# 指定此进程可以打开的最大文件数
LimitNOFILE=65535
# 指定此进程可以打开的最大进程数
LimitNPROC=65535
# 最大虚拟内存
LimitAS=infinity
# 最大文件大小
LimitFSIZE=infinity
# 超时设置 0-永不超时
TimeoutStopSec=0
# SIGTERM是停止java进程的信号
KillSignal=SIGTERM
# 信号只发送给给JVM
KillMode=process
# java进程不会被杀掉
SendSIGKILL=no
# 正常退出状态
SuccessExitStatus=143

[Install]
WantedBy=multi-user.target
```

给脚本赋权限：

```sh
$ chmod +x /usr/lib/systemd/system/elasticsearch.service
```

重新加载systemd的守护线程

```sh
$ sudo systemctl daemon-reload
```

开机启动生效

```sh
$ sudo systemctl enable elasticsearch.service
```

启动elasticsearch.service

```sh
$ sudo systemctl start elasticsearch.service
```

查看elasticsearch.serivce状态

```sh
$ sudo systemctl status elasticsearch.service
```

如果出现错误可以使用如下命令查看日志

```sh
$ sudo journalctl -u elaticsearch.service
```

## 测试es

```sh
$ curl http://127.0.0.1:9200
```

```json
{
  "name" : "node-1",
  "cluster_name" : "my-es",
  "cluster_uuid" : "dDwggAe9RfqyVRAp5s1Wzg",
  "version" : {
    "number" : "7.6.2",
    "build_flavor" : "default",
    "build_type" : "tar",
    "build_hash" : "ef48eb35cf30adf4db14086e8aabd07ef6fb113f",
    "build_date" : "2020-03-26T06:34:37.794943Z",
    "build_snapshot" : false,
    "lucene_version" : "8.4.0",
    "minimum_wire_compatibility_version" : "6.8.0",
    "minimum_index_compatibility_version" : "6.0.0-beta1"
  },
  "tagline" : "You Know, for Search"
}
```
