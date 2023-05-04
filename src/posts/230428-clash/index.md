---
title: Clash配置
date: "2023-04-28T16:47:52.000Z"
description: Clash配置
tags:
  - clash
last_updated: "2023-05-04T13:28:56.000Z"
---

```toc
# This code block gets replaced with the TOC
```

## 添加配置预处理

可以在加载配置文件时, 进行预处理, 可以在加载Remote Profiles添加自定义配置

测试Rule模式有效, Script模式需要看Script脚本是否处理到

举例: 针对Google Bard走美国代理节点

Settings -> Profiles -> Parsers Edit

```yaml
parsers: # array
  - url: https://anaer.github.io/Sub/clash.yaml
    yaml:
      prepend-rules:
        - DOMAIN,bard.google.com,US # rules最前面增加一个规则
      append-proxy-groups:
        - name: US # 建立新策略组
          type: load-balance
          url: "http://www.gstatic.com/generate_204"
          interval: 300

      commands:
        - proxy-groups.US.proxies=[]proxyNames|美国
        - proxy-groups.PROXY.proxies.4+US
```

### yaml下支持的配置项
| 键                   | 值类型 | 操作                                     |
| -------------------- | ------ | ---------------------------------------- |
| append-rules         | 数组   | 数组合并至原配置rules数组后              |
| prepend-rules        | 数组   | 数组合并至原配置rules数组前              |
| append-proxies       | 数组   | 数组合并至原配置proxies数组后            |
| prepend-proxies      | 数组   | 数组合并至原配置proxies数组前            |
| append-proxy-groups  | 数组   | 数组合并至原配置proxy-groups数组后       |
| prepend-proxy-groups | 数组   | 数组合并至原配置proxy-groups数组前       |
| mix-proxy-providers  | 对象   | 对象合并至原配置proxy-providers中        |
| mix-rule-providers   | 对象   | 对象合并至原配置rule-providers中         |
| mix-object           | 对象   | 对象合并至原配置最外层中                 |
| commands             | 数组   | 在上面操作完成后执行简单命令操作配置文件 |

## 参考链接

[配置文件预处理](https://docs.cfw.lbyczf.com/contents/parser.html)