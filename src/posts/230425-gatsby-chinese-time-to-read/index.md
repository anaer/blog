---
title: Gatsby添加中文阅读时间
date: "2023-04-25T11:16:30.000Z"
description: Gatsby添加中文阅读时间
tags:
  - gatsby
last_updated: "2023-04-25T11:16:30.000Z"
---

## 1. 在gatsby-node.js中, 添加中文阅读时间计算

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

## 2. 在blog-post.js模板中, 添加展示中文阅读时间

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