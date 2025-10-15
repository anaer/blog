## Chrome Network面板过滤器


---

### 常见过滤键

| 过滤键                   | 示例                                           | 说明                                |
| ------------------------ | ---------------------------------------------- | ----------------------------------- |
| **method:**              | `method:GET` `method:POST`                     | 按 HTTP 方法筛选                    |
| **domain:**              | `domain:example.com`                           | 只看特定域名的请求                  |
| **status-code:**         | `status-code:404`                              | 筛选指定 HTTP 状态码                |
| **mime-type:**           | `mime-type:application/json`                   | 按返回的内容类型筛选                |
| **larger-than:**         | `larger-than:50kb`                             | 按响应体大小（支持单位：b, kb, mb） |
| **is:**                  | `is:from-cache`、`is:running`、`is:redirect`   | 筛选特定请求状态                    |
| **scheme:**              | `scheme:https`                                 | 区分 http / https                   |
| **mixed-content:**       | `mixed-content:all`、`mixed-content:displayed` | 检查混合内容问题                    |
| **priority:**            | `priority:High`、`priority:Low`                | 请求优先级（渲染调试用）            |
| **has-response-header:** | `has-response-header:cache-control`            | 检查响应是否包含某个头              |
| **response-header:**     | `response-header:content-type:image/png`       | 精确匹配响应头内容                  |
| **set-cookie-domain:**   | `set-cookie-domain:example.com`                | 查看特定域设置的 Cookie             |
| **cookie-name:**         | `cookie-name:sessionid`                        | 筛选包含特定 Cookie 的请求          |

---

### 逻辑运算符

| 运算符   | 示例                                 | 说明          |
| -------- | ------------------------------------ | ------------- |
| 空格     | `method:POST domain:api.example.com` | AND（且）逻辑 |
| `-` 前缀 | `-method:GET`                        | NOT（非）逻辑 |
