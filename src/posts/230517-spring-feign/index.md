---
title: Spring Feign
date: "2023-05-17T15:04:42.000Z"
description: Spring Feign
tags:
  - spring
  - feign
last_updated: "2023-05-17T15:04:42.000Z"
---

```toc
# This code block gets replaced with the TOC
```

## FeignClient注入失败/请求熔断排查

### 调用方
1. 要启用 Feign 支持，确保在 `@SpringBootApplication` 类上添加 `@EnableFeignClients` 注解。

2. 确保 `@FeignClient` 接口被正确注入到代码中。

```java
@Autowired
private MyServiceClient myServiceClient;
```

### 提供方

1. 确保 `@FeignClient` 注解中指定了正确的服务名称和 URL。例如：

```java
@FeignClient(name = "my-service", url = "http://localhost:8080")
public interface MyServiceClient {
    // ...
}
```

2. 没有将 `@FeignClient` 注解标记为 `@Component` 或者没有在 Spring Boot 应用程序中启用组件扫描。
   要启用组件扫描，请确保在您的 `@SpringBootApplication` 类上添加 `@ComponentScan` 注解。