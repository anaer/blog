import os
import requests
import json
import random
"""
在仓库的 Settings > Secrets and variables > Actions 中添加密钥：
"""
def generate_summary(text):
    # 配置参数
    api_url = os.environ.get("API_URL")
    api_key = os.environ.get("API_KEY")
    api_model = os.environ.get("API_MODEL")

    # api_url = "https://models.inference.ai.azure.com/chat/completions"
    # api_key = ""
    # api_model = "gpt-4o"

    if not api_url or not api_model:
        return ""

    # 支持配置多个api_key和api_model
    if ',' in api_key:
        api_key = random.choice(api_key.split(','))

    if ',' in api_model:
        api_model = random.choice(api_model.split(','))

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # prompt = "请生成简洁完整的文本摘要，直接返回纯文本。确保涵盖所有主要要点，避免空泛表述或内容截断，不使用任何格式, 可以提出具体的修改建议，以提升内容的清晰度和逻辑性。"
    # prompt = "你是总结与优化建议生成器。你的任务是以简洁、完整的语句总结用户提供的文本，捕捉主要要点，并提供具体的优化建议，不使用Markdown格式，直接返回内容，避免空话或截断，以'本文介绍了'开头。换行展示优化建议。"
    prompt = "你是总结生成器。你的任务是以简洁、完整的语句总结用户提供的文本，捕捉主要要点，并指出存在的错误观点，不使用Markdown格式，直接返回内容，避免空话或截断，以'本文介绍了'开头。"
    
    payload = {
        "model": f"{api_model}",  # 或具体模型ID
        "messages": [
            {"role": "system", "content": f"{prompt}"},
            {"role": "user", "content": f"{text}"}
        ],
        "temperature": 0.5,
        "max_tokens": 1500
    }

    try:
        response = requests.post(
            url=api_url,
            headers=headers,
            data=json.dumps(payload),
            timeout=10
        )

        if response.status_code == 200:
            # print(response.json())
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
