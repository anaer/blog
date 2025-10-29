# RabbitMQ queue(队列)参数说明

| 参数                                               | 描述                                                                                                                  |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| queue                                              | 队列名称                                                                                                              |
| durable                                            | 是否持久化                                                                                                            |
| exclusive                                          | 是否排外 会对当前队列加锁，其他通道channel是不能访问的，如果强制访问会报异常, 当连接被关闭或者丢失, 队列会被删除      |
| autoDelete                                         | 是否自动删除  当最后一个订阅者被取消, 连接丢失, 队列会被删除                                                          |
| Message TTL(x-message-ttl)                         | 消息的生存周期                                                                                                        |
| Auto Expire(x-expires)                             | 队列定时删除 当队列在指定的时间没有被访问就会被删除                                                                   |
| Max Length(x-max-length)                           | 队列的消息的最大值长度 超过指定长度将会把最早的几条消息删除掉                                                         |
| Max Length Bytes(x-max-length-bytes)               | 队列最大占用的空间大小 一般受限于内存、磁盘的大小                                                                     |
| Dead letter exchange(x-dead-letter-exchange)       | 当队列消息长度大于最大长度、或者过期的等，将从队列中删除的消息推送到指定的交换机中去而不是丢弃掉                      |
| Dead letter routing key(x-dead-letter-routing-key) | 将删除的消息推送到指定交换机的指定路由键的队列中去                                                                    |
| Maximum priority(x-max-priority)                   | 优先级队列 声明队列时先定义最大优先级值，在发布消息的时候指定该消息的优先级， 优先级更高（数值更大的）的消息先被消费, |
| Lazy mode(x-queue-mode=lazy)                       | 先将消息保存到磁盘上，不放在内存中，当消费者开始消费的时候才加载到内存中                                              |
