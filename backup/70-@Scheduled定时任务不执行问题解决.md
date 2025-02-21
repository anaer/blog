当@RefreshScope触发Bean刷新时，原有的Bean实例被销毁，新实例被创建。
但是，ScheduledAnnotationBeanPostProcessor只在容器初始化时执行一次，不会重新扫描新创建的Bean。因此，新Bean中的@Scheduled方法未被注册，导致定时任务失效。

这里仅记录最简单的一种解决方案, 其他方式见相关链接

```java
import java.text.SimpleDateFormat;
import java.util.Date;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.context.config.annotation.RefreshScope;
import org.springframework.cloud.context.scope.refresh.RefreshScopeRefreshedEvent;
import org.springframework.context.ApplicationListener;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
@RefreshScope
public class AlertSchedulerCron implements ApplicationListener<RefreshScopeRefreshedEvent> {

    private SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");

    @Value("${pollingtime}")
    private String pollingtime;

    /*
     * @Value("${interval}") private String interval;
     */
    @Scheduled(cron = "${pollingtime}")
    //@Scheduled(fixedRateString = "${interval}" )
    public void task() {
        System.out.println(pollingtime);
        System.out.println("Scheduler (cron expression) task with duration : " + sdf.format(new Date()));
    }

    @Override
    public void onApplicationEvent(RefreshScopeRefreshedEvent event) {
        // TODO Auto-generated method stub

    }
}
```

## 相关链接

[@RefreshScope stops @Scheduled task](https://stackoverflow.com/questions/50440468/refreshscope-stops-scheduled-task)

[@RefreshScope导致@Scheduled失效](https://www.jianshu.com/p/0e490fe4ff7a)
