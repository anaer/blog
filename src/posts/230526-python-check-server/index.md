---
title: Python检测服务器端口连通性
date: "2023-05-26T10:59:24.000Z"
description: Python检测服务器端口连通性
tags:
  - python
last_updated: "2023-05-26T10:59:24.000Z"
---

```toc
# This code block gets replaced with the TOC
```

## 检测服务器端口连通性

```python
import socket

def check_server(ip, port):
    # 创建套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 设置连接超时时间
    server_socket.settimeout(5)

    # 建立连接
    try:
        server_socket.connect((ip, port))
    except socket.error as err:
        print(f'{ip}:{port} 连接失败')
        return False
    else:
        print(f'{ip}:{port} 连接成功')
        return True

    finally:
        # 关闭套接字
        server_socket.close()

if __name__ == "__main__":
    ip1 = '127.0.0.1'
    port1 = 3306
    ip2 = '192.168.1.1'
    port2 = 80

    check_server(ip1, port1) # 连接成功
    check_server(ip2, port2) # 连接失败
```