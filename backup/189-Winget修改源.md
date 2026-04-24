

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

## 自动更新备份 

winget_upgrade.bat 添加到自启动

```sh
@REM 应用更新并备份版本信息
chcp 65001
winget upgrade --all --include-unknown
winget export -o winget-pkg.config
```

## pin 添加包钉 阻止升级

对于不想升级, 或者升级报错的, 可以添加包钉

```sh
winget pin add --id Microsoft.VisualStudioCode.Insiders
winget pin add --id PremiumSoft.NavicatPremium
winget pin add --id Microsoft.AppInstaller
winget pin add --id Microsoft.WindowsTerminal

winget pin list
winget pin -?
```