vim /etc/fail2ban/jail.d/nginx.conf

```conf
[nginx-cc]
enabled = true
filter = nginx-cc
action = iptables-multiport[name=nginx-cc,port="80,443"]
         bark[name=nginx-cc]
maxretry = 120
findtime = 60s
bantime = 2d
logpath = /var/log/nginx/access.log

[nginx-404]
enabled = true
filter = nginx-404
action = iptables-multiport[name=nginx-404,port="80,443"]
         bark[name=nginx-404]
maxretry = 3
findtime = 60s
bantime = 1d
logpath = /var/log/nginx/access.log

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
action = iptables-multiport[name=nginx-http-auth,port="80,443"]
         bark[name=nginx-http-auth]
logpath = /var/log/nginx/access.log

```

vim /etc/fail2ban/filter.d/nginx-cc.conf

```conf
[Definition]
failregex = <HOST> -.*- .*HTTP/1.* .* .*$
ignoreregex = .*(robots.txt|favicon.ico)
```

vim /etc/fail2ban/filter.d/nginx-404.conf

```conf
[Definition]
failregex = <HOST> -.*- .*HTTP/1.* 404 .*$
ignoreregex = .*(robots.txt|favicon.ico)
```

nginx-http-auth 为自带规则

1.  [9 Ubuntu安装fail2ban](https://anaer.github.io/blog/post/9.html)  
