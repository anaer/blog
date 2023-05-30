---
title: Spring Cloud Gateway安全配置
date: "2023-05-30T14:27:51.000Z"
description: Spring Cloud Gateway安全配置
tags:
  - spring
  - gateway
last_updated: "2023-05-30T14:27:51.000Z"
---

```toc
# This code block gets replaced with the TOC
```

## 请求拦截

拦截所有匹配 /**/actuator/** 路径的请求,并返回 HTTP 400 响应,阻止请求继续被转发。

```yml
spring:
  cloud:
    gateway:
      routes:
        - id: no_router
          uri: no://op                 # 无效uri, 表明该路由在网关处处理请求
          predicates:                  # 请求匹配条件
            - Pathway=/**/actuator/**
          filters:                     # 过滤器列表
            - SetStatus=400            # Spring Cloud Gateway内置的过滤器, 设置HTTP响应的状态码
```

## 相关链接

[Spring Cloud Gateway文档](https://cloud.spring.io/spring-cloud-static/spring-cloud-gateway/2.2.1.RELEASE/reference/html/)