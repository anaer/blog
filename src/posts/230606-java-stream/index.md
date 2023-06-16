---
title: Java Stream用法记录
date: "2023-06-16T14:55:35.000Z"
description: Java Stream用法记录
tags:
  - java
  - stream
last_updated: "2023-06-16T14:55:35.000Z"
---

```toc
# This code block gets replaced with the TOC
```


```java
// 按年龄分组
Map<Integer, List<Student>> ageMap = studentList.stream().collect(Collectors.groupingBy(Student::getAge));
```