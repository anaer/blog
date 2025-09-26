
## 索引管理

### 新增索引
可以在新增索引时, 自定义分词器custom_pattern

```rest
PUT {{myes}}/my_index
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 1,
    "analysis": {
      "analyzer": {
        "custom_pattern": {
          "type": "pattern",
          "pattern": "\\|"
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "standard"
      },
      "content": {
        "type": "text",
        "analyzer": "standard"
      },
      "timestamp": {
        "type": "date"
      }
    }
  }
}
```



## Elasticsearch 常见分词器及其主要用途：

|内置分词器|作用|
|---|---|
|Standard|默认分词器，按单词分类并进行小写处理|
|Simple|按照非字母切分，然后去除非字母并进行小写处理|
|Stop|按照停用词过滤并进行小写处理，停用词包括the、a、is|
|Whitespace|按照空格切分, 不转小写|
|Language|提供了多种常见语言的分词器|
|Pattern|按照正则表达式进行分词，默认是\W+ ,代表非字母|
|Keyword|不进行分词，作为一个整体输出|
|Customer| 自定义分词器|


请求链接:
```rest
GET {{myes}}/my_index/_analyze
```

### **Standard Tokenizer**
**描述**：标准分词器，对文本进行基本的分词处理。
**示例**：
```json
{
  "analyzer": "standard",
  "text": "Hello, this is a document to be analyzed."
}
```

```json
{
  "tokens": [
    {
      "token": "hello",
      "start_offset": 0,
      "end_offset": 5,
      "type": "<ALPHANUM>",
      "position": 0
    },
    {
      "token": "this",
      "start_offset": 7,
      "end_offset": 11,
      "type": "<ALPHANUM>",
      "position": 1
    },
    {
      "token": "is",
      "start_offset": 12,
      "end_offset": 14,
      "type": "<ALPHANUM>",
      "position": 2
    },
    {
      "token": "a",
      "start_offset": 15,
      "end_offset": 16,
      "type": "<ALPHANUM>",
      "position": 3
    },
    {
      "token": "document",
      "start_offset": 17,
      "end_offset": 25,
      "type": "<ALPHANUM>",
      "position": 4
    },
    {
      "token": "to",
      "start_offset": 26,
      "end_offset": 28,
      "type": "<ALPHANUM>",
      "position": 5
    },
    {
      "token": "be",
      "start_offset": 29,
      "end_offset": 31,
      "type": "<ALPHANUM>",
      "position": 6
    },
    {
      "token": "analyzed",
      "start_offset": 32,
      "end_offset": 40,
      "type": "<ALPHANUM>",
      "position": 7
    }
  ]
}
```

**示例2**
```json
{
  "analyzer": "standard",
  "text": "aaa|bbb|ccc"
}
```

```json
{
  "tokens": [
    {
      "token": "aaa",
      "start_offset": 0,
      "end_offset": 3,
      "type": "<ALPHANUM>",
      "position": 0
    },
    {
      "token": "bbb",
      "start_offset": 4,
      "end_offset": 7,
      "type": "<ALPHANUM>",
      "position": 1
    },
    {
      "token": "ccc",
      "start_offset": 8,
      "end_offset": 11,
      "type": "<ALPHANUM>",
      "position": 2
    }
  ]
}
```

**示例3**
```json
{
  "analyzer": "standard",
  "text": "中文|汉字|测试"
}
```

```json
{
  "tokens": [
    {
      "token": "中",
      "start_offset": 0,
      "end_offset": 1,
      "type": "<IDEOGRAPHIC>",
      "position": 0
    },
    {
      "token": "文",
      "start_offset": 1,
      "end_offset": 2,
      "type": "<IDEOGRAPHIC>",
      "position": 1
    },
    {
      "token": "汉",
      "start_offset": 3,
      "end_offset": 4,
      "type": "<IDEOGRAPHIC>",
      "position": 2
    },
    {
      "token": "字",
      "start_offset": 4,
      "end_offset": 5,
      "type": "<IDEOGRAPHIC>",
      "position": 3
    },
    {
      "token": "测",
      "start_offset": 6,
      "end_offset": 7,
      "type": "<IDEOGRAPHIC>",
      "position": 4
    },
    {
      "token": "试",
      "start_offset": 7,
      "end_offset": 8,
      "type": "<IDEOGRAPHIC>",
      "position": 5
    }
  ]
}

```

### **Simple Tokenizer**
**描述**：简单分词器，根据非字母数字字符进行分词，适用于多语言文本。主要特点是根据短横线、中横线、下划线、逗号、冒号、分号等常见符号进行分词。它不进行任何大小写转换或其他复杂处理。
**示例**
```json
{
  "analyzer": "simple",
  "text": "中文|汉字|测试"
}
```


```json
{
  "tokens": [
    {
      "token": "中文",
      "start_offset": 0,
      "end_offset": 2,
      "type": "word",
      "position": 0
    },
    {
      "token": "汉字",
      "start_offset": 3,
      "end_offset": 5,
      "type": "word",
      "position": 1
    },
    {
      "token": "测试",
      "start_offset": 6,
      "end_offset": 8,
      "type": "word",
      "position": 2
    }
  ]
}

```

### **Whitespace Tokenizer**
**描述**：根据空格进行分词，忽略标点符号。
**示例**：
```json
{
  "analyzer": "whitespace",
  "text": "Hello, this is a document to be analyzed."
}
```

```json
{
  "tokens": [
    {
      "token": "Hello,",
      "start_offset": 0,
      "end_offset": 6,
      "type": "word",
      "position": 0
    },
    {
      "token": "this",
      "start_offset": 7,
      "end_offset": 11,
      "type": "word",
      "position": 1
    },
    {
      "token": "is",
      "start_offset": 12,
      "end_offset": 14,
      "type": "word",
      "position": 2
    },
    {
      "token": "a",
      "start_offset": 15,
      "end_offset": 16,
      "type": "word",
      "position": 3
    },
    {
      "token": "document",
      "start_offset": 17,
      "end_offset": 25,
      "type": "word",
      "position": 4
    },
    {
      "token": "to",
      "start_offset": 26,
      "end_offset": 28,
      "type": "word",
      "position": 5
    },
    {
      "token": "be",
      "start_offset": 29,
      "end_offset": 31,
      "type": "word",
      "position": 6
    },
    {
      "token": "analyzed.",
      "start_offset": 32,
      "end_offset": 41,
      "type": "word",
      "position": 7
    }
  ]
}

```

### **Keyword Tokenizer**
**描述**：保持输入的文本作为单个分词。
**示例**：
```json
{
  "analyzer": "keyword",
  "text": "Hello, this is a document to be analyzed."
}
```

```json
{
  "tokens": [
    {
      "token": "Hello, this is a document to be analyzed.",
      "start_offset": 0,
      "end_offset": 41,
      "type": "word",
      "position": 0
    }
  ]
}

```

### **Pattern Tokenizer**
**描述**: 正则分词器, 创建索引时创建分词器
**示例**
```json
{
  "analyzer": "custom_pattern",
  "text": "中文|汉字|测试"
}
```

```json
{
  "tokens": [
    {
      "token": "中文",
      "start_offset": 0,
      "end_offset": 2,
      "type": "word",
      "position": 0
    },
    {
      "token": "汉字",
      "start_offset": 3,
      "end_offset": 5,
      "type": "word",
      "position": 1
    },
    {
      "token": "测试",
      "start_offset": 6,
      "end_offset": 8,
      "type": "word",
      "position": 2
    }
  ]
}
```
