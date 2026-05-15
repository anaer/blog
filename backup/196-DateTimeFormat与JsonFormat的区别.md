## `@DateTimeFormat` 与 `@JsonFormat` 的区别

## 一、核心区别

| 维度         | `@DateTimeFormat`               | `@JsonFormat`              |
| ------------ | ------------------------------- | -------------------------- |
| **所属框架** | Spring Framework                | Jackson (JSON 处理库)      |
| **主要用途** | 参数绑定、表单提交的日期转换    | JSON 序列化/反序列化       |
| **作用场景** | Spring MVC 控制器参数、表单提交 | REST API 的 JSON 请求/响应 |
| **触发时机** | Spring 数据绑定时               | Jackson 处理 JSON 时       |


## 二、场景对比

| 场景                                                | 推荐注解          | 说明                                   |
| --------------------------------------------------- | ----------------- | -------------------------------------- |
| **REST API JSON 接口**                              | `@JsonFormat`     | 请求/响应体是 JSON                     |
| **表单提交（`application/x-www-form-urlencoded`）** | `@DateTimeFormat` | 参数在 query string 或 form data 中    |
| **`@RequestParam` 日期参数**                        | `@DateTimeFormat` | 如 `?date=2025-12-19`                  |
| **文件上传（`multipart/form-data`）中的日期字段**   | `@DateTimeFormat` | Spring 自动绑定                        |
| **Feign 客户端日期参数**                            | `@DateTimeFormat` | Feign 默认使用 Spring 的转换器         |
| **普通 Java 对象转 JSON**                           | `@JsonFormat`     | `ObjectMapper.writeValueAsString(obj)` |
