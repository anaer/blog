
## 安装

按行执行以下命令

```sh
sudo apt update && sudo apt install -y curl apt-transport-https gnupg

curl https://couchdb.apache.org/repo/keys.asc | gpg --dearmor | sudo tee /usr/share/keyrings/couchdb-archive-keyring.gpg >/dev/null 2>&1

source /etc/os-release

echo "deb [signed-by=/usr/share/keyrings/couchdb-archive-keyring.gpg] https://apache.jfrog.io/artifactory/couchdb-deb/ ${VERSION_CODENAME} main" | sudo tee /etc/apt/sources.list.d/couchdb.list >/dev/null

sudo apt update
sudo apt install couchdb
```

弹出安装提示:
1. 以单服务器独立模式安装
2. 绑定网络接口 保留默认127.0.0.1
3. 设置管理员密码

## 服务状态
```sh
systemctl status couchdb
systemctl stop couchdb
```

## 检查安装结果

```sh
curl http://127.0.0.1:5984/
```

```json
// 响应结果
{"couchdb":"Welcome","version":"3.4.2","git_sha":"6e5ad2a5c","uuid":"3c1399389c7a4c246449d48ba1990edb","features":["access-ready","partitioned","pluggable-storage-engines","reshard","scheduler"],"vendor":{"name":"The Apache Software Foundation"}}
```

## nginx配置

```conf
  location /cdb {
      proxy_pass http://127.0.0.1:5984/;
  }

```

## Gui管理

默认:  http://127.0.0.1:5984/_utils/

## Moon FM同步配置
1. 需要在CouchDB中创建一个数据库moon_fm
2. 配置Moon FM的同步设置中配置CouchDB地址
```
https://admin:password@xx.xx.xx.xx/cdb/moon_fm
```

![Image](https://github.com/user-attachments/assets/ca99ca40-8091-47ab-a89d-a0df6e9192e9)

## 相关链接

[如何在Ubuntu 20.04安装CouchDB](https://www.myfreax.com/how-to-install-couchdb-on-ubuntu-20-04/)
