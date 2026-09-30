## 开启事件调度器（Event Scheduler）：

```sql
SET GLOBAL event_scheduler = ON;
```

这个命令会立即启用事件调度器，而不需要重启 MySQL 服务。你可以通过以下命令来验证事件调度器是否已经启用：

```sql
SHOW VARIABLES LIKE 'event_scheduler';
```

如果结果是 `ON`，那么事件调度器已经成功启用。

### 注意事项：

1. `SET GLOBAL event_scheduler = ON;` 是一个全局变量的设置，通常需要管理员权限（`SUPER` 或 `SET` 权限）。
2. 如果你希望在 MySQL 启动时自动启用事件调度器，可以将配置文件中的 `event_scheduler` 设置为 `ON`：

   ```ini
   [mysqld]
   event_scheduler = ON
   ```

   这种方法需要重启 MySQL 服务来生效，但它确保每次启动时事件调度器都会启用。

### 禁用事件调度器：

  ```sql
  SET GLOBAL event_scheduler = OFF;
  ```


## 定时删除日表

```sql
-- 打开事件调度器（需要管理员权限）
SET GLOBAL event_scheduler = ON;

DELIMITER $$

CREATE EVENT IF NOT EXISTS ev_drop_daily_table
ON SCHEDULE EVERY 1 DAY
-- 从明天 02:10 开始第一次执行，之后每天同一时间执行
STARTS (CURRENT_DATE + INTERVAL 1 DAY + INTERVAL 2 HOUR + INTERVAL 10 MINUTE)
DO
BEGIN
    DECLARE tbl_name VARCHAR(64);

    -- 生成要删除的表名（这里为昨天的表），例如 t_table_2025-11-20
    SET tbl_name = CONCAT('t_table_', DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 DAY), '%Y-%m-%d'));

    -- 使用用户变量传入 PREPARE
    SET @sql_text = CONCAT('DROP TABLE IF EXISTS `', tbl_name, '`');

    PREPARE stmt FROM @sql_text;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END$$

DELIMITER ;

```

查询事件执行情况:

```sql
SELECT EVENT_NAME, LAST_EXECUTED
FROM information_schema.events
WHERE EVENT_NAME = 'ev_drop_daily_table';
```


定时删除历史数据:

```sql
CREATE EVENT IF NOT EXISTS `ev_delete_history` 
ON SCHEDULE EVERY 1 DAY 
STARTS (CURRENT_DATE + INTERVAL 1 DAY + INTERVAL 2 HOUR + INTERVAL 10 MINUTE)  
DO 
BEGIN  
    SET @sql_text = 'DELETE FROM t_history WHERE create_time < DATE_SUB(now(),INTERVAL 100 DAY);';  

    PREPARE stmt FROM @sql_text;  
    EXECUTE stmt;  
    DEALLOCATE PREPARE stmt;  
END
```