---
title: 微信公众号模板推送问题
date: "2023-04-17T16:09:32.000Z"
description: 微信公众号模板推送问题
tags:
  - wechat
last_updated: "2023-04-17T16:20:16.000Z"
---

## 常见错误码及解决方案

|errcode|errmsg|解决方案|
|---|---|---|
|40036|invalid template_id size | 不合法的 template_id 长度, 可能是template_id未传
|40037|invalid template_id | template_id不正确
|40164|invalid ip 1.1.1.1 ipv6 ::ffff:1.1.1.1, not in whitelist | 配置 ip 白名单
|43004|require subscribe | 需要接收者关注
|43019| require remove blacklist | 需要将接收者从黑名单中移除
|45015|response out of time limit or subscription is canceled | 回复时间超过限制, 由于长时间用户 OpenId 未和微信公众号做互动消息，微信公众号会停止对用户进行消息推送。 需要以用户的身份向微信公众号发送任意文字以激活和微信公众号的互动，然后再次发送客服消息就会成功！
|50002|user limited | 用户受限，可能是违规后接口被封禁

## 微信公众号返回码
需要结合下述两个链接, 单个不全

[微信公众号 全局错误码](https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Global_Return_Code.html)

[返回码](https://developers.weixin.qq.com/doc/oplatform/Return_codes/Return_code_descriptions_new.html)