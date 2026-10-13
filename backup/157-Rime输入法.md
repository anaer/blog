
## 重新部署

```sh
WeaselDeployer.exe /deploy
```

## 万象模型
下载模型[wanxiang-lts-zh-hans.gram](https://github.com/amzxyz/RIME-LMDG/releases/download/LTS/wanxiang-lts-zh-hans.gram)

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
[雾凇拼音](https://github.com/iDvel/rime-ice/)