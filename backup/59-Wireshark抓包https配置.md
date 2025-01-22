
## 抓包https配置

1. 添加环境变量 SSLKEYLOGFILE

SSLKEYLOGFILE = C:\sslkey.log

2. 新打开 chrome 浏览器, 访问任意一个 https 网站, 检查 sslkey 文件生成情况

3. Wireshark 配置

编辑 -> 首选项 -> Protocols -> TLS

(Pre)-Master-Secret log filename -> C:\sslkey.log

4. 抓包验证

## 过滤请求中包含 api 的 POST 请求

http contains api and http.request.method == "POST"

http.request.method == "POST" and http.request.uri contains auth


## 参考链接

过滤参数说明
https://www.wireshark.org/docs/dfref/h/http.html
