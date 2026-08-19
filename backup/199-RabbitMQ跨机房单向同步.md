## RabbitMQ跨机房单向同步

### Shovel单向同步
Shovel 像一个内置的“消息泵”，从源队列消费，再发布到目标。

启用插件
```sh
rabbitmq-plugins enable rabbitmq_shovel rabbitmq_shovel_management
```

在RabbitMQ控台Admin->Shovel Management配置页配置

uri配置 `amqp://user:password@server-name/my-vhost`
1. 需要url编码 user 和 password 部分，以防包含@等特殊字符
2. VHost / 本身也要写成 %2f
