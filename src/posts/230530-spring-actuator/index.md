---
title: SpringBoot Actuator 安全限制处理
date: "2023-05-30T16:45:53.000Z"
description: SpringBoot Actuator 安全限制处理
tags:
  - spring
  - actuator
last_updated: "2023-05-30T16:45:53.000Z"
---

```toc
# This code block gets replaced with the TOC
```

## SpringBoot Actuator安全限制

SpringBoot Actuator 如果不进行任何安全限制直接对外暴露访问接口，会导致敏感信息泄露甚至恶意命令执行。

**解决方案：**

配置参考 springboot 2.3.2

```yml
management:
    server:
        port: 9999   # 指定端口, 监控信息端口应与业务应用端口不同
    endpoints:
        web:
            base-path: /actuator123 # 路径映射 尽量不使用默认的path, 容易被扫描
            exposure:
                include: info,health,env,metrics,mappings # 允许查询的endpoint
        enabled-by-default: false   # 默认不启用endpoint
    access:
        iplist: 127.0.0.1,192.168.1.1/24  # 允许访问的ip列表
    endpoint:
        info:
            enabled: true  # 启用需要访问的endpoint
        health:
            enabled: true
            show-details: always  # 是否显示详情 never(不显示) / when-authorized (有授权显示) / always (显示)
```