# Redis 慢日志（Slow Log）使用与配置

Redis 慢日志是 Redis 用来记录命令执行时间的日志系统。通过慢日志，您可以快速定位 Redis 服务器中耗时的命令，帮助分析性能瓶颈。

## 配置慢日志

Redis 提供了两种配置慢日志的方法：

1. **修改 `redis.conf` 配置文件**
2. **使用 `CONFIG SET` 动态修改配置**

### 配置参数

* `slowlog-log-slower-than`：设置执行时间超过多少微秒的命令进行记录。例如，`1000` 微秒（即 1 毫秒）。
* `slowlog-max-len`：设置最大保存的慢日志条数。当慢日志队列大小超过该配置值时，最旧的日志将被删除。

### 示例配置

* 通过 `CONFIG SET` 配置慢日志记录：

```bash
CONFIG SET slowlog-log-slower-than 10000   # 记录执行时间超过 10000 微秒（即 10 毫秒）的命令
CONFIG SET slowlog-max-len 128            # 设置最多保存 128 条慢日志记录
```

### 查询配置是否生效

可以通过 `CONFIG GET` 查询当前的慢日志配置：

```bash
127.0.0.1:6379> CONFIG GET slowlog-log-slower-than
1) "slowlog-log-slower-than"
2) "10000"

127.0.0.1:6379> CONFIG GET slowlog-max-len
1) "slowlog-max-len"
2) "128"
```

## 查询慢日志

使用 `SLOWLOG GET` 命令查询慢日志，默认情况下查询所有慢查询命令。您也可以通过参数指定返回的记录数。

### 示例查询：

```bash
127.0.0.1:6379> SLOWLOG GET 2
1481
1764642944
1092820
keys
abc*
```

### 输出说明：

1. **唯一日志标识符**：Redis 会为每条慢查询日志分配一个唯一的 ID，重启 Redis 后 ID 会重置。
2. **执行时间点**：以 UNIX 时间戳格式表示，记录命令执行的时间。
3. **查询执行时间**：命令的执行时间，单位为微秒。
4. **执行的命令**：命令及其参数，以数组形式显示。

### 查询慢日志数量

使用 `SLOWLOG LEN` 命令查询当前慢日志的数量：

```bash
127.0.0.1:6379> SLOWLOG LEN
(integer) 128
```

### 重置慢日志

使用 `SLOWLOG RESET` 命令清空所有慢日志记录：

```bash
127.0.0.1:6379> SLOWLOG RESET
OK
```