---
title: gatsby添加标签支持
date: "2023-04-04T20:06:37.121Z"
tags:
  - gatsby
---

## 1. 安装gatsby-plugin-tags

```
npm install gatsby-plugin-tags
```

## 2. 配置插件

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

## 3. 添加标签页模板
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

## 4. 在首页列表中展示标签信息

```javascript
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

## 5. 添加样式
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