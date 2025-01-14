vim script/free.py

```py
import subprocess
from bark import send_bark_notification

# 执行 free -m 命令并获取结果
result = subprocess.run(['free', '-m'], stdout=subprocess.PIPE)

# 处理结果并提取 total 和 available 两项
lines = result.stdout.decode().split('\n')
headers = lines[0].split()
values = lines[1].split()

# 提取 total 和 available 两项
total = values[headers.index('total')+1]
available = values[headers.index('available')+1]

# 打印结果
content = f"Total Memory: {total} MB \nAvailable Memory: {available} MB"
#print(content)
send_bark_notification("服务器内存信息", content)

```


`crontab -e`  配置定时任务

```
# 每小时通知服务器内存信息
0 * * * * python3 script/free.py
```

