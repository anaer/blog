## jieba

```python
# pip install jieba
import jieba

# 精确模式，试图将句子最精确地切开，适合文本分析
text = "测试分词长字符串"
words = jieba.cut(text, cut_all=False)
print("/".join(words))

# 全模式，把句子中所有的可以成词的词语都扫描出来，速度非常快，但是不能解决歧义
words_all = jieba.cut(text, cut_all=True)
print("/".join(words_all))

# 搜索引擎模式，在精确模式的基础上，对长词再次切分，提高召回率，适合用于搜索引擎分词
words_search = jieba.cut_for_search(text)
print("/".join(words_search))
```

## pkuseg

```python
# pip install pkuseg
# 上述命令安装失败, 暂未测试以下脚本
import pkuseg

# 加载默认模型
seg = pkuseg.pkuseg()

# 对文本进行分词
text = "测试分词长字符串"
words = seg.cut(text)
print(words)
```

## thulac

```python
# pip install thulac
import thulac

# 初始化THULAC模型，默认模型位于当前目录的'model'子目录下
thu1 = thulac.thulac(seg_only=True)  # 只进行分词
thu2 = thulac.thulac()  # 分词和词性标注

# 对文本进行分词
text = "测试分词长字符串"
words = thu1.cut(text, text=True)
print(words)

# 对文本进行分词和词性标注
words_pos = thu2.cut(text, text=True)
print(words_pos)
```