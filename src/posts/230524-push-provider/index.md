---
title: 推送厂商对比
date: "2023-05-24T10:13:30.000Z"
description: 推送厂商对比
tags:
  - push
last_updated: "2023-05-24T10:13:30.000Z"
---

```toc
# This code block gets replaced with the TOC
```

# 华为

没有别名和标签

官方网站: https://developer.huawei.com/consumer/cn/hms/huawei-pushkit/

隐私政策: https://developer.huawei.com/consumer/cn/doc/development/HMSCore-Guides/privacy-statement-0000001050042021

接入视频: https://developer.huawei.com/consumer/cn/training/course/video/100000000083

开发文档: https://developer.huawei.com/consumer/cn/doc/development/HMSCore-Guides/android-server-dev-0000001050040110

消息回执: https://developer.huawei.com/consumer/cn/doc/development/HMSCore-Guides/msg-receipt-guide-0000001050040176

常见问题: https://developer.huawei.com/consumer/cn/forum/topic/37729830?fid=18

下行消息及错误码: https://developer.huawei.com/consumer/cn/doc/development/HMSCore-References/https-send-api-0000001050986197

消息分类: https://developer.huawei.com/consumer/cn/doc/development/HMSCore-Guides/message-classification-0000001149358835


鉴权说明: 开发者应用在 Access Token 有效期（expires_in）内，请勿过于频繁请求，否则可能会被流控（当前应用级 Access Token 的流控阈值为 1000 个/5 分钟，5 分钟内申请 Access Token 超过 1000 个，后续将提示被流控，无法申请。5 分钟后重置，可以再次申请）。您可根据有效期，提前重新申请或通过 Refresh Token 刷新鉴权凭证，同时您也可根据鉴权凭证超时错误返回（NSP_STATUS=6，请参见错误与异常机制），重新触发申请鉴权凭证流程。

消息体限制:
title, body 无明确限制
消息体大小（不含 Token）系统设置的默认限制（4096Bytes）

消息量限制: https://developer.huawei.com/consumer/cn/doc/development/HMSCore-Guides/message-restriction-description-0000001361648361

流控限制 3000QPS,每秒不能超过 3000token 数.

# 小米

regId

regid 与 alias 一一对应
多个设备设置同一 alias, 只有最后的设备才能收到消息 (如果需要多个设备使用同一 alias, 推荐使用 UserAccount 消息)
每个 app 单台设备可订阅的 alias 上限为 15 个

官方网站：https://dev.mi.com/console/appservice/push.html

隐私政策：https://dev.mi.com/console/doc/detail?pId=1822

合规指南：https://dev.mi.com/console/doc/detail?pId=2379

开发文档：https://dev.mi.com/console/doc/detail?pId=230#_2

服务端 Java SDK 文档: https://dev.mi.com/console/doc/detail?pId=1278#_0

鉴权方式: 添加 HEADER 字段 Authorization，用于身份验证。格式是 key=<APP_SECRET>。
APP_SECRET 是从开发者网站申请得到。

APP_SECRET 固定的, 没有失效期, 长期有效

消息体限制:
```
title:设置在通知栏展示的通知的标题, 不允许全是空白字符, 长度小于 50, 一个中英文字符均计算为 1(通知栏消息必填)
description:设置在通知栏展示的通知描述, 不允许全是空白字符, 长度小于 128, 一个中英文字符均计算为 1(通知栏消息必填)
payload:设置要发送的消息内容 payload, 不允许全是空白字符, 长度小于 4KB, 一个中英文字符均计算为 1(透传消息回传给 APP, 为必填字段, 非透传消息可选)
extra: key 和 value 的字符数不能超过 1024, 至多可以设置 10 个 key-value 键值对
callback: 第三方接收回执的 Http 接口, 最大长度 128 字节
callback.param: 第三方自定义回执参数, 最大长度 64 字节
```

消息量限制:
(广播)普通消息限制 50000 条/天
(运营)重要消息

回执: 只有单推有回执

## 错误码

```json
[ messageId=tdm587XXX errorCode=0 data={"day_acked":"979","id":"tdm587XXX","day_quota":"50000"} trace_id=Xdm587XXX ]
[ messageId=Xcm609XXX errorCode=10008 reason=Title or Description exceeds the maximum number of characters! data={"day_acked":"3159","day_quota":"50000"} trace_id=Xcm609XXX ]
[ messageId=Xdm575XXX errorCode=65015 reason=Extra total length is too long, must less than 2048. data={"day_acked":"3130","day_quota":"50000"} trace_id=Xdm575XXX ]
[ messageId=Xdm603XXX errorCode=200001 reason=exceed quota, quota : 50000, have acked 52168 trace_id=Xdm603XXX ]
```

# OPPO

regId
alias 与 regId 一一对应, 同一 alias 不能对应多个 regId, alias 对应的 regId 以最后一次为准

alias 失效:
主动调用 unsetalias
alias 对应的 regId 已经失效
设置 alias 不成功(调用 setalias 失败)

官方网站：https://open.oppomobile.com/newservice/capability?pagename=push

服务协议：https://open.oppomobile.com/wiki/doc#id=10194

开发文档：https://open.oppomobile.com/wiki/doc#id=10742

通知通道: https://open.oppomobile.com/new/developmentDoc/info?id=10289

鉴权: 官网未说明一个 appId 是否可以有多个 token
有效期默认为 24 小时

回执: 当消息到达设备之后, oppo 才会发送回执, 因此瞎填的 regId 就没有回执了.
只有单推 有回执

消息体限制:
```
title:设置在通知栏展示的通知栏标题, 【字数串长度限制在 50 个字符内，中英文字符及特殊符号（如 emoji）均视为一个字符】
content:设置在通知栏展示的通知的正文内容
1）当选择标准样式（style 设置为 1）时，内容字符串长度限制在 200 以内；
2）当选择长文本样式（style 设置 为 2）时，内容字符串长度限制在 128 以内；
3）当选择大图样式（style 设置为 3）时，内容字符串长度限制在 50 以内。
【字符串长度计算说明：中英文字符及特殊符号（如 emoji）均视作一个字符计算】
action_parameters:打开应用内页或网页时传递给应用或网页的附加参数【JSON 格式】，字符串长度不超过 4000。当跳转类型是 URL 类型时，参数会以 URL 参数直接拼接在 URL 后面。
call_back_url:URL 长度限制在限制 200 以内。
call_back_parameter:参数字符串长度限制在 100 以内，OPPO PUSH 将这个参数设置在回执请求体单个 JSON 结构的 param 字段中。
```

推送限制: ![](OPPO推送限制.png)

消息量限制:
公信消息限制 100000 条/天

## 错误码
```json
{"code": 10000, "message": "Invalid RegistrationId" }
{"code":33,"data":{"permits":100000,"pushed":105207},"message":"The number of messages exceeds the daily limit"}
```

# VIVO

regId
alias 与 regId 一一对应, 同一 alias 不能对应多个 regId, alias 对应的 regId 以最后一次为准

alias 失效:
```
主动调用 unsetalias
alias 对应的 regId 已经失效
```

官方网站：https://dev.vivo.com.cn/home

隐私政策：https://dev.vivo.com.cn/documentCenter/doc/366

开发文档：https://dev.vivo.com.cn/documentCenter/doc/180

鉴权说明: 一个 appId 可对应多个 token，24 小时过期，业务方做中心缓存，1-2 小时更新一次。
限制：一天限制调用不超过 10000 次。

消息分级:
系统消息:

运营消息:

```
频控管控：单用户单应用每天收到的消息条数上限 5 条
```

消息体限制:
```
title:通知标题（用于通知栏消息） 最大 20 个汉字（一个汉字等于两个英文字符，即最大不超过 40 个英文字符）
content:通知内容（用于通知栏消息） 最大 50 个汉字（一个汉字等于两个英文字符，即最大不超过 100 个英文字符）
skipContent:跳转内容 跳转类型为 2 时，跳转内容最大 1000 个字符，跳转类型为 3 或 4 时，跳转内容最大 1024 个字符
requestId:用户请求唯一标识 最大 64 字符
callback: 第三方接收回执的 http 接口，最大长度 128 个字符
callback.param:第三方自定义回执参数，最大长度 64 个字符
```

消息量限制:
```
系统消息 限制 10000 条/天 >> 100000 条/天
运营消息 频控 单用户 5 条/天
```

## 错误码

```json
{"result":0,"desc":"请求成功","taskId":"xxx"}
{"result":10058,"desc":"content长度不能超过100个字符"}
{"result":10069,"desc":"skipType = 4, skipContent超过长度限制"}
{"result":10302,"desc":"用户Id不合法","invalidUser":{"status":2,"userid":"xxx"}}
{"result":10306,"desc":"extra callback.param长度不能超过64个字符"}
{"result":10070,"desc":"运营消息发送量总量超出限制"}
```

# 魅族

```
同个 pushId 只有一个别名, pushId 对应的别名以最后一次订阅为准
多个 pushId 可以绑定同一别名

别名失效:
对应的 pushId 失效
App 调用 unSubScribeAlias
```

官方网站：https://open.flyme.cn/open-web/views/push.html?t=1514529597773

隐私政策：http://open-wiki.flyme.cn/doc-wiki/index?title=%E9%AD%85%E6%97%8F%E6%8E%A8%E9%80%81%E5%B9%B3%E5%8F%B0%E5%BC%80%E5%8F%91%E8%80%85%E6%96%87%E6%A1%A3#id?10

开发文档：http://open-wiki.flyme.cn/doc-wiki/index?title=%E9%AD%85%E6%97%8F%E6%8E%A8%E9%80%81%E5%B9%B3%E5%8F%B0%E5%BC%80%E5%8F%91%E8%80%85%E6%96%87%E6%A1%A3#id?129

# 苹果

错误码: https://developer.apple.com/library/archive/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/CommunicatingwithAPNs.html#//apple_ref/doc/uid/TP40008194-CH11-SW1

pushy 最佳实践: https://github.com/jchambers/pushy/wiki/Best-practices

消息体限制:
For regular remote notifications, the maximum size is 4KB (4096 bytes)

消息量限制:
无限制

[What are the possible reasons to get APNs responses BadDeviceToken or Unregistered?](https://stackoverflow.com/questions/42511476/what-are-the-possible-reasons-to-get-apns-responses-baddevicetoken-or-unregister)

[APNS Push Token Management](https://developer.apple.com/forums/thread/670868?answerId=655652022#655652022)

```
How this works though, is, when an app is deleted from a device, the device token is not invalidated immediately.
To avoid developers from detecting and tracking user behavior around installations and uninstallations, APNs invalidates tokens on a sliding schedule. This schedule is not documented, and can change at any time. This is for protecting the users’ privacy, and is by design.

但是，当从设备中删除应用程序时，设备令牌不会立即失效。
为了避免开发人员检测和跟踪安装和卸载的用户行为，APNs 会按滑动计划使令牌失效。此时间表未记录在案，并且可能随时更改。这是为了保护用户的隐私，并且是设计使然。
```

[Apple push feedback service with new token based http2 requests](https://developer.apple.com/forums/thread/109376?answerId=669256022#669256022)

```
Unfortunately, it even returns "200" or success for a device token from a device that uninstalled the app 2 years ago. So basically there is no way to know if the user uninstalled the app or not
```

# 个推

* 根据clientId推送, 返回报错: {"response":{"result":"AppidError"},"resultCode":"RESULT_OK"}

用真机调试，必须用个推平台登记的应用参数重新云端打包才行。

[问题相关链接](https://blog.csdn.net/java_newbie2/article/details/102315019)