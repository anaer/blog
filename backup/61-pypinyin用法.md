
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

| Style Name     | Style | PinYin         |
| -------------- | ----- | -------------- |
| NORMAL         | 0     | zhong guo      |
| TONE           | 1     | zhōng guó      |
| TONE2          | 2     | zho1ng guo2    |
| TONE3          | 8     | zhong1 guo2    |
| INITIALS       | 3     | zh g           |
| FIRST_LETTER   | 4     | z g            |
| FINALS         | 5     | ong uo         |
| FINALS_TONE    | 6     | ōng uó         |
| FINALS_TONE2   | 7     | o1ng uo2       |
| FINALS_TONE3   | 9     | ong1 uo2       |
| BOPOMOFO       | 10    | ㄓㄨㄥ ㄍㄨㄛˊ |
| BOPOMOFO_FIRST | 11    | ㄓ ㄍ          |
| CYRILLIC       | 12    | чжун1 го2      |
| CYRILLIC_FIRST | 13    | ч г            |
| WADEGILES      | 14    | chung kuo      |

## 样式

```sh
#: 普通风格，不带声调。如： 中国 -> ``zhong guo``
NORMAL  =  0
#: 标准声调风格，拼音声调在韵母第一个字母上（默认风格）。如： 中国 -> ``zhōng guó``
TONE  =  1
#: 声调风格2，即拼音声调在各个韵母之后，用数字 [1-4] 进行表示。如： 中国 -> ``zho1ng guo2``
TONE2  =  2
#: 声调风格3，即拼音声调在各个拼音之后，用数字 [1-4] 进行表示。如： 中国 -> ``zhong1 guo2``
TONE3  =  8
#: 声母风格，只返回各个拼音的声母部分。如： 中国 -> ``zh g``
INITIALS  =  3
#: 首字母风格，只返回拼音的首字母部分。如： 中国 -> ``z g``
FIRST_LETTER  =  4
#: 韵母风格，只返回各个拼音的韵母部分，不带声调。如： 中国 -> ``ong uo``
FINALS  =  5
#: 标准韵母风格，带声调，声调在韵母第一个字母上。如：中国 -> ``ōng uó``
FINALS_TONE  =  6
#: 韵母风格2，带声调，声调在各个韵母之后，用数字 [1-4] 进行表示。如： 中国 -> ``o1ng uo2``
FINALS_TONE2  =  7
#: 韵母风格3，带声调，声调在各个拼音之后，用数字 [1-4] 进行表示。如： 中国 -> ``ong1 uo2``
FINALS_TONE3  =  9
#: 注音风格，带声调，阴平（第一声）不标。如： 中国 -> ``ㄓㄨㄥ ㄍㄨㄛˊ``
BOPOMOFO  =  10
#: 注音风格，仅首字母。如： 中国 -> ``ㄓ ㄍ``
BOPOMOFO_FIRST  =  11
#: 汉语拼音与俄语字母对照风格，声调在各个拼音之后，用数字 [1-4] 进行表示。如： 中国 -> ``чжун1 го2``
CYRILLIC  =  12
#: 汉语拼音与俄语字母对照风格，仅首字母。如： 中国 -> ``ч г``
CYRILLIC_FIRST  =  13
#: 威妥玛拼音/韦氏拼音/威式拼音风格，无声调 如： 中国 -> ``chung kuo``
WADEGILES = 14
```
