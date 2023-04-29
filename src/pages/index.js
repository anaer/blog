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
        <p>
          No blog posts found. Add markdown posts to "content/blog" (or the
          directory you specified for the "gatsby-source-filesystem" plugin in
          gatsby-config.js).
        </p>
        <Bio />
      </Layout>
    )
  }

  return (
    <Layout location={location} title={siteTitle}>
      <ol style={{ listStyle: `none` }}>
        {posts.map(post => {
          const title = post.frontmatter.title || post.fields.slug
          const slugify = (tag) => tag.toLowerCase().replace(/\s+/g, "-");
          const tags = post.frontmatter.tags
          const timeAgo = (date) => {
            const now = new Date();
            const diff = now - new Date(date);
            const minute = 60 * 1000;
            const hour = minute * 60;
            const day = hour * 24;
          
            if (diff < minute) {
              const seconds = Math.round(diff / 1000);
              return `${seconds} 秒前`;
            } else if (diff < hour) {
              const minutes = Math.round(diff / minute);
              return `${minutes} 分钟前`;
            } else if (diff < day) {
              const hours = Math.round(diff / hour);
              return `${hours} 小时前`;
            } else {
              const days = Math.round(diff / day);
              return `${days} 天前`;
            }
          }

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
                  <small>
                  {tags && (
                    <span style={{ marginLeft: '5px' }}>
                        {tags.map((tag) => (
                            <span>
                            <Link className="node" to={`/tags/${slugify(tag)}`}>{tag}</Link>&nbsp;&nbsp;
                            </span>
                        ))}
                    </span>
                  )
                  }
                  {timeAgo(post.frontmatter.date)} 
                  </small>
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
      <Bio />
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
    allMarkdownRemark(sort: {
        fields: [frontmatter___last_updated, frontmatter___date],
        order: [DESC, DESC]
      }
    ) {
      nodes {
        excerpt
        fields {
          slug
        }
        frontmatter {
          date(formatString: "YYYY-MM-DD")
          title
          description
          tags
          last_updated(formatString: "YYYY-MM-DD")
        }
      }
    }
  }
`
