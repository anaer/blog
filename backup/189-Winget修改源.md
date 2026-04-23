

## 修改源
remove可能需要多执行一次, 偶尔remove完 直接add 会提示winget已存在

```sh
winget source remove winget
winget source add winget https://mirrors.cernet.edu.cn/winget-source --trust-level trusted
```

## 重置源
重置为官方源

```sh
winget source reset winget
```