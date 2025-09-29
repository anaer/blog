
### logrotate配置参数一览

| 参数             | 作用说明                                                                                                   |
|------------------|---------------------------------------------------------------------------------------------------------|
| daily            | 日志每天轮转                                                                                                |
| weekly           | 日志每周轮转                                                                                                |
| monthly          | 日志每月轮转                                                                                                |
| yearly           | 日志每年轮转                                                                                                |
| rotate N         | 仅保留 N 个历史文件，超过自动删除                                                                            |
| maxage DAYS      | 仅保留最近 DAYS 天内日志                                                                                    |
| size SIZE        | 日志达到指定大小时轮转（如：50M, 500k）                                                                     |
| compress         | 对旧日志进行压缩                                                                                            |
| nocompress       | 不压缩轮转后的旧日志                                                                                        |
| delaycompress    | 最近一次轮转日志暂不压缩，等下次轮转时再压缩                                                                |
| missingok        | 日志文件不存在时不报错                                                                                      |
| notifempty       | 如果日志为空则不轮转                                                                                        |
| ifempty          | 即使日志为空也轮转                                                                                          |
| create MODE OWNER GROUP | 以指定权限/用户/组创建新日志文件                                                                      |
| copytruncate     | 针对被进程占用的日志，先拷贝后截断                                                                           |
| nocopytruncate   | 备份日志但不截断                                                                                             |
| mail ADDRESS     | 轮转后的日志发送到指定邮箱                                                                                  |
| nomail           | 不发送备份到邮箱                                                                                            |
| olddir DIR       | 轮转文件移动到指定目录，须与当前日志同文件系统                                                               |
| noolddir         | 轮转文件与当前日志同目录                                                                                    |
| dateext          | 轮转后的日志文件名带日期后缀                                                                                |
| dateformat       | 配合 dateext 使用，自定义日期格式（如 -%Y%m%d%s）                                                           |
| tabooext [+] LIST| 指定不轮转某些扩展名的文件                                                                                  |
| prerotate/endscript | 轮转前执行脚本（单独成行）                                                                                 |
| postrotate/endscript | 轮转后执行脚本（单独成行）                                                                                 |
| sharedscripts    | 全部日志文件轮转完再统一执行一次脚本                                                                         |


### 配置实例

```
/log/*.log
{
    daily
    rotate 3
    nocompress
    missingok
    notifempty
    copytruncate
    create 0640 root root
}
```


### 测试配置

- 检查语法（debug模式，仅校验不实际轮转）：
  ```
  logrotate -d /path/to/your_rule_file
  ```

- 强制执行轮转（真正进行日志分割）：
  ```
  logrotate -f /path/to/your_rule_file
  ```

- 加详细输出（可选）：
  ```
  logrotate -vf /path/to/your_rule_file
  ```