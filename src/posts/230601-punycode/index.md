---
title: IDN地址与Punycode编码
date: "2023-06-01T10:59:05.000Z"
description: IDN地址与Punycode编码
tags:
  - idn
  - punycode
last_updated: "2023-06-01T10:59:05.000Z"
---

```toc
# This code block gets replaced with the TOC
```

## IDN地址

`https://xn--sss604efuw.ga/` 是一个IDN(国际化域名)地址。
IDN允许使用非ASCII字符集的文字来表示域名,而不仅限于英文字母和数字。这使得不同的语言和文字符号都可以用于域名中。
这种地址形式通过Punycode编码将域名中的非ASCII字符转换为ASCII字符,这样就可以在现有域名系统中支持这些国际化的域名。
Punycode遵循RFC 3492标准,它使用ASCII字符“xn--”来标识一个Punycode编码的国际化域名。
所以,https://xn--sss604efuw.ga/这个地址中:
- xn--表示开始的Punycode编码
- sss604efuw是编码后的域名字符串
- .ga是顶级域

## 相关链接

[Punycode维基](https://zh.wikipedia.org/wiki/Punycode)
[Hutool Punycode编解码工具类](https://www.hutool.cn/docs/#/core/Codec%E7%BC%96%E7%A0%81/Punycode%E5%AE%9E%E7%8E%B0-PunyCode)