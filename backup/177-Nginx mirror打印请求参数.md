Python 3.6.8

## app.py

```python
import logging
from flask import Flask, request

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log", encoding="utf-8")
    ]
)

@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def handle_request(path):
    logging.info("---------------------------------------------")

    msg = "\n"

    msg = msg + f"{request.method} {request.headers['X-Forwarded-Proto']}://{request.headers['Host']}{request.headers['X-Mirror-Path']}" + "\n"

    exclude_headers = {"Accept-Encoding", "Host", "Accept", "X-Mirror-Path", "Connection", "Content-Length", "X-Forwarded-Proto"}
    filtered_headers = {k: v for k, v in request.headers.items() if k not in exclude_headers}
    for k, v in filtered_headers.items():
        msg = msg + f"{k}: {v}" + "\n"

    if request.args:
        args_str = "&".join([f"{key}={value}" for key, value in request.args.items()])
        msg = msg + args_str

    msg = msg + "\n"

    if request.form:
        form_str = "&".join([f"{key}={value}" for key, value in request.form.items()])
        msg = msg + form_str

    if request.is_json:
        msg = msg + str(request.get_json())
    else:
        msg = msg + request.data.decode('utf-8')

    logging.info(msg)

    return "Request received and logged"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9876, debug=True)

```


## pm2.json

```json
{
  "apps": [
    {
      "name": "mirrorlog",
      "script": "python3 app.py",
      "instances": 1,
      "autorestart": true,
      "watch": ["app.py"],
      "log_date_format": "YYYY-MM-DD HH:mm Z",
      "merge_logs": true,
      "error_file": "pm2.log",
      "out_file": "pm2.log"
    }
  ]
}
```


## nginx

```conf
location / {
    proxy_pass http://backend;

    mirror /mirrorlog;
    mirror_request_body on;
}

 # 定义镜像请求的处理路径
location = /mirrorlog {
    internal;  # 确保这个 location 只作为内部请求处理
    proxy_pass http://127.0.0.1:9876;  # 代理请求到镜像后端

    # 确保传递所有请求头
    proxy_set_header Host $host;  # 保留原始请求中的 Host 头
    proxy_set_header X-Real-IP $remote_addr;  # 保留客户端 IP
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;  # 保留原始的 X-Forwarded-For 头
    proxy_set_header X-Forwarded-Proto $scheme;  # 保留请求协议（http 或 https）
    proxy_set_header User-Agent $http_user_agent;  # 保留请求的 User-Agent 头
    proxy_set_header Accept $http_accept;  # 保留请求的 Accept 头
    proxy_set_header Content-Type $http_content_type;  # 保留请求的 Content-Type 头

    proxy_set_header X-Mirror-Path $request_uri;  # 保留原始路径（包括查询参数）
}
```