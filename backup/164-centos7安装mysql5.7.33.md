# centos7安装mysql5.7.33

## 下载安装包
mysql-5.7.33-linux-glibc2.12-x86_64.tar.gz

## 解压并移动
解压到/data/mysql/mysql-5.7.33
创建mysq数据目录 /data/mysql/mysql-data

## 创建mysql组和用户
```sh
groupadd mysql
useradd -r -g mysql mysql
```

## 参数配置
vim /etc/my.cnf

```conf
[mysqld]
bind-address=0.0.0.0
port=3306
user=mysql
basedir=/data/mysql/mysql-5.7.33/
datadir=/data/mysql/mysql-data
socket=/tmp/mysql.sock
character_set_server=utf8mb4
# Disabling symbolic-links is recommended to prevent assorted security risks
symbolic-links=0
# Settings user and group are ignored when systemd is used.
# If you need to run mysqld under a different user or group,
# customize your systemd unit file for mariadb according to the
# instructions in http://fedoraproject.org/wiki/Systemd

[mysqld_safe]
log-error=/data/mysql/mysql-data/mysql.err
pid-file=/data/mysql/mysql-data/mysql.pid

#
# include all files from the config directory
#
!includedir /etc/my.cnf.d
```

## 初始化mysql

```sh
cd /data/mysql/mysql-5.7.33/bin/
./mysqld --defaults-file=/etc/my.cnf --basedir=/data/mysql/mysql-5.7.33/ --datadir=/data/mysql/mysql-data/ --user=mysql --initialize
```

执行完有打印初始密码, 或者查看日志文件/data/mysql/mysql-data/mysql.err

## 启动mysql，并更改root 密码
拷贝服务文件
```sh
cp /data/mysql/mysql-5.7.33/support-files/mysql.server /etc/init.d/mysqld
```

启动：
```sh
service mysqld start
```

停止：
```sh
service mysqld stop
```

更改密码：

```sh
cd /data/mysql/mysql-5.7.33/bin
./mysql -u root -p
```

提示输入密码，把刚才复制的密码粘过来

然后执行修改，并刷新：

```sh
SET PASSWORD = PASSWORD('newpassword');

ALTER USER 'root'@'localhost' PASSWORD EXPIRE NEVER;

FLUSH PRIVILEGES;
```

如果想关闭mysql 执行

## 设置开机启动
chkconfig --add mysqld
chkconfig --list

## 配置环境变量

vim /etc/profile
```sh
export MYSQL_HOME=/data/mysql/mysql-5.7.33
export PATH=$PATH:$MYSQL_HOME/bin
```

## FAQ
### Host 'xxx.xxx.xxx.xxx' is not allowed to connect to this MySQL server

```sql
SELECT user, host FROM mysql.user WHERE user='root';
UPDATE mysql.user SET host='%' WHERE user='root';
FLUSH PRIVILEGES;
```


### ERROR 2002 (HY000): Can't connect to local MySQL server through socket '/tmp/mysql.sock' (2)
检查mysql.sock路径
