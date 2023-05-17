---
title: Guava Cache缓存使用
date: "2023-05-17T15:37:49.000Z"
description: Guava Cache缓存使用
tags:
  - guava
  - cache
last_updated: "2023-05-17T15:37:49.000Z"
---

```toc
# This code block gets replaced with the TOC
```

## pom.xml添加依赖

```xml
<dependency>
  <groupId>com.google.guava</groupId>
  <artifactId>guava</artifactId>
  <version>23.0</version>
</dependency>
```

## 定义缓存

```java
LoadingCache<Long, Optional<UserInfo>> cache = CacheBuilder.newBuilder()
        //并发级别是指可以同时写缓存的线程数
        .concurrencyLevel(Runtime.getRuntime().availableProcessors())
        //设置缓存容器的初始容量为10
        .initialCapacity(10)
        //设置缓存最大容量为100，超过100之后就会按照LRU最近虽少使用算法来移除缓存项
        .maximumSize(100)
        //是否需要统计缓存情况,该操作消耗一定的性能,生产环境应该去除
        .recordStats()
        //设置写缓存后n秒钟过期
        .expireAfterWrite(60, TimeUnit.SECONDS)
        //设置读写缓存后n秒钟过期,实际很少用到,类似于expireAfterWrite
        //.expireAfterAccess(17, TimeUnit.SECONDS)
        //只阻塞当前数据加载线程，其他线程返回旧值
        //.refreshAfterWrite(13, TimeUnit.SECONDS)
        //设置缓存的移除通知
        .removalListener(notification -> {
            System.out.println(notification.getKey() + " " + notification.getValue() + " 被移除,原因:" + notification.getCause());
        })
        //build方法中可以指定CacheLoader，在缓存不存在时通过CacheLoader的实现自动加载缓存
        .build(new CacheLoader<Long, UserInfo>() {
          @Override
          public Optional<UserInfo> load(Long key) throws Exception {
            UserInfo userInfo = getUserInfoByUserId(key);
            return Optional.ofNullable(userInfo);
          }
        });
```

## 使用缓存

```java
try {
  // 读取缓存
  Optional<UserInfo> optional = cache.get(1L);
  if(optional.isPresent()){
    UserInfo userInfo = optional.get();
  }
} catch (ExecutionException e) {
  e.printStackTrace();
}
```

## 关联阅读

[CacheLoader returned null for key](https://blog.csdn.net/codingtu/article/details/89577316)