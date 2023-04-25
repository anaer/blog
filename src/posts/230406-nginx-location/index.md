---
title: Nginx location配置
date: "2023-04-06T10:58:03.284Z"
description:
tags:
  - nginx
last_updated: "2023-04-06T10:58:03.284Z"
---

### 匹配多个`.html`链接

如果要匹配`/about.html`和`/contact.html`两个页面，可以按如下方式进行配置：

```nginx
location ~ /(about|contact)\.html$ {
    # your configuration
}
```

上述配置中使用了
  `~`符号表示要使用正则表达式进行匹配。
  `\.`表示需要转义`.`字符，
  `\$`表示匹配结尾。

还可以使用`|`符号连接多个正则表达式进行匹配，如上述代码片段所示。其中`(about|contact)`表示匹配`about`或`contact`字符串。

在上述示例中，如果请求链接为`/about.html`或`/contact.html`，则会被匹配到相应的`location`块中，然后可以继续添加其他配置指令以处理该请求。