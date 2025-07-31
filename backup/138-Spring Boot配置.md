# Spring Boot 配置

仅列举相关配置, 具体配置时, 还需要根据实际使用的版本环境进行调整.

### Tomcat连接池

默认配置: org\springframework\boot\spring-boot-autoconfigure\2.3.12.RELEASE\spring-boot-autoconfigure-2.3.12.RELEASE.jar\META-INF\spring-configuration-metadata.json

```yaml
server:
  tomcat:
    max-connections: 10000  # 最大连接数 默认:8192
    threads:
      max: 800              # 最大工作线程数 默认:200
      min-spare: 100        # 最小空闲线程数 默认:10
    accept-count: 100       # 等待队列长度 默认:100
    connection-timeout: 20000 # 默认未配置
```

### 数据库连接池

SpringBoot默认使用HikariCP作为数据库连接池

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 50      # 最大连接数，默认:10
      minimum-idle: 10           # 最小空闲连接，默认:10
      connection-timeout: 30000
      idle-timeout: 600000       # 空闲连接超时时间，默认:600000（10分钟）
      max-lifetime: 1800000      # 连接最大存活时间 默认:1800000（30分钟）
      leak-detection-threshold: 60000 # 连接泄露检查阈值，默认:0（关闭）
```

### Jackson时区序列化

SpringBoot默认使用Jackson处理JSON序列化，Jackson会使用系统时区，这在分布式部署时会导致不一致的问题。

```yaml
spring:
  jackson:
    time-zone: GMT+8
    date-format: yyyy-MM-dd HH:mm:ss
    serialization:
      write-dates-as-timestamps: false
```

### 日志配置

SpringBoot默认使用Logback，但默认配置下没有对日志文件进行滚动和清理。

长时间运行的应用会产生巨大的日志文件，最终占满磁盘空间。

```yaml
logging:
  file:
    name: app.log
  logback:
    rollingpolicy:
      max-file-size: 100MB
      max-history: 30
      total-size-cap: 3GB
```

### 缓存配置

SpringBoot的Cacheable注解默认使用ConcurrentHashMap作为缓存实现，但这个实现没有过期机制，也没有大小限制。在高并发场景下，缓存会无限增长，最终导致内存溢出。
可以考虑使用Caffeine替代默认实现，可以提供更好的性能和内存管理能力。

```yaml
spring:
  cache:
    type: caffeine
    caffeine:
      spec: maximumSize=10000,expireAfterWrite=600s
```

### 监控端点

SpringBoot Actuator默认暴露了很多监控端点，包括健康检查、配置信息、环境变量等。

只暴露必要的端点，并且配置适当的安全策略，避免信息泄漏。

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics
  endpoint:
    health:
      show-details: when-authorized
```


### 文件上传大小限制

SpringBoot默认的文件上传限制非常小，单个文件只能上传1MB，整个请求大小限制10MB。

```yaml
spring:
  servlet:
    multipart:
      max-file-size: 100MB
      max-request-size: 100MB
      file-size-threshold: 2KB
      location: /tmp
      resolve-lazily: false
```

### 异步线程池配置

使用`@Async`注解时，SpringBoot默认使用`SimpleAsyncTaskExecutor`，这个执行器每次都会创建新线程，没有线程池复用机制。高并发情况下会创建大量线程，最终导致系统资源耗尽。

```yaml
spring:
  task:
    execution:
      pool:
        core-size: 8
        max-size: 16
        queue-capacity: 100
        keep-alive: 60s
      thread-name-prefix: async-task-
    scheduling:
      pool:
        size: 4
      thread-name-prefix: scheduling-
```

### 静态资源缓存策略

SpringBoot默认不为静态资源设置HTTP缓存头，浏览器每次都会重新请求CSS、JS、图片等静态文件，影响页面加载性能。

```yaml
spring:
  web:
    resources:
      cache:
        cachecontrol:
          max-age: 365d
          cache-public: true
      chain:
        strategy:
          content:
            enabled: true
            paths: /**
        cache: true
      static-locations: classpath:/static/
```

开启内容版本化策略后，SpringBoot会根据文件内容生成MD5哈希值作为版本号，文件名变成`style-abc123.css`这样的格式。当文件内容发生变化时，哈希值也会变化，浏览器会认为这是新文件重新下载；如果文件没变化，浏览器就直接使用缓存，有效提升页面加载速度。

### 数据库事务超时

`@Transactional`注解默认没有设置超时时间，长时间运行的事务会一直持有数据库锁，影响其他操作的执行。批量数据处理时，容易出现锁表问题。

```java
@Transactional(timeout = 30, rollbackFor = Exception.class)
public void batchProcess(List<Data> dataList) {
    // 分批处理，避免长事务
    int batchSize = 100;
    for (int i = 0; i < dataList.size(); i += batchSize) {
        List<Data> batch = dataList.subList(i,
            Math.min(i + batchSize, dataList.size()));
        processBatch(batch);
    }
}
```
