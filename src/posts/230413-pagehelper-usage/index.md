---
title: PageHelper分页查询
date: "2023-04-13T17:15:11.001Z"
description: PageHelper分页查询
tags:
  - pagehelper
---

### pom.xml

```xml
<dependency>
    <groupId>com.github.pagehelper</groupId>
    <artifactId>pagehelper-spring-boot-starter</artifactId>
    <version>1.3.2</version>
</dependency>
```

PageHelper.startPage相当于开启分页,通过拦截MySQL的方式,拦截查询语句拦添加limit.

```java
public PageInfo<User> getUsers(PageQuery pageQuery) {
        PageHelper.startPage(pageQuery.getPage(),pageQuery.getRows());
        List<User> userList = userMapper.selectByExample(null);
        PageInfo<User> pageInfo=new PageInfo<>(userList);
        return pageInfo;
    }
```
