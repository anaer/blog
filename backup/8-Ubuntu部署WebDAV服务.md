0. 系统环境

系统: Ubuntu 20.04.6

1. 安装nginx

`apt-get install nginx-full` 安装full版

2. 创建webdav目录

```bash
mkdir /var/www/webdav
chown -R www-data:www-data /var/www/webdav
```

3. 配置nginx

`vim /etc/nginx/sites-available/default`

在 `server` 块内添加以下配置:
```bash
location /webdav {
    # 指定webdav的根目录
    root /var/www/;
    # dav允许的操作
    dav_methods PUT DELETE MKCOL COPY MOVE;
    dav_ext_methods PROPFIND OPTIONS;
    # 允许自动创建文件夹
    create_full_put_path on;
    # 创建文件的默认权限
    dav_access user:rw group:rw all:r;
    # 用户密码文件
    auth_basic "WebDAV";
    auth_basic_user_file /etc/nginx/.htpasswd;
    # 临时文件位置
    client_body_temp_path /tmp;
    # 开启目录浏览功能, 如果未开启 访问会提示`403 Forbidden`
    autoindex on;
    # 文件大小限制1G
    client_max_body_size 1G;
}
```

4. 用户认证

创建用户username, 根据提示输入密码并确认.

```bash
apt-get install apache2-utils
htpasswd -c /etc/nginx/.htpasswd username
```

5. 启动服务

```bash
nginx -t # 检查配置
nginx -s reload # 重载配置
```


6. 访问服务

`http://xxx.xxx.xxx.xxx/webdav`


## 相关链接
[htpasswd命令介绍](https://ipcmen.com/htpasswd)