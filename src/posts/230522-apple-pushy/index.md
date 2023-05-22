---
title: Apple Pushy推送
date: "2023-05-22T15:12:37.000Z"
description: Apple Pushy推送
tags:
  - apple
  - pushy
last_updated: "2023-05-22T15:12:37.000Z"
---

```toc
# This code block gets replaced with the TOC
```

## 苹果Pushy推送提示create channel异常

推送证书已被吊销, 需要更新p12证书

```log
[c.e.pushy.apns.ApnsChannelPool:160] : Failed to create channel

io.netty.handler.codec.DecoderException: javax.net.ssl.SSLException: error:10000414:SSL routines:OPENSSL_internal:SSLV3_ALERT_CERTIFICATE_REVOKED
        at io.netty.handler.codec.ByteToMessageDecoder.callDecode(ByteToMessageDecoder.java:477)
        at io.netty.handler.codec.ByteToMessageDecoder.channelRead(ByteToMessageDecoder.java:276)
        at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:379)
        at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:365)
        at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:357)
        at io.netty.channel.DefaultChannelPipeline$HeadContext.channelRead(DefaultChannelPipeline.java:1410)
        at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:379)
        at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:365)
        at io.netty.channel.DefaultChannelPipeline.fireChannelRead(DefaultChannelPipeline.java:919)
        at io.netty.channel.nio.AbstractNioByteChannel$NioByteUnsafe.read(AbstractNioByteChannel.java:166)
        at io.netty.channel.nio.NioEventLoop.processSelectedKey(NioEventLoop.java:719)
        at io.netty.channel.nio.NioEventLoop.processSelectedKeysOptimized(NioEventLoop.java:655)
        at io.netty.channel.nio.NioEventLoop.processSelectedKeys(NioEventLoop.java:581)
        at io.netty.channel.nio.NioEventLoop.run(NioEventLoop.java:493)
        at io.netty.util.concurrent.SingleThreadEventExecutor$4.run(SingleThreadEventExecutor.java:989)
        at io.netty.util.internal.ThreadExecutorMap$2.run(ThreadExecutorMap.java:74)
        at io.netty.util.concurrent.FastThreadLocalRunnable.run(FastThreadLocalRunnable.java:30)
        at java.lang.Thread.run(Thread.java:748)
Caused by: javax.net.ssl.SSLException: error:10000414:SSL routines:OPENSSL_internal:SSLV3_ALERT_CERTIFICATE_REVOKED
        at io.netty.handler.ssl.ReferenceCountedOpenSslEngine.shutdownWithError(ReferenceCountedOpenSslEngine.java:1061)
        at io.netty.handler.ssl.ReferenceCountedOpenSslEngine.sslReadErrorResult(ReferenceCountedOpenSslEngine.java:1346)
        at io.netty.handler.ssl.ReferenceCountedOpenSslEngine.unwrap(ReferenceCountedOpenSslEngine.java:1295)
        at io.netty.handler.ssl.ReferenceCountedOpenSslEngine.unwrap(ReferenceCountedOpenSslEngine.java:1371)
        at io.netty.handler.ssl.ReferenceCountedOpenSslEngine.unwrap(ReferenceCountedOpenSslEngine.java:1414)
        at io.netty.handler.ssl.SslHandler$SslEngineType$1.unwrap(SslHandler.java:224)
        at io.netty.handler.ssl.SslHandler.unwrap(SslHandler.java:1338)
        at io.netty.handler.ssl.SslHandler.decodeNonJdkCompatible(SslHandler.java:1245)
        at io.netty.handler.ssl.SslHandler.decode(SslHandler.java:1282)
        at io.netty.handler.codec.ByteToMessageDecoder.decodeRemovalReentryProtection(ByteToMessageDecoder.java:507)
        at io.netty.handler.codec.ByteToMessageDecoder.callDecode(ByteToMessageDecoder.java:446)
        ... 17 common frames omitted
```