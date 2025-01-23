
记录访问的 log，为了在出现特殊情况时，方便检查出现问题的地方。

## 配置示例

```conf
log_format access '$remote_addr - $remote_user [$time_local] "$request" '
                  '$status $body_bytes_sent "$http_referer" '
                  '"$http_user_agent" $http_x_forwarded_for';
access_log /var/log/nginx_access.log access;


# 拼成json格式
log_format main escape=json '{ "@timestamp": "$time_iso8601", '
                    '"remote_addr": "$remote_addr",'
                    '"costtime": "$request_time",'
                    '"realtime": "$upstream_response_time",'
                    '"status": $status,'
                    '"x_forwarded": "$http_x_forwarded_for",'
                    '"referer": "$http_referer",'
                    '"request": "$request",'
                    '"upstr_addr": "$upstream_addr",'
                    '"bytes":$body_bytes_sent,'
                    '"dm":$request_body,'
                    '"agent": "$http_user_agent" }';


# escape=json 不转义的话, $request_body 会有\x22字符
log_format main escape=json '$remote_addr - $remote_user [$time_local] $request '
                    '$status $request_time "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"'
                    '$request_body'
                    '\n';

```

## 参数列表

```conf
$arg_PARAMETER           这个变量包含在查询字符串时GET请求PARAMETER的值。
$args                    这个变量等于请求行中的参数。
$binary_remote_addr      二进制码形式的客户端地址。
$body_bytes_sent         请求体字节数
$content_length          请求头中的 Content-length 字段。
$content_type            请求头中的 Content-Type 字段。
$cookie_COOKIE           cookie COOKIE的值。
$document_root           当前请求在 root 指令中指定的值。
$document_uri            与$uri 相同。
$host                    请求中的主机头字段，如果请求中的主机头不可用，则为服务器处理请求的服务器名称。
$is_args                 如果$args设置，值为"?"，否则为""。
$limit_rate              这个变量可以限制连接速率。
$nginx_version           当前运行的nginx版本号。
$query_string            与$args相同。
$remote_addr             客户端的 IP 地址。
$remote_port             客户端的端口。
$remote_user             已经经过 Auth Basic Module 验证的用户名。

$request                 请求行 (包括方法、路径、协议版本)。
$request_filename        当前连接请求的文件路径，由root或alias指令与URI请求生成。
$request_body            这个变量（0.7.58+）包含请求的主要信息。在使用 proxy_pass 或 fastcgi_pass 指令的 location 中比较有意义。
$request_body_file       客户端请求主体信息的临时文件名。
$request_completion      请求完成
$request_method          这个变量是客户端请求的动作，通常为GET或POST。包括0.8.20及之前的版本中，这个变量总为main request中的动作，如果当前请求是一个子请求，并不使用这个当前请求的动作。
$request_uri             这个变量等于包含一些客户端请求参数的原始 URI，它无法修改，请查看$uri更改或重写URI。
$request_time            整个请求的总时间
$upstream_response_time  请求过程中, upstream响应时间

$scheme                  HTTP 方法（如 http，https）。按需使用，例： rewrite ^(.+)$ $scheme://example.com$1 redirect;
$server_addr             服务器地址，在完成一次系统调用后可以确定这个值，如果要绕开系统调用，则必须在listen中指定地址并且使用bind参数。
$server_name             服务器名称。
$server_port             请求到达服务器的端口号。
$server_protocol         请求使用的协议，通常是 HTTP/1.0 或 HTTP/1.1。
$uri                     请求中的当前URI(不带请求参数，参数位于$args)，可以不同于浏览器传递的$request_uri 的值，它可以通过内部重定向，或者使用 index 指令进行修改。

$status                  请求的HTTP状态码，如200、404等。
$http_referer            客户端请求的来源，如果没有，则为空。
$http_user_agent         客户端的浏览器信息，如果没有，则为空。
$http_x_forwarded_for    客户端的IP地址，如果没有，则为空。
$http_Authorization      请求头Authorization，如果没有，则为空。
$http_HEADER             请求头HEADER, 如上

$time_iso8601            生成格式：2023-06-28T17:09:30+08:00
$time_local              生成格式：28/Jun/2023:17:09:30 +0800
```
