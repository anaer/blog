## 查询最新版本
https://cdnjs.com/libraries/Primer

字节跳动静态资源公共库
https://cdn.bytedance.com/

## CDN地址

### cdnjs.cloudflare.com 国内可能无法正常访问
https://cdnjs.cloudflare.com/ajax/libs/Primer/21.1.1/primer.css
https://cdnjs.cloudflare.com/ajax/libs/vue/2.6.11/vue.min.js

### 南方科技大学
cdnjs.cloudflare.com -> mirrors.sustech.edu.cn/cdnjs
https://mirrors.sustech.edu.cn/cdnjs/ajax/libs/Primer/21.1.1/primer.css

### 国内加速 
cdnjs.cloudflare.com -> cdnjs.admincdn.com
https://cdnjs.admincdn.com/ajax/libs/Primer/21.1.1/primer.css

### unpkg
https://unpkg.com/vue@2.6.11/dist/vue.min.js

### jsdelivr
unpkg.com -> https://cdn.jsdelivr.net/npm
https://cdn.jsdelivr.net/npm/vue@2.6.11/dist/vue.min.js

### 其他
https://lib.baomitu.com/vue/2.6.11/vue.min.js


## jsdelivr刷新缓存
purge.jsdelivr.net 是一个用于清除 jsDelivr CDN 缓存的服务。jsDelivr是一个开源的公共CDN（内容分发网络），它可以免费为开发人员提供各种开源库和资源的加速和分发。

当您需要刷新或清除jsDelivr CDN上的缓存时，可以使用 purge.jsdelivr.net 服务来执行此操作。通过向 purge.jsdelivr.net 发送 HTTP 请求，您可以告诉jsDelivr将特定文件或文件夹的缓存从其网络中清除。

```sh
curl -k -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4937.0 Safari/537.36" https://purge.jsdelivr.net/gh/anaer/Meow@main/meow.json
```


## 相关链接

1. **[供应链投毒后，我们的选择还剩下哪些？ - LINUX DO](https://linux.do/t/topic/133332)** 
2. **[Polyfill 的供应链攻击，背后的 BootCDN, Staticfile - feizhuqwq](https://blog.feizhuqwq.com/86)**  
3. **[停止使用 staticfile.org 服务 - 流动](https://liudon.com/posts/remove-staticfile.org-from-your-website/)**  
4. **[Polyfill.io、BootCDN、Bootcss 和 Staticfile CDN 可能已被投毒 - yeelz](https://yeelz.com/post/568.html)**  
5. **[BootCDN/Staticfile】CDN供应商被投毒后，应该如何替换 - CSDN](https://blog.csdn.net/m0_59415345/article/details/141496707)**  
6. **[静态文件资源 cdnjs, jsdelivr 抖音字节国内快速 CDN 镜像推荐 - ksh7](https://ksh7.com/posts/cdn-static-file-recommend/index.html)**  
7. **[BootCDN/Staticfile投毒分析 - 吾爱破解](https://www.52pojie.cn/thread-1944970-1-1.html)**  
8. **[茶余饭后-供应链投毒后，我们的选择还剩下哪些？ - 游戏逆向](http://www.yxfzedu.com/article/11052)**  