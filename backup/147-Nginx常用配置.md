## 配置txt校验文件

```conf
location ~ ^/.*txt$ {
       root /var/www/txt/;
}
```

```log
/var/www/txt/.well-known/pki-validation/xxx.txt
http://myecs/.well-known/pki-validation/xxx.txt
```

