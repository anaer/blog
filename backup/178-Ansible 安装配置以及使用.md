多台 CentOS 服务器同步配置

## 安装Ansible

```sh
# 安装 ansible
yum install ansible

# 验证安装
ansible --version
```

## 配置主机清单

`vim /etc/ansible/hosts`

可以按情况添加分组

```conf
[servers]
192.168.0.1
192.168.0.2
```

## 配置SSH免密登录

Ansible 默认通过 SSH 执行命令，因此目标节点需支持免密登录：

```sh
ssh-keygen -t rsa
ssh-copy-id root@192.168.0.1
ssh-copy-id root@192.168.0.2
```

## 测试主机节点可达

```sh
ansible all -m ping
```

输出示例：
```
192.168.0.1 | SUCCESS => {"changed": false, "ping": "pong"}
```

执行远程命令
```sh
ansible servers -m shell -a "uptime"
```

推送配置
```sh
ansible all -m copy -a "src=/root/myconf/nginx.conf dest=/etc/nginx/nginx.conf"
```

批量执行命令：
```sh
ansible all -m shell -a "systemctl restart nginx"
```
