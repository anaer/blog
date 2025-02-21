
## 查询pem证书有效期

```bash
$ openssl x509 -enddate -noout -in cacert.pem
notAfter=May 29 02:07:58 2021 GMT
```

## 查询p12证书有效期

```bash
$ openssl pkcs12 -in dev.p12 -nokeys -clcerts | openssl x509 -noout -dates
Enter Import Password:
notBefore=Jun 19 05:48:10 2024 GMT
notAfter=Jul 19 05:48:09 2025 GMT
```

### 参数说明
```
pkcs12 -in dev.p12：读取.p12文件。
-nokeys：不输出私钥。
-clcerts：仅输出客户端证书（避免输出CA证书）。
|：将提取的证书传递给x509命令。
-dates：显示证书的有效期。
```

存在密码时 会提示输入密码, 也可以通过添加参数-passin pass:你的密码

```bash
openssl pkcs12 -in dev.p12 -nokeys -clcerts -passin pass:123456 | openssl x509 -noout -dates
```