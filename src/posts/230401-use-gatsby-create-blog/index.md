---
title: 使用gatsby创建博客
date: "2023-04-01T00:31:37.121Z"
---
## 安装部署

### 安装Gatsby

运行 `npm install -g gatsby-cli` 全局安装Gatsby CLI

### 创建新网站：

运行 `gatsby new blog https://github.com/gatsbyjs/gatsby-starter-blog` 命令。将在当前目录下"blog"目录, 使用的官方博客模板.
运行 `npm install` 安装依赖

目录结构:

```
├── public
├── src
|  ├── components       // 自定义组件
|  ├── images           // 图片目录
|  ├── pages            // 路由页面
|  |   ├── 404.js       // 404页面
|  |   └── index.js     // 首页
|  ├── posts            // 博文
|  ├── templates        // 模板目录
|  |   └── blog-post.js // 帖子页面模板
|  ├── normalize.css    // 样式文件
|  └── style.css
├── static              // 静态资源
├── .gitignore
├── .prettierignore
├── .prettierrc
├── gatsby-browser.js   // 客户端相关配置
├── gatsby-config.js    // 基本配置
├── gatsby-node.js      // Node相关配置
├── gatsby-ssr.js       // 服务端渲染相关配置
├── LICENSE
├── package.json
└── README.md
```

### 预览和编译：
运行 `gatsby develop` 命令启动本地服务。访问 http://localhost:8000 查看网站。

### 发布网站

提交到GitHub, 配置Pages.

链接: https://anaer.github.io/blog/

![](default_blog_site.png)


## 插件

### [gatsby-source-filesystem](https://www.gatsbyjs.com/plugins/gatsby-source-filesystem/)

将数据从本地文件系统导入Gatsby应用

### [gatsby-plugin-offline](https://www.gatsbyjs.com/plugins/gatsby-plugin-offline/)

离线插件

## FAQ

1. node要求18以上

2. 本地启动报错提示: getaddrinfo ENOTFOUND localhost

vim /etc/hosts

```
127.0.0.1 localhost
```

3. libvips安装失败
使用镜像安装, 详情见: https://sharp.pixelplumbing.com/install
```sh
npm_config_sharp_binary_host="https://npmmirror.com/mirrors/sharp" \
  npm_config_sharp_libvips_binary_host="https://npmmirror.com/mirrors/sharp-libvips" \
  npm install sharp
```


## 相关链接

[Gatsby.js 文档](https://www.gatsbyjs.cn/docs/)
[GraphQL 中文](https://graphql.cn/)