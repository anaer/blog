## 分类列表

| 分类               | category |
| ------------------ | -------- |
| OPT_CATEGORY_FORMAT | 1        |
| OPT_CATEGORY_CODEC  | 2        |
| OPT_CATEGORY_SWS    | 3        |
| OPT_CATEGORY_PLAYER | 4        |

## 配置列表

|  分类  | 配置项                              | 描述                                                                                 | 默认值      | 建议值 |
| :----: | ----------------------------------- | ------------------------------------------------------------------------------------ | ----------- | ------ |
| CODEC  | skip_frame                          | 跳帧开关，如果 cpu 解码能力不足，可能会引起音画不同步，也可以设置它来实现倍速播放    | 5           |
| CODEC  | skip_loop_filter                    | 跳过循环滤波; 0 开启, 画面质量高, 解码开销大; 48 关闭,画面质量差, 解码开销小         | 48          |
| CODEC  | tune                                | tune 的参数主要配合视频类型和视觉优化的参数                                          | zerolatency |
| FORMAT | analyzeduration                     | 播放前的探测时间 1 达到首屏秒开效果 单位是微妙                                       | 1           |
| FORMAT | analyzemaxduration                  | 播放前的最大探测时间 100 (说是以讹传讹, 没这参数)                                    | 100         |
| FORMAT | avioflags                           |                                                                                      | direct      |
| FORMAT | dns_cache_clear                     | 清空 dns，因为多种协议播放会缓存协议导致播放 h264 后无法播放 h265.                   | 1           |
| FORMAT | fflags                              | fastseek 设置 seekTo 能够快速 seek 到指定位置并播放 ; nobuffer                       | fastseek    |
| FORMAT | flush_packets                       | 通过立即清理数据包来减少等待时长 1 开启 0 关闭                                       |
| FORMAT | http-detect-range-support           |                                                                                      | 0           |
| FORMAT | max-buffer-size                     | 最大缓冲大小 单位 kb, 默认值 `5*1024*1024=5242880` 即 5M                             | 5242880     |
| FORMAT | max_delay                           |                                                                                      | 0           |
| FORMAT | probesize                           | 播放前的探测大小, 默认是 1M, 改小一点会出画面更快(可能会有画面没声音)                | 1024        | 不设置 |
| FORMAT | reconnect                           | 播放重连次数                                                                         | 1           |
| FORMAT | reorder_queue_size                  | 设置要缓冲的数据包数以处理重新排序的数据包                                           | 0           |
| FORMAT | rtbufsize                           |                                                                                      | 60          |
| FORMAT | rtsp_flags                          | rtsp 支持                                                                            |
| FORMAT | rtsp_transport                      | 如果是 rtsp 协议, 可以优先用 tcp(默认是用 udp)                                       | udp         | tcp    |
| PLAYER | accurate-seek-timeout               | seek 默认超时时间 `5*1000` ms                                                        |
| PLAYER | an                                  | 静音设置 1 开启 0 关闭                                                               | 0           |
| PLAYER | enable-accurate-seek                | SeekTo 设置优化                                                                      | 0           |
| PLAYER | find_stream_info                    | 0 不查询 stream_info, 直接使用                                                       |
| PLAYER | first-high-water-mark-ms            | 设置第一次唤醒 read_thread 线程的时间(毫秒)，范围 100-5000，默认值 100               | 100         |
| PLAYER | fps                                 | 每秒传输帧数                                                                         | 20          |
| PLAYER | framedrop                           | 跳帧处理,CPU 处理慢时，跳帧处理，保证播放流程，音画同步                              | 1           | 1      |
| PLAYER | infbuf                              | 无限读                                                                               | 1           |
| PLAYER | last-high-water-mark-ms             | 设置最后一次唤醒 read_thread 线程的时间(毫秒)，范围 100-5000，默认值 5000            | 5000        |
| PLAYER | max-fps                             | 设置最大 fps                                                                         | 30          |
| PLAYER | max_cached_duration                 | 最大缓存时长(毫秒)                                                                   |             | 3000   |
| PLAYER | mediacodec                          | 1 硬解码(使用媒体解码器); 0 软解码(使用 av 解码器)                                   | 0           |
| PLAYER | mediacodec-auto-rotate              | 自动旋屏                                                                             | 0           |
| PLAYER | mediacodec-handle-resolution-change | 处理分辨率变化                                                                       | 0           |
| PLAYER | mediacodec-hevc                     | 开启 H265 硬解码                                                                     | 0           |
| PLAYER | min-frames                          | 设置停止预读取的最小帧数, 范围 2-50000, 默认 50000                                   | 50000       |
| PLAYER | next-high-water-mark-ms             | 设置下一次唤醒 read_thread 线程的时间(毫秒)，范围 100-5000，默认值 1000              | 1000        |
| PLAYER | opensles                            | Open Sound Library for Embedded Systems 为嵌入式系统打开声音库                       | 0           |
| PLAYER | overlay-format                      |                                                                                      | 842225234   |
| PLAYER | packet-buffering                    | 是否开启预缓冲, 一般直播项目会开启, 达到秒开的效果, 不过播放可能丢帧卡顿             | 0           | 0      |
| PLAYER | r                                   | 帧速率(fps) （可以改，确认非标准桢率会导致音画不同步，所以只能设定为 15 或者 29.97） |             | 29.97  |
| PLAYER | render-wait-start                   | 1 等待开始之后才绘制                                                                 |
| PLAYER | soundtouch                          | 设置是否开启变调 1 开启; 0 关闭                                                      | 1           |
| PLAYER | start-on-prepared                   | 0 为一进入就播放,1 为进入时不播放                                                    | 1           |
| PLAYER | sync                                |                                                                                      | ext         |
| PLAYER | sync-av-start                       | 音视频启动时不做对齐，加速秒开                                                       | 0           | 0      |
| PLAYER | videotoolbox                        | 开启硬解码 1 是硬解 0 是软解                                                         | 0           |
| PLAYER | vol                                 | 设置音量大小, 256 为标准音量                                                         | 256         |

## 参数说明

### tune

tune 的参数主要配合视频类型和视觉优化的参数，或特别的情况。
如果视频的内容符合其中一个可用的调整值又或者有其中需要，则可以使用此选项，否则建议不使用（如 tune grain 是为高比特率的编码而设计的）。

| tune 取值   | 说明                                                           |
| :---------- | -------------------------------------------------------------- |
| film        | 电影、真人类型；                                               |
| animation   | 动画；                                                         |
| grain       | 需要保留大量的 grain 时用；                                    |
| stillimage  | 静态图像编码时使用；                                           |
| psnr        | 为提高 psnr 做了优化的参数；                                   |
| ssim        | 为提高 ssim 做了优化的参数；                                   |
| fastdecode  | 可以快速解码的参数；                                           |
| zerolatency | 零延迟，用在需要非常低的延迟的情况下，比如电视电话会议的编码。 |
