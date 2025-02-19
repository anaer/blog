import os
import requests
import json
"""
在仓库的 Settings > Secrets and variables > Actions 中添加密钥：
"""
def generate_summary(text):
    # 配置参数
    api_url = os.environ.get("API_URL")
    api_key = os.environ.get("API_KEY")
    api_model = os.environ.get("API_MODEL")

    if not api_url or not api_model:
        return ""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": f"{model}",  # 或具体模型ID
        "messages": [
            {"role": "system", "content": "你是一个专业文本摘要生成器"},
            {"role": "user", "content": f"请用中文生成以下技术文档的摘要，控制在100字内：\n{text}"}
        ],
        "temperature": 0.5,
        "max_tokens": 150
    }

    try:
        response = requests.post(
            url=endpoint,
            headers=headers,
            data=json.dumps(payload),
            timeout=10
        )

        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            print(f"请求失败：{response.status_code} - {response.text}")
            return ""

    except Exception as e:
        print(f"发生异常：{str(e)}")
        return ""

# 使用示例
article_content = """
GitHub Actions的配置需要包含工作流触发器、任务定义和运行环境。
关键参数包括：runs-on指定运行器类型，steps定义执行步骤，uses引用预构建动作。
示例配置部署Node.js应用：
name: Node.js CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-node@v3
      with:
        node-version: 18.x
"""

# print(generate_summary(article_content))
