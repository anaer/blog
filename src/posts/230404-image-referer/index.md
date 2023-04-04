---
title: 图片防盗链解决方案
date: "2023-04-04T15:48:37.121Z"
---

### 添加 meta 标签

给页面添加一个 meta 标签，在 meta 标签里指定 referrer 的值

WHATWG标准:
```html
<meta name="referrer" content="never">
```

MDN标准:
```html
<meta name="referrer" content="no-referrer">
```

### 添加 referrerpolicy 属性

referrerpolicy (MDN：引用头将被完全省略，没有请求信息随请求一起发送。)

```html
<img
  src="https://example.com/image.png"
  referrerpolicy="no-referrer"
/>
```

## 相关链接

[Referrer-Policy 浏览器兼容性](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Headers/Referrer-Policy#%E6%B5%8F%E8%A7%88%E5%99%A8%E5%85%BC%E5%AE%B9%E6%80%A7)