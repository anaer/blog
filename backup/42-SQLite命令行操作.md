
Ubuntu 20.04

## 安装

```sh
apt install sqlite3
```

## 连接数据库

```sh
sqlite3 your_db_file
```

## 开启自动压缩

PRAGMA page_size 允许你设置数据库的页面大小，间接影响数据库的存储效率。较大的页面大小（例如 4096 或 8192 字节）有时能减少碎片并提高压缩效率。
```sql
PRAGMA page_size = 4096;
```
PRAGMA auto_vacuum 设置，它可以在每次删除数据时自动压缩数据库，减少未使用空间。

```sql
PRAGMA auto_vacuum = FULL;
```

FULL：表示启用自动压缩，每次删除数据时，SQLite 会自动清理空白空间。

INCREMENTAL：允许你手动触发压缩。

NONE：禁用自动压缩。

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

## 添加字段

```sql
ALTER TABLE users ADD COLUMN phone_number TEXT NOT NULL;
```

## 冲突时更新

```sql
INSERT INTO table_name(column1, column2) VALUES(value1, value2)
ON CONFLICT(column1) DO UPDATE SET
  column2 = excluded.column2;
```

column1 需要有唯一约束