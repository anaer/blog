## 查询每个db容量

```sql
SELECT 
    table_schema AS `Database`,
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS `Size_MB`
FROM 
    information_schema.tables
GROUP BY 
    table_schema
ORDER BY `Size_MB` DESC;
```


## 查询容量最大的10张表

```sql
SELECT 
    table_schema AS `Database`,
    table_name AS `Table`,
    ROUND((data_length + index_length) / 1024 / 1024, 2) AS `Size_MB`
FROM 
    information_schema.tables
WHERE 
    table_schema NOT IN ('information_schema', 'performance_schema', 'mysql', 'sys')  -- 排除系统数据库
ORDER BY 
    `Size_MB` DESC
LIMIT 10;
```



## Invalid default value for 'update_time'

MySQL 5.7.33

update_time 默认值 '0000-00-00 00:00:00'(零时间戳)，不满足sql_mode中的NO_ZERO_DATE而报错。

NO_ZERO_DATE：若设置该值，MySQL数据库不允许插入零日期，插入零日期会抛出错误而不是警告。

5.7版本默认严格模式

```sql
SHOW VARIABLES LIKE 'sql_mode';
```

```log
ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION
```

修改/etc/my.cnf

```conf
[mysqld]
sql_mode=ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION
```

重启mysql

## binlog复制权限

```sql
GRANT REPLICATION SLAVE ON *.* TO 'replica_user'@'%';
FLUSH PRIVILEGES;
SHOW GRANTS FOR 'replica_user'@'%';
```

## 开启binlog
```conf
[mysqld]
server-id=1
log-bin = /data/mysql/binlog/mysql-bin
binlog_format = ROW
expire_logs_days = 10
```

```sql
SHOW VARIABLES LIKE 'log_bin';
SHOW BINARY LOGS;
```

## 开启慢查询日志
```conf
[mysqld]
slow_query_log = ON
long_query_time = 1
slow_query_log_file=/data/mysql/mysql-slow.log

```