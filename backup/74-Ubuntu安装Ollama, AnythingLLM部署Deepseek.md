
## ollama安装

可以按照官方的安装手册进行安装, 这里仅记录自己的操作步骤方便记忆.
[Linux安装ollama手册](https://github.com/ollama/ollama/blob/main/docs/linux.md)

PS: 以Ubuntu 14.04.5 LTS为例

### 下载安装[ollama v0.5.7](https://github.com/ollama/ollama/releases/tag/v0.5.7) ollama-linux-amd64.tgz

将压缩包解压到/usr目录, 可以不用再配置环境变量直接调用
```sh
sudo tar -C /usr -xzf ollama-linux-amd64.tgz
```

查询压缩包的结构
```log
# tar -tvf ollama-linux-amd64.tgz
drwxr-xr-x root/root         0 2025-01-17 00:47 ./
drwxr-xr-x root/root         0 2025-01-17 00:47 ./bin/
-rwxr-xr-x root/root  30064856 2025-01-17 00:47 ./bin/ollama
drwxr-xr-x root/root         0 2025-01-17 00:47 ./lib/
drwxr-xr-x root/root         0 2025-01-17 00:52 ./lib/ollama/
lrwxrwxrwx root/root         0 2025-01-17 00:52 ./lib/ollama/libcudart.so.12 -> libcudart.so.12.4.127
-rwxr-xr-x root/root 441938896 2025-01-17 00:52 ./lib/ollama/libcublasLt.so.12.4.5.8
lrwxrwxrwx root/root         0 2025-01-17 00:49 ./lib/ollama/libcudart.so.11.0 -> libcudart.so.11.3.109
lrwxrwxrwx root/root         0 2025-01-17 00:49 ./lib/ollama/libcublas.so.11 -> libcublas.so.11.5.1.109
lrwxrwxrwx root/root         0 2025-01-17 00:52 ./lib/ollama/libcublas.so.12 -> ./libcublas.so.12.4.5.8
-rwxr-xr-x root/root    619192 2025-01-17 00:52 ./lib/ollama/libcudart.so.11.3.109
-rwxr-xr-x root/root 109604768 2025-01-17 00:52 ./lib/ollama/libcublas.so.12.4.5.8
-rwxr-xr-x root/root    707904 2025-01-17 00:52 ./lib/ollama/libcudart.so.12.4.127
-rwxr-xr-x root/root 263770264 2025-01-17 00:49 ./lib/ollama/libcublasLt.so.11.5.1.109
lrwxrwxrwx root/root         0 2025-01-17 00:49 ./lib/ollama/libcublasLt.so.11 -> libcublasLt.so.11.5.1.109
drwxr-xr-x root/root         0 2025-01-17 01:15 ./lib/ollama/runners/
drwxr-xr-x root/root         0 2025-01-17 01:03 ./lib/ollama/runners/cuda_v11_avx/
-rwxr-xr-x root/root   9885296 2025-01-17 01:03 ./lib/ollama/runners/cuda_v11_avx/ollama_llama_server
-rwxr-xr-x root/root 979085896 2025-01-17 01:01 ./lib/ollama/runners/cuda_v11_avx/libggml_cuda_v11.so
drwxr-xr-x root/root         0 2025-01-17 01:17 ./lib/ollama/runners/rocm_avx/
-rwxr-xr-x root/root   9930480 2025-01-17 01:17 ./lib/ollama/runners/rocm_avx/ollama_llama_server
-rwxr-xr-x root/root 451342832 2025-01-17 01:15 ./lib/ollama/runners/rocm_avx/libggml_rocm.so
drwxr-xr-x root/root         0 2025-01-17 01:01 ./lib/ollama/runners/cuda_v12_avx/
-rwxr-xr-x root/root   9873136 2025-01-17 01:01 ./lib/ollama/runners/cuda_v12_avx/ollama_llama_server
-rwxr-xr-x root/root 1237676328 2025-01-17 00:59 ./lib/ollama/runners/cuda_v12_avx/libggml_cuda_v12.so
drwxr-xr-x root/root          0 2025-01-17 00:47 ./lib/ollama/runners/cpu_avx2/
-rwxr-xr-x root/root    9860720 2025-01-17 00:47 ./lib/ollama/runners/cpu_avx2/ollama_llama_server
drwxr-xr-x root/root          0 2025-01-17 00:47 ./lib/ollama/runners/cpu_avx/
-rwxr-xr-x root/root    9840240 2025-01-17 00:47 ./lib/ollama/runners/cpu_avx/ollama_llama_server
-rwxr-xr-x root/root  121866104 2025-01-17 00:49 ./lib/ollama/libcublas.so.11.5.1.109
lrwxrwxrwx root/root          0 2025-01-17 00:52 ./lib/ollama/libcublasLt.so.12 -> ./libcublasLt.so.12.4.5.8
```

### 启动ollama
长期使用可以按照安装手册, 添加ollama到系统服务中.

OLLAMA_HOST默认为127.0.0.1, 如果非本机访问, 需修改OLLAMA_HOST设置

设置环境变量

```sh
export OLLAMA_HOST=0.0.0.0
```

```sh
nohup /usr/bin/ollama serve &
```

### 命令执行

**查询本地已下载的模型**

```sh
$ ollama list
NAME                ID              SIZE      MODIFIED
deepseek-r1:1.5b    a42b25d8c10a    1.1 GB    24 hours ago
```

**拉取模型**

```sh
ollama pull deepseek-r1:1.5b
```

**启动模型**
直接在命令行进行交互

```sh
$ ollama run deepseek-r1:1.5b
>>> 你是什么
<think>

</think>

您好！我是由中国的深度求索（DeepSeek）公司开发的智能助手DeepSeek-R1。如您有任何任何问题，我会尽我所能为您提供帮助。
```


### nginx配置

```
location /ollama/ {
    proxy_pass http://127.0.0.1:11434/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
}
```

## 本地客户端 [Cherry Studio](https://github.com/CherryHQ/cherry-studio/releases/tag/v0.9.21)

设置->模型服务->Ollama
API密钥: 空
API地址: http://mydomain.com/ollama/v1/
添加模型: deepseek-r1:1.5b

在助手页设置选择默认模型为上述模型 即可进行聊天

![Image](https://github.com/user-attachments/assets/2127d6b0-7229-44d0-bac7-4b31557e325e)

![Image](https://github.com/user-attachments/assets/f4f0d98d-b353-4367-a7c5-f02c2a2eda0e)


## anythingllm
要求: 服务器安装docker

install.sh 安装脚本

```sh
export STORAGE_LOCATION=$HOME/anythingllm && \
mkdir -p $STORAGE_LOCATION && \
touch "$STORAGE_LOCATION/.env" && \
docker run -d -p 3001:3001 \
--cap-add SYS_ADMIN \
-v ${STORAGE_LOCATION}:/app/server/storage \
-v ${STORAGE_LOCATION}/.env:/app/server/.env \
-e STORAGE_DIR="/app/server/storage" \
mintplexlabs/anythingllm
```

执行该脚本会在当前用户目录下anythingllm目录安装服务

### nginx配置

```
location / {
    proxy_pass http://127.0.0.1:3001;
}
```

### 配置AnythingLLM

首次访问时按导引进行模型配置, 配置URL后会自动获取支持的模型列表

1. 人工智能提供商 -> LLM首选项
LLM提供商: Ollama
Ollama Model: deepseek-r1:1.5b
Ollama Base URL: http://mydomain.com/ollama

### 新工作区

创建工作区后, 可通过上传图标按钮, 上传自有文档添加到工作区中
也可以连接GitHub Repo, GitLab Repo, YouTube Transcript, Bulk Link Scraper, Confluence

![Image](https://github.com/user-attachments/assets/0d4acaa7-ed97-4576-84f4-25099e85abae)

### 嵌入式对话

可新增嵌入式对话, 按需配置后(需选择工作区), Show Code复制代码, 将代码复制到空白html的<body></body>内, 可直接打开html测试

![Image](https://github.com/user-attachments/assets/3d7f9e47-9d59-4e7e-adfe-4c84b00c08e2)

## Deepseek模型 硬件要求

### DeepSeek-R1-1.5B
CPU: 最低 4 核（推荐 Intel/AMD 多核处理器）
内存: 8GB+
硬盘: 3GB+ 存储空间（模型文件约 1.5-2GB）
显卡: 非必需（纯 CPU 推理），若 GPU 加速可选 4GB+ 显存（如 GTX 1650）
场景：低资源设备部署，如树莓派、旧款笔记本、嵌入式系统或物联网设备

### DeepSeek-R1-7B
CPU: 8 核以上（推荐现代多核 CPU）
内存: 16GB+
硬盘: 8GB+（模型文件约 4-5GB）
显卡: 推荐 8GB+ 显存（如 RTX 3070/4060）
场景：中小型企业本地开发测试、中等复杂度 NLP 任务，例如文本摘要、翻译、轻量级多轮对话系统

### DeepSeek-R1-671B
CPU: 64 核以上（服务器集群）
内存: 512GB+
硬盘: 300GB+
显卡: 多节点分布式训练（如 8x A100/H100）
场景：超大规模 AI 研究、通用人工智能（AGI）探索

## 相关链接

[ollama](https://github.com/ollama/ollama)
[ollama常用模型](https://github.com/ollama/ollama/tree/main?tab=readme-ov-file#model-library)
[ollama模型列表](https://ollama.com/library)
[DeepSeek技术专题：部署教程、一线玩法、原理解析](https://cloud.tencent.com/developer/special/deepseek)
[TI-ONE 训练平台 快速部署和体验 DeepSeek 系列模型](https://cloud.tencent.com/document/product/851/115962?from=25520)
