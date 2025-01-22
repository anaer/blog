
地址: https://github.com/DXY-F2E/api-mocker

## 启动命令

```
source ~/nvm/nvm.sh
nvm use v8.15.0

mongod --bind_ip 127.0.0.1 --fork --dbpath ./db/ --logpath ./db/mongod.log
make prod_client
make prod_server
```

## 修改用户密码

```sh
mongo --port 27017 --host 127.0.0.1

show dbs

use api-mock

show collections

// 查询用户
db.users.find({email: 'a@b.com'})

// 修改密码
// 123456 -> 890e5ea426292d095a0843886a21bcb0
db.users.update({'email':'a@b.com'},{'$set':{'password':'890e5ea426292d095a0843886a21bcb0'}},upsert=true,multi=false)
```

```json
// 用户数据示例
{ "_id" : ObjectId("6111da18038317083608181f"), "email" : "a@b.com", "password" : "f19b112ebe36ec9429d4c31cdd2f473c", "name" : "ablet", "isDeleted" : false, "modifiedTime" : ISODate("2021-08-10T01:44:56.138Z"), "createTime" : ISODate("2021-08-10T01:44:56.138Z"), "teamId" : [ ], "__v" : 0 }
```
