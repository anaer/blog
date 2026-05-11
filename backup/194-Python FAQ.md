### 'utf-8' codec can't encode character '\ud83d' in position 79: surrogates not allowed


```py
# 编码时直接忽略无效字符
safe_text = dirty_text.encode('utf-8', errors='ignore').decode('utf-8')
```