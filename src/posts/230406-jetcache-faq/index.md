---
title: jetcache缓存使用问题记录
date: "2023-04-06T15:47:11.001Z"
description:
tags:
  - jetcache
---

### @Cache一个类中调用无效

jetcache的方法缓存通过spring aop来实现的，spring aop使用cglib或者jdk proxy得到一个代理，在代理上调用方法，相关的切面才会执行，
一个类里面直接调用自己的另一个方法，没有经过代理，所以不会生效。不仅是jetcache，其他任何aop切面都不会生效。

[@Cached注解无效](https://github.com/alibaba/jetcache/issues/184)


### @Cache自定义key, 不使用Spel表达式
spel可以输出常量
key="'key1'"

[@Cached 能否自定义Key，不使用Spel表达式](https://github.com/alibaba/jetcache/issues/751)