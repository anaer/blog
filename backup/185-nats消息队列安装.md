
## 目录

```tree
/etc/nats
  - docker-compose.yml
  - nats.conf
  - certs/
    - ca.pem
    - client-cert.pem
    - client-key.pem
    - server-cert.pem
    - server-key.pem
```

### docker-compose.yml

```yaml
services:
  nats:
      image: nats:latest
      ports:
        - "4222:4222"
        - "8222:8222" # 管理端口
      volumes:
        - ./nats.conf:/etc/nats/nats.conf:ro
        - ./certs:/etc/nats/certs:ro
      command: "-c /etc/nats/nats.conf" # 明确指定配置文件
```

### nats.conf

```conf
port: 4222
tls {
  cert_file: "/etc/nats/certs/server-cert.pem"
  key_file:  "/etc/nats/certs/server-key.pem"
  ca_file:   "/etc/nats/certs/ca.pem"
  verify:    true  # 开启 mTLS 验证客户端
  min_version: "1.2" # 设置最低TLS版本以保证安全
}
```

## mkcert 生成本地证书

CentOS安装mkcert

```sh
# mkcert 依赖 nss-tools 来操作系统的证书信任库
yum install nss-tools -y

# 下载二进制文件 (以 v1.4.4 为例，请根据需要检查最新版)
wget -O mkcert https://github.com/FiloSottile/mkcert/releases/download/v1.4.4/mkcert-v1.4.4-linux-amd64

# 赋予执行权限并移动到系统路径
chmod +x mkcert
sudo mv mkcert /usr/local/bin/
```


```sh
# 初始化本地CA证书并安装到系统信任存储中
mkcert -install

ls /root/.local/share/mkcert
# rootCA-key.pem
# rootCA.pem
```

```sh
cd /etc/nats/certs
cp /root/.local/share/mkcert/rootCA.pem ca.pem

# 生成证书，包含 localhost、127.0.0.1 等
mkcert -cert-file server-cert.pem -key-file server-key.pem localhost 127.0.0.1 nats-server

# 生成客户端证书
mkcert -client -cert-file client-cert.pem -key-file client-key.pem nats-client
```

## 测试脚本

### sub.py

```py
# pip install nats-py
import asyncio
import nats
import ssl

async def main():
    # 1. 创建 SSL 上下文
    ssl_ctx = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)

    # 2. 加载 mkcert 的根证书 (rootCA.pem)
    # 这样 Python 才能信任 NATS 服务端出示的自签名证书
    ssl_ctx.load_verify_locations(cafile="ca.pem")

    ssl_ctx.load_cert_chain(
        certfile="client-cert.pem",
        keyfile="client-key.pem"
    )

    # 连接到 NATS 服务器
    nc = await nats.connect("tls://127.0.0.1:4222", tls=ssl_ctx)

    # 创建一个订阅对象
    sub = await nc.subscribe("subject_test")

    print("订阅者已启动，等待消息...")

    # 处理接收到的消息
    async for msg in sub.messages:
        data = msg.data.decode()
        print(f"收到消息: '{data}' 在主题: '{msg.subject}'")

if __name__ == '__main__':
    asyncio.run(main())

```

### pub.py

```py
import asyncio
import nats
import ssl

async def main():
    # 1. 创建 SSL 上下文
    ssl_ctx = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)

    # 2. 加载 mkcert 的根证书 (rootCA.pem)
    # 这样 Python 才能信任 NATS 服务端出示的自签名证书
    ssl_ctx.load_verify_locations(cafile="ca.pem")

    ssl_ctx.load_cert_chain(
        certfile="client-cert.pem",
        keyfile="client-key.pem"
    )

    # 连接到 NATS 服务器
    nc = await nats.connect("tls://127.0.0.1:4222", tls=ssl_ctx)

    # 发布消息到主题
    await nc.publish("subject_test", b"Hello NATS!")
    print("消息已发布: Hello NATS!")

    # 关闭连接
    await nc.close()

if __name__ == '__main__':
    asyncio.run(main())

```