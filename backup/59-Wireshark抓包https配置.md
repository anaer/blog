
## 抓包https配置

1. 添加环境变量 SSLKEYLOGFILE

SSLKEYLOGFILE = C:\sslkey.log

2. 新打开 chrome 浏览器, 访问任意一个 https 网站, 检查 sslkey 文件生成情况

3. Wireshark 配置

编辑 -> 首选项 -> Protocols -> TLS

(Pre)-Master-Secret log filename -> C:\sslkey.log

4. 抓包验证

## 过滤器

| 过滤器语法                                                       | 描述                                                             |
| ---------------------------------------------------------------- | ---------------------------------------------------------------- |
| `frame.number <= 1000`                                           | 显示前1000个数据包。                                             |
| `frame.number >= 10 and frame.number <= 20`                      | 显示序列号10-20内的数据包。                                      |
| `http contains api and http.request.method == "POST"`            | 过滤包含api的POST请求。                                          |
| `http.content_encoding == "gzip"`                                | 过滤content_encoding是gzip的HTTP包。                             |
| `http.content_length == 279`                                     | 根据content_length的数值过滤。                                   |
| `http.content_length_header == "279"`                            | 根据content_length的数值过滤。                                   |
| `http.content_type == "text/html"`                               | 过滤content_type是text/html的HTTP响应、POST包。                  |
| `http.cookie contains guid`                                      | 过滤含有指定cookie的HTTP数据包。                                 |
| `http.host == "www.google.cn"`                                   | 只显示访问指定域名（www.google.cn）的HTTP请求数据包。            |
| `http.host contains "google"`                                    | 只显示访问包含指定字符串（google）的域名的HTTP请求数据包。       |
| `http.referer == "http://www.google.cn/"`                        | 只显示Referer头部内容为“http://www.google.cn/”的HTTP请求数据包。 |
| `http.request and not http.request.method == GET`                | 显示所有HTTP数据包，但不包含GET方法的HTTP请求数据包。            |
| `http.request.full_uri=="http://www.google.cn/demo"`             | 过滤含域名的整个URL。                                            |
| `http.request.method == POST and http.request.uri contains auth` | 过滤POST请求中包含auth的URI。                                    |
| `http.request.method == POST`                                    | 过滤所有请求方式为POST的HTTP请求包。                             |
| `http.request.uri=="/demo"`                                      | 过滤请求的URI，取值是域名后的部分。                              |
| `http.request.version == "HTTP/1.1"`                             | 过滤HTTP/1.1版本的HTTP包，包括请求和响应。                       |
| `http.request`                                                   | 显示所有HTTP请求数据包。                                         |
| `http.response.code <= 599`                                      | 只显示包含HTTP服务器端错误状态码的HTTP响应数据包。               |
| `http.response.code == 200`                                      | 只显示状态码为200的HTTP响应数据包。                              |
| `http.response.code >= 400 and http.response.code <= 499`        | 只显示包含HTTP客户端错误状态码的HTTP响应数据包。                 |
| `http.response.phrase == "OK"`                                   | 过滤HTTP响应中的phrase。                                         |
| `http.response`                                                  | 显示所有HTTP响应数据包。                                         |
| `http.server contains "nginx"`                                   | 过滤HTTP头中server字段含有nginx字符的数据包。                    |
| `http.server`                                                    | 过滤所有含有HTTP头中含有server字段的数据包。                     |
| `http.transfer_encoding == "chunked"`                            | 根据transfer_encoding过滤。                                      |

## 参考链接

过滤参数说明
https://www.wireshark.org/docs/dfref/h/http.html
