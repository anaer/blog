这是之前blog使用的框架, 现在没在用了, 这里仅做留痕.

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
|  ├── components        // 自定义组件
|  ├── images            // 图片目录
|  ├── pages             // 路由页面
|  |   ├── 404.js        // 404页面
|  |   └── index.js      // 首页
|  ├── posts             // 博文
|  ├── templates         // 模板目录
|  |   └── blog-post.js  // 帖子页面模板
|  └── styles            // 样式文件目录
|      ├── normalize.css // 样式文件
|      └── style.css
├── static               // 静态资源
├── .gitignore
├── .prettierignore
├── .prettierrc
├── gatsby-browser.js    // 客户端相关配置
├── gatsby-config.js     // 基本配置
├── gatsby-node.js       // Node相关配置
├── gatsby-ssr.js        // 服务端渲染相关配置
├── LICENSE
├── package.json
└── README.md
```

### 预览和编译：
运行 `gatsby develop` 命令启动本地服务。访问 http://localhost:8000 查看网站。

### 发布网站

提交到GitHub, 配置Pages.

链接: https://anaer.github.io/blog/

![](../.images/default_blog_site.png)


### 插件

* [gatsby-source-filesystem](https://www.gatsbyjs.com/plugins/gatsby-source-filesystem/)

将数据从本地文件系统导入Gatsby应用

* [gatsby-plugin-offline](https://www.gatsbyjs.com/plugins/gatsby-plugin-offline/)

离线插件

### FAQ

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


### 相关链接

[Gatsby.js 文档](https://www.gatsbyjs.cn/docs/)
[GraphQL 中文](https://graphql.cn/)


## PLUGIN: 添加标签支持

### 1. 安装gatsby-plugin-tags

```
npm install gatsby-plugin-tags
```

### 2. 配置插件

```javascript
// gatsby-config.js
module.exports = {
  plugins: [
    {
      resolve: `gatsby-plugin-tags`,
      options: {
        templatePath: `${__dirname}/src/templates/tags.js`, // 标签页模板路径
        contentPath: `${__dirname}/src/posts`, // 数据源路径
        slugify: (tag) => tag.toLowerCase().replace(/\s+/g, "-"), // 自定义 slug 生成函数
        useTagsInPath: true, // 是否为标签页添加前缀路由
        postTypes: ["MarkdownRemark"], // 数据源类型
        args: { limit: 1000 }, // 数据源查询参数
      },
    },
  ],
};
```

### 3. 添加标签页模板
使用 graphql 查询获取标签数据和相关内容，并进行展示：

```javascript
// src/templates/tags.js
import React from "react";
import { Link, graphql } from "gatsby";

import Layout from "../components/layout"

const TagsTemplate = ({ pageContext, data, location }) => {
  const { tag } = pageContext;
  const { edges, totalCount } = data.allMarkdownRemark;
  const siteTitle = data.site.siteMetadata?.title || `Title`

  return (
    <Layout location={location} title={siteTitle}>
      <div>
        <h1>Tag: {tag}</h1>
        <p>{totalCount} posts</p>
        <ul>
          {edges.map(({ node }) => (
            <li key={node.fields.slug}>
              <Link to={node.fields.slug}>{node.frontmatter.title}</Link>
            </li>
          ))}
        </ul>
      </div>
      <hr />
      <footer>
      </footer>
    </Layout>
  );
};

export const query = graphql`
  query($tag: String!) {
    site {
      siteMetadata {
        title
      }
    }
    allMarkdownRemark(
      limit: 1000
      sort: { frontmatter: { date: DESC } }
      filter: { frontmatter: { tags: { in: [$tag] } } }
    ) {
      totalCount
      edges {
        node {
          fields {
            slug
          }
          frontmatter {
            title
            date(formatString: "DD MMMM, YYYY")
          }
        }
      }
    }
  }
`;

export default TagsTemplate;
```

### 4. 在首页列表中展示标签信息

```ts
import * as React from "react"
import { Link, graphql } from "gatsby"

import Bio from "../components/bio"
import Layout from "../components/layout"
import Seo from "../components/seo"

const BlogIndex = ({ data, location }) => {
  const siteTitle = data.site.siteMetadata?.title || `Title`
  const posts = data.allMarkdownRemark.nodes


  if (posts.length === 0) {
    return (
      <Layout location={location} title={siteTitle}>
        <Bio />
        <p>
          No blog posts found. Add markdown posts to "content/blog" (or the
          directory you specified for the "gatsby-source-filesystem" plugin in
          gatsby-config.js).
        </p>
      </Layout>
    )
  }

  return (
    <Layout location={location} title={siteTitle}>
      <Bio />
      <ol style={{ listStyle: `none` }}>
        {posts.map(post => {
          const title = post.frontmatter.title || post.fields.slug
          const slugify = (tag) => tag.toLowerCase().replace(/\s+/g, "-");
          const tags = post.frontmatter.tags

          return (
            <li key={post.fields.slug}>
              <article
                className="post-list-item"
                itemScope
                itemType="http://schema.org/Article"
              >
                <header>
                  <h2>
                    <Link to={post.fields.slug} itemProp="url">
                      <span itemProp="headline">{title}</span>
                    </Link>
                  </h2>
                  <small class='left-element'>{post.frontmatter.date}</small>
                  {tags && (
                    <div class='right-element'>
                      <ul >
                        {tags.map((tag) => (
                          <li key={tag}>
                            <Link to={`/tags/${slugify(tag)}`}>{tag}</Link>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </header>
                <section>
                  <p
                    dangerouslySetInnerHTML={{
                      __html: post.frontmatter.description || post.excerpt,
                    }}
                    itemProp="description"
                  />
                </section>
              </article>
            </li>
          )
        })}
      </ol>
    </Layout>
  )
}

export default BlogIndex

/**
 * Head export to define metadata for the page
 *
 * See: https://www.gatsbyjs.com/docs/reference/built-in-components/gatsby-head/
 */
export const Head = () => <Seo title="All posts" />

export const pageQuery = graphql`
  {
    site {
      siteMetadata {
        title
      }
    }
    allMarkdownRemark(sort: { frontmatter: { date: DESC } }) {
      nodes {
        excerpt
        fields {
          slug
        }
        frontmatter {
          date(formatString: "MMMM DD, YYYY")
          title
          description
          tags
        }
      }
    }
  }
`
```

### 5. 添加样式
将标签和时间展示在同一行

```css
.left-element,
.right-element {
  display: inline-block;
  font-size: 16px;
  vertical-align: top;
  width: 50%; /* 每个元素占据宽度的50% */
}

/* 列表不展示圆点 */
.right-element > ul {
  list-style-type: none;
}
```

## PLUGIN: 添加toc

### package.json

```json
    "gatsby-remark-table-of-contents": "^2.0.0",
    "gatsby-remark-autolink-headers": "^6.9.0",
```

`npm install`安装插件

### gatsby-config.js

在`gatsby-transformer-remark`配置项中添加plugins配置`gatsby-remark-table-of-contents`, `gatsby-remark-autolink-headers`
添加位置在`gatsby-remark-prismjs`之前

```js
    {
      resolve: `gatsby-transformer-remark`,
      options: {
        plugins: [
          {
            resolve: `gatsby-remark-table-of-contents`,
            options: {
              exclude: "Table of Contents",
              tight: false,
              ordered: false,
              fromHeading: 1,
              toHeading: 6,
              className: "table-of-contents"
            },
          },
          `gatsby-remark-autolink-headers`,
          `gatsby-remark-prismjs`,
        ],
      },
    }
```

## 使用方式

### 相关链接

[npm gatsby-remark-table-of-contents](https://npmmirror.com/package/gatsby-remark-table-of-contents)
[gatsby-remark-autolink-headers](https://npmmirror.com/package/gatsby-remark-autolink-headers)

## FEATURE: 添加中文阅读时间


### 1. 在gatsby-node.js中, 添加中文阅读时间计算

```js
function chineseTimeToRead(content) {
  const wordsPerMinute = 300 // 假设中文阅读速度为每分钟300字
  const chineseCharacters = content.replace(/[^\u4e00-\u9fa5]/gi, '') //只保留中文字符
  const chineseCharactersCount = chineseCharacters.length
  const timeInMinutes = chineseCharactersCount / wordsPerMinute
  return Math.ceil(timeInMinutes)
}

// 在 gatsby-node.js 文件中添加 chineseTimeToRead 函数
// PS: createNodeField可以多次调用以便添加其他字段, 如slug等
exports.onCreateNode = ({ node, actions }) => {
  const { createNodeField } = actions
  if (node.internal.type === `MarkdownRemark`) {
    const content = node.rawMarkdownBody
    const chineseTime = chineseTimeToRead(content)
    createNodeField({
      node,
      name: `chineseTimeToRead`,
      value: chineseTime
    })
  }
}
```

### 2. 在blog-post.js模板中, 添加展示中文阅读时间

```js
// 在需要显示阅读时间的地方使用 node.fields.chineseTimeToRead
// post.timeToRead 英文阅读时间
// post.fields.chineseTimeToRead 中文阅读时间
import React from "react"
import { graphql } from "gatsby"

export default ({ data }) => {
  const post = data.markdownRemark
  return (
    <div>
      <h1>{post.frontmatter.title}</h1>
      <p>阅读时间: {post.timeToRead + post.fields.chineseTimeToRead} 分钟</p>
      <div dangerouslySetInnerHTML={{ __html: post.html }} />
    </div>
  )
}

export const query = graphql`
  query($slug: String!) {
    markdownRemark(fields: { slug: { eq: $slug } }) {
      html
      timeToRead
      frontmatter {
        title
      }
      fields {
        chineseTimeToRead
      }
    }
  }
`
```


## 介绍: markdownRemark


`markdownRemark` 是 Gatsby.js 中 Markdown 文件的节点类型，在查询 Markdown 文件时可以使用它来获取文件的各种信息。以下是 `markdownRemark` 节点类型中常用的字段列表：

- `id`: 节点 ID，是唯一标识一个 Markdown 文件节点的字符串。
- `frontmatter`: 前置元数据，是 Markdown 文件头部的 YAML 格式内容，可以包含一些元信息，例如标题、日期、作者等。前置元数据的具体内容可以在查询时指定，例如 `frontmatter { title, date }`。
- `excerpt`: 摘要内容，是基于 Markdown 文件生成的摘要，可以在页面中用于描述文章概要或列表中的摘要展示。摘要的长度和内容可以在查询时指定，例如 `excerpt(pruneLength: 100)` 表示获取摘要内容并将其截断到 100 个字符以内。
- `excerptAst`: 摘要的抽象语法树（AST），可以用于处理和操作摘要的节点结构。
- `html`: 渲染后的 HTML 内容，是将 Markdown 格式解析为 HTML 格式后的结果。可以直接将其用于渲染文章内容。
- `htmlAst`: HTML 内容的抽象语法树（AST），可以用于处理和操作文章内容的节点结构。
- `timeToRead`: 预估的阅读时间，是一个大概的时间估计值，以分钟为单位。
- `wordCount`: 字数统计信息，包括 `paragraphs`（段落数）、`sentences`（句子数）和 `words`（单词数）三个字段。

这些字段可以在 GraphQL 查询语句中使用，以获取指定 Markdown 文件的相应信息。
例如，以下查询语句返回了 `slug` 值为 "/hello-world/" 的 Markdown 文件节点的 `frontmatter`、`excerpt` 和 `timeToRead` 字段：

```graphql
query {
  markdownRemark(frontmatter: { slug: { eq: "/hello-world/" } }) {
    frontmatter {
      title
      date
    }
    excerpt(pruneLength: 100)
    timeToRead
  }
}
```

## 介绍: 日期格式

| 日期格式                 | 例子                     |
| ------------------------ | ------------------------ |
| MMMM DD, YYYY            | January 01, 2022         |
| MMM DD, YYYY             | Jan 01, 2022             |
| MM/DD/YYYY               | 01/01/2022               |
| DD/MM/YYYY               | 01/01/2022               |
| YYYY-MM-DD               | 2022-01-01               |
| YYYY-MM-DDTHH:mm:ss.sssZ | 2022-01-01T12:00:00.000Z |
| ddd MMM DD HH:mm:ss YYYY | Sat Jan 01 12:00:00 2022 |
