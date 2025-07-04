网络波动时因匿名队列的排他性导致无法连接, 队列又因为auto-delete自动删除, 可能通过指定队列名的形式来处理

```log
#method<channel.close>(reply-code=405, reply-text=RESOURCE_LOCKED - cannot obtain exclusive access to locked queue 'springCloudBus.anonymous.xxxxx' in vhost '/', class-id=50, method-id=10)

#method<channel.close>(reply-code=404, reply-text=NOT_FOUND - no queue 'springCloudBus.anonymous.xxxxx' in vhost '/', class-id=50, method-id=10)
```

springCloudBus.anonymous.xxxxx 队列特性:
```yaml
x-queue-master-locator:	client-local
exclusive:	true  # 排他性
auto-delete:	true # 自动删除
```

[RabbitExchangeQueueProvisioner.doProvisionConsumerDestination](https://github.com/spring-cloud/spring-cloud-stream/blob/2916acfac7747cd842d7aa91ef2979adf345abc0/binders/rabbit-binder/spring-cloud-stream-binder-rabbit-core/src/main/java/org/springframework/cloud/stream/binder/rabbit/provisioning/RabbitExchangeQueueProvisioner.java#L233)

group 参数为空的时候，自动创建匿名的排他队列


```yaml
spring:
  cloud:
    stream:
      default:
        group: ${spring.application.name}-${spring.cloud.client.ip-address}-${server.port}
      rabbit:
        bindings:
          springCloudBusInput:
            consumer:
              # 为true时，使用‘group’作为配置刷新队列的名称
              queue-name-group-only: true
```
## 相关连接
[【spring cloud 配置中心 + rabbit mq】网络断连恢复引起的配置无法动态刷新](https://www.jianshu.com/p/84f0667fa277)