
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