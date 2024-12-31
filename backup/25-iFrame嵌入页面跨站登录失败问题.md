## 原因

谷歌浏览器 80.0 及以上版本修改了安全策略，默认 SameSite 策略不允许 cookie 跨站发送，因此单点登录会失败。

## 解决

1. 低版本谷歌 关闭谷歌浏览器的「SameSite by default cookies」选项，重启浏览器
2. 统一域名 保证两个工程的顶级域名、次顶级域名相同，比如 a.b.com 和 c.b.com，「.com」顶级，「b」是次顶级。
3. 安装跨域插件 node cors

