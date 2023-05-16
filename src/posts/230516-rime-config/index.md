---
title: Rime配置
date: "2023-05-16T11:11:03.000Z"
description: Rime配置
tags:
  - rime
last_updated: "2023-05-16T11:11:03.000Z"
---

```toc
# This code block gets replaced with the TOC
```

## 添加emoji表情支持

1. 下载opencc目录

### default.custom.yaml

```yml
patch:
  switcher/save_options:
    - full_shape
    - ascii_punct
    - simplification
    - zh_hans
    - emoji_suggestion
```

### terra_pinyin.custom.yaml

```yml
patch:
  switches:
    - name: ascii_mode
      reset: 0
      states: [ 中文, 西文 ]
    - name: emoji_suggestion
      reset: 1
      states: [ "Yes", "No" ]
    - name: full_shape
      states: [ 半角, 全角 ]
    - name: simplification
      reset: 1
      states: [ 漢字, 汉字 ]
    - name: ascii_punct
      states: [ 。，, ．， ]

  engine/filters:
    - simplifier@emoji_suggestion
    - simplifier
    - uniquifier

  emoji_suggestion:
    opencc_config: emoji.json
    option_name: emoji_suggestion
```

## 添加中文维基词库

### 步骤
1. 从最新的[Release](https://github.com/ipcjs/fcitx5-pinyin-zhwiki/releases)中下载zhwiki.dict.yaml文件，放到用户文件夹下
2. 创建terra_pinyin.custom.yaml文件，添加如下内容：

```yml
# encoding: utf-8
patch:
  translator/dictionary: terra_pinyin.extended # 指定字典
```

3. 创建terra_pinyin.extended.dict.yaml文件，添加如下内容：

```yml
# encoding: utf-8
name: terra_pinyin.extended
version: "2023.05.16"
sort: by_weight
use_preset_vocabulary: true
import_tables:
  - terra_pinyin
  - zhwiki
```

## 添加中英文混合输入

1. 添加以下文件
```
easy_en.yaml
easy_en.schema.yaml
easy_en.dict.yaml
lua/easy_en.lua
```

2. 在全球拼音输入法的terra_pinyin.custom.yaml配置中添加
__include值 与easy_en.yaml中一致

```yaml
patch:
  __include: easy_en:/patch_terra_pinyin
```

[参考提交记录](https://github.com/anaer/rime/commit/654c077c721a4e23b7a8709beac82b986eec9398)