## 冲突时更新

```sql
INSERT INTO table_name(column1, column2) VALUES(value1, value2)
ON CONFLICT(column1) DO UPDATE SET
  column2 = excluded.column2;
```

column1 需要有唯一约束