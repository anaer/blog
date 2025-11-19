# CentOS 7.9 迁移MongoDB 3.0.6

## 安装MongoDB

```sh
$ curl -O https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-3.0.6.tgz
$ tar -zxvf mongodb-linux-x86_64-3.0.6.tgz
$ mv mongodb-linux-x86_64-3.0.6/ /usr/local/mongodb                         # 将解压包拷贝到指定目录
```

MongoDB 的可执行文件位于 bin 目录下，所以可以将其添加到 PATH 路径中：

```sh
vim /etc/profile

export PATH=/usr/local/mongodb/bin:$PATH
```

## 迁移MongoDB
将原MongoDB的数据打包复制到新服务器上

```conf
dbpath=/data/mongodb/data
logpath=/data/mongodb/log/mongod.log
pidfilepath=/data/mongodb/mongod.pid
```

## 添加系统服务

```sh
$ groupadd mongodb
$ useradd -g mongodb mongodb
$ chown -R mongodb:mongodb /data/mongodb

$ vim /etc/systemd/system/mongodb.service
```

```conf
[Unit]
Description=MongoDB Database Server
After=network.target

[Service]
Type=forking
User=mongodb
Group=mongodb
PIDFile=/data/mongodb/mongod.pid
Environment="OPTIONS=-f /data/mongodb/mongod.conf"
ExecStart=/usr/local/mongodb/bin/mongod $OPTIONS
ExecStop=/usr/local/mongodb/bin/mongod --shutdown -f /data/mongodb/conf/mongod.conf
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务

```sh
$ systemctl daemon-reload
$ systemctl enable mongodb.service
$ systemctl restart mongodb
```

## 测试

```sh
$ mongo --host 127.0.0.1 --port 27017 -u user -p pass
```

这里主要讲迁移MongoDB, 如果是全新创建, 需要新增db和用户的 到时再查下.