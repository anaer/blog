## systemctl 常用命令

| 命令                                 | 说明                     | 示例                                 |
|:-------------------------------------|:-------------------------|:--------------------------------------|
| systemctl start [服务名]             | 启动服务                 | systemctl start nginx                 |
| systemctl stop [服务名]              | 停止服务                 | systemctl stop nginx                  |
| systemctl restart [服务名]           | 重启服务                 | systemctl restart nginx               |
| systemctl reload [服务名]            | 重新加载服务配置         | systemctl reload nginx                |
| systemctl status [服务名]            | 查看服务状态             | systemctl status nginx                |
| systemctl enable [服务名]            | 开机自启服务             | systemctl enable nginx                |
| systemctl disable [服务名]           | 取消开机自启             | systemctl disable nginx               |
| systemctl is-enabled [服务名]        | 查看服务是否开机自启     | systemctl is-enabled nginx            |
| systemctl is-active [服务名]         | 查看服务是否激活         | systemctl is-active nginx             |
| systemctl list-units --type=service  | 列出所有已加载服务       | systemctl list-units --type=service   |
| systemctl list-unit-files --type=service | 列出所有服务及自启状态| systemctl list-unit-files --type=service|
| systemctl daemon-reload              | 重新加载单元文件         | systemctl daemon-reload               |
| systemctl mask [服务名]              | 服务彻底禁止启动         | systemctl mask nginx                  |
| systemctl unmask [服务名]            | 取消服务mask限制         | systemctl unmask nginx                |
| systemctl reload-or-restart [服务名] | 配置变更自动重载或重启   | systemctl reload-or-restart nginx     |
| systemctl --failed                   | 查看失败的服务           | systemctl --failed                    |
| systemctl get-default                | 查看默认启动级别(target) | systemctl get-default                 |
| systemctl set-default [target]       | 设置默认启动级别(target) | systemctl set-default multi-user.target|
| systemctl isolate [target]           | 切换系统运行级别         | systemctl isolate rescue.target       |
| systemctl poweroff                   | 关机                     | systemctl poweroff                    |
| systemctl reboot                     | 重启                     | systemctl reboot                      |
| systemctl suspend                    | 挂起                     | systemctl suspend                     |
| systemctl hibernate                  | 休眠                     | systemctl hibernate                   |
| systemctl list-dependencies [服务名] | 查看服务依赖             | systemctl list-dependencies nginx     |
