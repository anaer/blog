---
title: 圈X定时任务学习
date: "2023-05-26T16:53:54.000Z"
description:  圈X定时任务学习
tags:
  - quanx
last_updated: "2023-05-26T16:53:54.000Z"
---

```toc
# This code block gets replaced with the TOC
```

quanx签到js, 未测试过, 待测试.

## 记录请求的Cookie信息

```
更新cookie的情况, 根据情况取下面的条件:
1. 未存cookie
2. cookie超过1小时
3. cookie值有变更
```

```js
// site.cookie.js 获取cookie
const cookieName = 'site'
const cookieKey = 'cookie_site'
const cookieVal = $request.headers['Cookie']

// 获取缓存的Cookie
let cookie = $persistentStore.read(cookieKey)

// 如果缓存中没有Cookie或者Cookie超过1小时,或者Cookie值变化,则更新
if (!cookie || new Date().getTime() - cookie.timestamp > 3600 * 1000 || cookie.val != cookieVal) {
  if (cookieVal) {
    cookie = {
      val: cookieVal,
      timestamp: new Date().getTime()
    }
    let writeCookie = $persistentStore.write(cookie, cookieKey)
    if (writeCookie) {
      let msg = `${cookieName}`
      if (cookie.val != cookieVal) msg += ` (Cookie值更新!)`
      $notification.post(msg, 'Cookie更新成功', '详见日志')
      console.log(msg)
      console.log(cookieVal)
    }
  }
}

$done({})
```

## 任务实体

```js
// site.js 任务实体
const cookieName = 'site'
const cookieKey = 'cookie_site'
const cookieVal = $persistentStore.read(cookieKey)

function sign() {
  let date = new Date()
  let today = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`

  // 获取上一次签到日期
  let lastSignDate = cookieVal.lastSignDate

  // 如果上次签到日期与今日相同,则跳过
  if (lastSignDate == today) {
    let title = `${cookieName}`
    let subTitle = `签到跳过`
    let detail = `今天已经签过了`
    console.log(`${title}, ${subTitle}, ${detail}`)
    return $notification.post(title, subTitle, detail)
  }

  let url = {
    url: `https://www.example.com/sign`,
    headers: {
      Cookie: cookieVal.val
    }
  }
  $httpClient.get(url, (error, response, data) => {
    if (data.indexOf('签到成功') >= 0) {
      // 签到成功,更新最后签到日期
      cookieVal.lastSignDate = today

      let title = `${cookieName}`
      let subTitle = `签到成功`
      let detail = ` 信息: ${data}!`
      console.log(`${title}, ${subTitle}, ${detail}`)
      $notification.post(title, subTitle, detail)
    } else {
      // 判断如果是因为cookie失效导致的, 可以进行cookie删除操作
      console.log('签到失败!')
    }
  })

  // 持久化更新Cookie
  $persistentStore.write(cookieVal, cookieKey)
}

sign()
$done()
```