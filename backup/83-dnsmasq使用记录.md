

---

### **DNSMASQ 使用记录**
**dnsmasq** 是一个轻量级、灵活的 DNS 转发和 DHCP 服务器工具，常用于本地 DNS 解析、网络管理、代理 DNS 请求或自定义域名映射。以下是其核心功能和使用方法：

---

### **1. 安装 dnsmasq**
#### **在 Linux 上安装**
- **Ubuntu/Debian**：
  ```bash
  sudo apt update && sudo apt install dnsmasq
  ```
- **CentOS/RHEL**：
  ```bash
  sudo yum install epel-release && sudo yum install dnsmasq
  ```

#### **在 macOS 上安装**
通过 Homebrew 安装：
```bash
brew install dnsmasq
```

#### **在 Windows 上**
DNSMASQ 本身是 Linux 工具，但可通过 **Windows Subsystem for Linux (WSL)** 或替代工具（如 **dnscrypt-proxy**）实现类似功能。

---

### **2. 配置文件**
默认配置文件路径：
- **Linux**：`/etc/dnsmasq.conf`
- **macOS**：`/usr/local/etc/dnsmasq.conf`

#### **基础配置示例**
```ini
listen-address=127.0.0.1
log-queries
log-facility=/var/log/dnsmasq.log
 
# 设置上游 DNS（默认会使用系统配置）
server=8.8.8.8    # Google Public DNS
server=1.1.1.1    # Cloudflare DNS

# 自定义域名解析（静态映射）
address=/example.com/192.168.1.100
address=/api.example.com/192.168.1.101
address=/test.example.com/192.168.1.102

# 允许多 IP 映射（同一域名指向多个 IP）
address=/multi-ips.com/192.168.1.200,192.168.1.201

# 读取 hosts 文件（可叠加 hosts 配置）
addn-hosts=/path/to/custom-hosts

# 启用 DHCP（如果需要）
interface=eth0      # 绑定的网络接口
dhcp-range=192.168.1.100,192.168.1.200,255.255.255.0,12h

# 缓存设置（加快重复查询）
cache-size=1000     # 缓存大小
```

---

### **3. 常见功能与场景**
#### **场景 1：自定义域名解析**
- **需求**：将 `dev.local` 解析到本地开发服务器 `192.168.1.50`。
- **配置**：
  ```ini
  address=/dev.local/192.168.1.50
  ```
- **测试**：
  ```bash
  nslookup dev.local  # 应返回 192.168.1.50
  ```

#### **场景 2：多 IP 负载均衡**
- **需求**：让 `service.example.com` 轮询解析到 `192.168.1.5` 和 `192.168.1.6`。
- **配置**：
  ```ini
  address=/service.example.com/192.168.1.5,192.168.1.6
  ```
- **行为**：DNSMASQ 会随机选择一个 IP 返回。

#### **场景 3：代理部分请求到指定 DNS**
- **需求**：将 `.cn` 域名解析到国内 DNS（如 `223.5.5.5`），其他域名用 `1.1.1.1`。
- **配置**：
  ```ini
  server=/cn/223.5.5.5
  server=/#/1.1.1.1    # 默认服务器
  ```

#### **场景 4：启用 DHCP**
- **需求**：为局域网设备分配 IP 和 DNS。
- **配置**：
  ```ini
  interface=eth0        # 网络接口
  dhcp-range=192.168.1.100,192.168.1.200,255.255.255.0,12h
  dhcp-option=option:dns-server,192.168.1.1  # 指定 DNS 服务器
  ```

---

### **4. 启动与测试**
#### **启动服务**
- **Linux**：
  ```bash
  sudo systemctl restart dnsmasq
  ```
- **macOS**（以命令行方式启动）：
  ```bash
  sudo dnsmasq -C /usr/local/etc/dnsmasq.conf
  ```

#### **设置 DNS 客户端**
将本地设备的 DNS 配置为 dnsmasq 的 IP（通常是 `127.0.0.1` 或局域网 IP）：
- **Windows**：
  - 进入网络设置 → 更改适配器选项 → 双击 DNS → 手动设置 `127.0.0.1`。
- **Linux/macOS**：
  修改 `/etc/resolv.conf`（或通过网络管理工具）：
  ```bash
  nameserver 127.0.0.1
  ```

#### **测试 DNS 解析**
```bash
# 查看解析结果
nslookup example.com 127.0.0.1

# 或使用 dig
dig @127.0.0.1 example.com
```

---

### **5. 常用参数说明**
| 参数                          | 说明                                                                 |
|-------------------------------|--------------------------------------------------------------------|
| `server`                      | 配置上游 DNS 服务器（支持条件匹配，如 `server=/domain.com/8.8.8.8`）。 |
| `address=/domain.com/1.2.3.4` | 将 `domain.com` 解析到指定 IP。                                     |
| `addn-hosts=/path/to/hosts`   | 读取额外的 hosts 文件（可叠加多个）。                               |
| `no-resolv`                   | 禁用 `/etc/resolv.conf` 中的默认 DNS 配置。                        |
| `listen-address=127.0.0.1`     | 指定监听的 IP 地址（默认仅本地）。                                 |
| `dhcp-range`                  | 配置 DHCP 地址池（适用于局域网服务器）。                           |

---

### **6. 日志与调试**
- **日志路径**：默认记录在 `/var/log/syslog`（Linux）或 `/var/log/dnsmasq.log`。
- **调试模式**：启动时添加 `-d` 参数查看详细日志：
  ```bash
  sudo dnsmasq -d -C /etc/dnsmasq.conf
  ```

---

### **7. 典型应用场景**
- **开发环境**：模拟生产环境的域名解析（如 `api.test` 指向本地服务）。
- **局域网管理**：提供 DHCP 和 DNS 服务，简化内网设备配置。
- **DNS 过滤**：屏蔽广告或恶意域名（通过 `address=/adserver.com/0.0.0.0`）。
- **跨平台测试**：模拟不同 DNS 策略（如强制使用特定 DNS 或多 IP 轮询）。

---

### **相关链接**

1. [dnsmasq 官方文档](http://www.thekelleys.org.uk/dnsmasq/docs/dnsmasq-man.html)。