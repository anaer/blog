## 安装
系统: Ubuntu 20.04.6 LTS

```bash
apt-get install fail2ban
```

## 命令

### 查询服务状态

```bash
service fail2ban status
systemctl status fail2ban.service
```

### 查询状态

```bash
# 查看启用的规则
# fail2ban-client status
Status
|- Number of jail:      1
`- Jail list:   sshd

# 查看规则详情
# fail2ban-client status sshd
Status for the jail: sshd
|- Filter
|  |- Currently failed: 0
|  |- Total failed:     0
|  `- File list:        /var/log/auth.log
`- Actions
   |- Currently banned: 0
   |- Total banned:     0
   `- Banned IP list:

# 重新加载配置
# fail2ban-client reload

# 重新加载单个配置
# fail2ban-client reload sshd

# 手动解禁IP
# fail2ban-client set sshd unbanip 192.168.1.1
```

## 配置

配置目录: `/etc/fail2ban`

修改sshd配置
/etc/fail2ban/jail.d/sshd.conf

```bash
[sshd]
enabled = true
mode   = normal
port    = ssh
filter  = sshd
banaction = iptables
            bark[name=sshd]
backend = systemd
maxretry = 2
findtime = 1d
bantime = 2w
ignoreip = 127.0.0.1/8
logpath = %(sshd_log)s
#backend = %(sshd_backend)s
```

添加bark.conf自定义action
```bash
vim /etc/fail2ban/action.d/bark.conf
```

```bash
[Definition]
norestored = 1
actionban   = /usr/bin/python3 /root/script/bark.py fail2ban-<name> <ip>
actionunban =
actioncheck =
actionstart =
actionstop =

[Init]

name = default
blocktype = unreachable
```

## 参考链接

[Fail2Ban 教程](https://github.com/wangdoc/ssh-tutorial/blob/main/docs/fail2ban.md)
[Fail2ban推荐配置脚本](https://idcflare.com/t/topic/17588)