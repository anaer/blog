---
title: Java Stream用法记录
date: "2023-06-16T14:55:35.000Z"
description: Java Stream用法记录
tags:
  - java
  - stream
last_updated: "2023-07-12T17:28:50.000Z"
---

```toc
# This code block gets replaced with the TOC
```

### 过滤

```java
List<String> result = list.stream()
                          .filter(str -> str.length() > 5)
                          .collect(Collectors.toList());
```

### 映射

字符串列表转大写

```java
List<String> result = list.stream()
                          .map(str -> str.toUpperCase())
                          .collect(Collectors.toList());
```

获取id列表

```java
List<Integer> result = list.stream()
                           .map(c -> c.getId())
                           .collect(Collectors.toList());
```

List<String> 转 List<Long>
```java
List<Long> longList = stringList.stream()
                                .map(Long::parseLong)
                                .collect(Collectors.toList());
```

### 排序

按字符串长度升序排列

```java
List<String> result = list.stream()
                          .sorted((str1, str2) -> str1.length() - str2.length())
                          .collect(Collectors.toList());
```

按年龄降序排列

```java
List<Person> result = list.stream()
                          .sorted(Comparator.comparing(Person::getAge).reversed())
                          .collect(Collectors.toList());
```

### 分组

```java
// 按年龄分组
Map<Integer, List<Student>> ageMap = studentList.stream()
                                                .collect(Collectors.groupingBy(Student::getAge));
```

### 转map


```java
// key重复时, 取前值
Map<Long, User> map = list.stream()
                          .collect(Collectors.toMap(User::getId, Function.identity(), (v1, v2) -> v1))

// key重复时, 取后值
Map<Long, User> map = list.stream()
                          .collect(Collectors.toMap(User::getId, Function.identity(), (v1, v2) -> v2))
```