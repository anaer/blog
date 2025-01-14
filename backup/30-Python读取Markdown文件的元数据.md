## 使用PyYAML

```python
# pip install pyyaml
import yaml

def extract_metadata(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否有 YAML Front Matter
    if content.startswith('---'):
        parts = content.split('---', 2)  # 分割 YAML 部分
        if len(parts) > 1:
            yaml_content = parts[1]
            metadata = yaml.safe_load(yaml_content)  # 解析 YAML
            return metadata
    return {}

# 示例：读取 Markdown 文件元数据
metadata = extract_metadata('README.md')
print(metadata)
```

## 使用frontmatter解析

```python
# pip install python-frontmatter
import frontmatter

def extract_metadata_with_frontmatter(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)  # 解析 Markdown 文件
    return post.metadata

# 示例：读取 Markdown 文件元数据
metadata = extract_metadata_with_frontmatter('README.md')
print(metadata)
```