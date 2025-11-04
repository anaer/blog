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
