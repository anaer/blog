## 重复请求头处理

在特定的 location 块中添加 proxy_hide_header 指令来隐藏 "Access-Control-Allow-Origin" 头部。该指令会在将响应发送到客户端之前从响应中删除指定的头部。

```conf
proxy_hide_header Access-Control-Allow-Origin;
add_header Access-Control-Allow-Origin "*";
```

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

