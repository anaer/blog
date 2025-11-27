
Ubuntu 20.04

## 安装

```sh
apt install sqlite3
```

## 连接数据库

```sh
sqlite3 your_db_file
```

## 命令

```sh
sqlite> .tables  # 显示所有表
sqlite> .schema table_name  # 显示指定表的结构
sqlite> .schema  # 显示所有表的结构
sqlite> .fullschema  # 显示所有表的完整结构 包含触发器等
```

```sh
sqlite> .mode column # 以列模式显示
sqlite> .headers on # 显示列名
```

```sh
sqlite> select * from t_ad limit 1;
id  type  name            sort  status  remark  created_at                  updated_at
--  ----  --------------  ----  ------  ------  --------------------------  ----------
1   0     abcd.011q2l.cn  0     0               2021-11-18 13:24:32.152277
```

```sh
sqlite> .mode list # 以列表模式显示
sqlite> .headers off # 不显示列名
```

```sh
sqlite> select * from t_ad limit 1;
1|0|abcd.011q2l.cn|0|0||2021-11-18 13:24:32.152277|
```


## 冲突时更新

```sql
INSERT INTO table_name(column1, column2) VALUES(value1, value2)
ON CONFLICT(column1) DO UPDATE SET
  column2 = excluded.column2;
```

column1 需要有唯一约束