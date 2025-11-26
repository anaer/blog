
日志文件|说明
---|--|
`/var/log/btmp`|记录**错误登录（登陆失败）**日志；使用**lastb**命令查看
`/var/log/lastlog`|记录系统中所有用户最后一次成功登录时间，使用**lastlog**命令查看
`/var/log/wtmp`|永久记录所有用户的登录、注销信息，同时记录系统的启动、重启、关机事件；用**last**命令来查看
`/var/log/utmp`|只记录**当前登录用户**的信息；使用**w,who,users**等命令来查询
`/var/log/secure`|记录验证和授权方面的信息，如SSH登录，su切换用户，sudo授权，甚至添加用户和修改用户密码（Centos）