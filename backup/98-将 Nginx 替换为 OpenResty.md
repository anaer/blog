## 将 Nginx 替换为 OpenResty
OpenResty 是基于 Nginx 核心并集成了 LuaJIT、`ngx_lua` 模块等功能的增强版本。

系统:  Ubuntu 20.04.6 LTS (GNU/Linux 5.4.0-187-generic x86_64)
---

### 步骤 1：备份现有 Nginx 配置
1. **备份配置文件**:
   ```bash
   sudo cp -r /etc/nginx /etc/nginx-backup
   ```

2. **记录当前版本和模块**:
   ```bash
   nginx -V
   ```
   输出会显示 Nginx 的版本和编译参数，记录下来以便后续对比。

---

### 步骤 2：卸载现有 Nginx

  ```bash
  sudo systemctl stop nginx
  sudo apt remove nginx nginx-common nginx-full
  sudo apt autoremove
  ```
---

### 步骤 3：安装 OpenResty

  1. 添加 OpenResty 仓库：
     ```bash
     sudo apt update
     sudo apt install -y curl gnupg2 ca-certificates lsb-release
     wget -qO - https://openresty.org/package/pubkey.gpg | sudo apt-key add -
     echo "deb http://openresty.org/package/ubuntu $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/openresty.list
     sudo apt update
     ```
  2. 安装 OpenResty：
     ```bash
     sudo apt install -y openresty
     ```

  3. 检查安装：
   ```bash
   systemctl status openresty
   openresty -v
   ```

---

### 步骤 4：迁移 Nginx 配置
1. **复制备份的配置文件**:
    可以直接复制, 或者手动将需要的配置添加的新配置文件中
     ```bash
     sudo cp -r /etc/nginx-backup/* /etc/openresty/
     ```

2. **调整路径**:
   - 检查 `nginx.conf` 中的路径（如 `access_log`、`error_log`、`root` 等），确保与 OpenResty 的安装路径一致。
   - 默认情况下，OpenResty 使用 `/usr/local/openresty/nginx/` 作为工作目录。

3. **验证配置**:
   ```bash
   openresty -t
   ```
---

### 步骤 5：启动 OpenResty
1. **启动服务**:
     ```bash
     sudo systemctl start openresty
     sudo systemctl enable openresty
     ```

2. **检查运行状态**:
   ```bash
   ps aux | grep openresty
   curl http://localhost
   ```

---

### 步骤 6：验证 OpenResty 功能
OpenResty 的主要优势是集成了 `ngx_lua` 模块，可以通过简单的 Lua 脚本测试是否生效。

#### 测试配置
在 `nginx.conf` 中添加：
```nginx
http {
    server {
        listen 80;
        server_name example.com;

        location /test {
            content_by_lua_block {
                ngx.say("Hello from OpenResty!")
            }
        }
    }
}
```

#### 重载并测试
```bash
sudo openresty -s reload
curl http://localhost/test
```
输出应为：
```
Hello from OpenResty!
```

#### 替换Nginx
添加nginx软链接, 按nginx命令使用

```bash
ln -s /usr/bin/openresty /usr/bin/nginx
```
---


### 清理
如果确认 OpenResty 运行正常，可以删除备份或旧的 Nginx 文件：
```bash
sudo rm -rf /etc/nginx-backup
```

---
