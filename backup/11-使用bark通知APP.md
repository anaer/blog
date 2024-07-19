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