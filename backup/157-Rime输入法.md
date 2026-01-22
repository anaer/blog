
### 重新部署

```sh
WeaselDeployer.exe /deploy
```

### 问题
跟WPS Office 10.8.2.6613兼容有问题 输入卡顿

## 万象输入法

| 特性           | 使用           |
| -------------- | -------------- |
| 数字、金额大写 | R数字          |
| 计算器         | V数字          |
| 辅助码提示     | Ctrl+a         |
| 音调显示       | Ctrl+s         |
| 翻译模式       | Ctrl+e         |
| 时间           | osj 或者 /sj   |
| 日期           | orq 或者 /rq   |
| 农历           | onl 或者 /nl   |
| 星期           | oxq 或者 /xq   |
| 今年第几周     | oww 或者 /ww   |
| 节气           | ojq 或者 /jq   |
| 日期+时间      | ors 或者 /rs   |
| 时间戳         | ott 或者 /tt   |
| 大写N日期      | N20250315      |
| 节日           | ojr 或者 /jr   |
| 问候模板       | /day 或者 oday |


## 添加万象模型
[下载模型wanxiang-lts-zh-hans.gram](https://github.com/amzxyz/RIME-LMDG/releases/download/LTS/wanxiang-lts-zh-hans.gram)

universe_pinyin.custom.yaml 添加配置

```yaml
patch:
    grammar:
        language: wanxiang-lts-zh-hans
        collocation_max_length: 5
        collocation_min_length: 2
    translator/contextual_suggestions: true
    translator/max_homophones: 7
    translator/max_homographs: 7
```

验证尝试输出 `苍茫的天涯是我的爱`

## 相关链接

[RIME仓库](https://github.com/rime)
[oh-my-rime](https://github.com/Mintimate/oh-my-rime)
[万象拼音](https://github.com/amzxyz/rime_wanxiang)