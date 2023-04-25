---
title: Python Dict
date: "2023-04-03T13:32:37.121Z"
tags:
  - python
last_updated: "2023-04-03T13:32:37.121Z"
---

## 判断字段Dict中是否存在key, 存在则替换

```python
dict = {'key1': 'value1', 'key2': 'value2'}
string = "key1"

if string in dict:
    string = dict[string]

print(string)
```