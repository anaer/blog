## 查询最新版本
https://cdnjs.com/libraries/Primer

字节跳动静态资源公共库
https://cdn.bytedance.com/

## CDN地址

### 南方科技大学
https://mirrors.sustech.edu.cn/cdnjs/ajax/libs/Primer/21.1.1/primer.css

### cdnjs.cloudflare.com 国内可能无法正常访问
https://cdnjs.cloudflare.com/ajax/libs/Primer/21.1.1/primer.css

### 国内加速 cdnjs.cloudflare.com -> cdnjs.admincdn.com
https://cdnjs.admincdn.com/ajax/libs/Primer/21.1.1/primer.css

## jsdelivr刷新缓存
purge.jsdelivr.net 是一个用于清除 jsDelivr CDN 缓存的服务。jsDelivr是一个开源的公共CDN（内容分发网络），它可以免费为开发人员提供各种开源库和资源的加速和分发。

当您需要刷新或清除jsDelivr CDN上的缓存时，可以使用 purge.jsdelivr.net 服务来执行此操作。通过向 purge.jsdelivr.net 发送 HTTP 请求，您可以告诉jsDelivr将特定文件或文件夹的缓存从其网络中清除。

```sh
curl -k -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4937.0 Safari/537.36" https://purge.jsdelivr.net/gh/anaer/Meow@main/meow.json
```
