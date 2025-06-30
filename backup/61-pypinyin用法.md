
## 安装

```sh
pip install pypinyin
```

## 使用

```py
from pypinyin import lazy_pinyin,Style
word = "中国"
for s in Style:
    pinyin = lazy_pinyin(word,style=s)
    print(f"{s.name:<15} = {s:<2} {" ".join(pinyin)}")
```

| Style Name     | Style | PinYin         | Remark|
| -------------- | ----- | -------------- |----|
| NORMAL         | 0     | zhong guo      |普通风格，不带声调。
| TONE           | 1     | zhōng guó      |标准声调风格，拼音声调在韵母第一个字母上（默认风格）。
| TONE2          | 2     | zho1ng guo2    |声调风格2，即拼音声调在各个韵母之后，用数字 [1-4] 进行表示。
| TONE3          | 8     | zhong1 guo2    |声调风格3，即拼音声调在各个拼音之后，用数字 [1-4] 进行表示。
| INITIALS       | 3     | zh g           |声母风格，只返回各个拼音的声母部分。
| FIRST_LETTER   | 4     | z g            |首字母风格，只返回拼音的首字母部分。
| FINALS         | 5     | ong uo         |韵母风格，只返回各个拼音的韵母部分，不带声调。
| FINALS_TONE    | 6     | ōng uó         |标准韵母风格，带声调，声调在韵母第一个字母上。
| FINALS_TONE2   | 7     | o1ng uo2       |韵母风格2，带声调，声调在各个韵母之后，用数字 [1-4] 进行表示。
| FINALS_TONE3   | 9     | ong1 uo2       |韵母风格3，带声调，声调在各个拼音之后，用数字 [1-4] 进行表示。
| BOPOMOFO       | 10    | ㄓㄨㄥ ㄍㄨㄛˊ |注音风格，仅首字母。
| BOPOMOFO_FIRST | 11    | ㄓ ㄍ          |注音风格，仅首字母。
| CYRILLIC       | 12    | чжун1 го2      |汉语拼音与俄语字母对照风格，声调在各个拼音之后，用数字 [1-4] 进行表示。
| CYRILLIC_FIRST | 13    | ч г            |汉语拼音与俄语字母对照风格，仅首字母。
| WADEGILES      | 14    | chung kuo      |威妥玛拼音/韦氏拼音/威式拼音风格，无声调。

