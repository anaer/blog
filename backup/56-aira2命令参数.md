
`aria2c --help=#all`

| 参数                                | 说明                                        |
| ----------------------------------- | ------------------------------------------- |
| -c, --continue[=true, false]        | 断点续传                                    |
| -o, --out=FILE                      | 输出文件                                    |
| -d, --dir=DIR                       | 保存文件路径，绝对路径                      |
| -l, --log=LOG                       | 日志文件                                    |
| -s, --split=N                       | 并发下载数                                  |
| -j, --max-concurrent-downloads=N    | 一个 URL 的最大并发下载数                   |
| -k, --min-split-size                | 每个 split 最小 size,源文件按这个拆分成多个 |
| -x, --max-connection-per-server=NUM | 一个 server 的最大并发下载数                |
| --no-conf                           | Disable loading aria2.conf file.            |
| -t, --timeout=SEC                   | 设置超时时间为SEC秒, 默认值:60              |
| --connect-time=SEC                  | 设置建立连接超时时间为SEC秒, 默认值:60      |
| --max-tries                         | 超时后尝试次数                              |
| --stop=SEC                          | SEC 秒后自动结束                            |
| --allow-overwrite=true              | 覆盖                                        |
| --enable-http-keep-alive            | http 长连接                                 |
| --log-level                         | 日志级别                                    |
| -u, --max-upload-limit=SPEED        | 限速                                        |
