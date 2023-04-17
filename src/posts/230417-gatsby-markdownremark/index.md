---
title: Gatsby markdownRemark介绍
date: "2023-04-17T17:27:16.000Z"
description: Gatsby markdownRemark介绍
tags:
  - gatsby
last_updated: "2023-04-17T17:27:16.000Z"
---

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
