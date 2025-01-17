## 安装依赖

```pip
pip install markdown beautifulsoup4
```

## 代码
```python
import markdown
from bs4 import BeautifulSoup

# Markdown 文本
md_text = """
# 标题 1
这是一个段落。

- 列表项 1
- 列表项 2

**加粗文本**
"""

# 将 Markdown 转换为 HTML
html = markdown.markdown(md_text)

# 使用 BeautifulSoup 提取纯文本
soup = BeautifulSoup(html, "html.parser")
plain_text = soup.get_text()

print(plain_text)
```