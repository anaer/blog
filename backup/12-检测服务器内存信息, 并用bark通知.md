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

vim script/bark.py

```py
import requests
import sys
from urllib.parse import quote

# Bark 的通知 API xxx为token信息
BARK_API = "https://api.day.app/xxx"

def send_bark_notification(param1, param2):
 # quote默认safe='/', 不进行处理, 如需处理将safe置空
 title = quote(param1, safe="")
 content = quote(param2, safe="")
 print(title, content)
 url = f"{BARK_API}/{title}/{content}"
 print(url)
 response = requests.get(url)
 if response.status_code == 200:
     print("发送 Bark 通知成功")
 else:
     print(f"发送 Bark 通知失败: {response.text}")

if __name__ == "__main__":
 if len(sys.argv) > 2:
     title = sys.argv[1]
     content = sys.argv[2]
     send_bark_notification(title, content)
```
