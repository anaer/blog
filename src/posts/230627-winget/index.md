---
title: WinGet命令
date: "2023-06-27T14:12:09.000Z"
description: WinGet命令
tags:
  - winget
last_updated: "2023-07-03T09:33:02.000Z"
---

```toc
# This code block gets replaced with the TOC
```

```ps1
WinGet 命令行实用工具可从命令行安装应用程序和其他程序包。

使用情况: winget [<命令>] [<选项>]

下列命令有效:
install   安装给定的程序包
show      显示包的相关信息
source    管理程序包的来源
search    查找并显示程序包的基本信息
list      显示已安装的程序包
upgrade   升级给定的程序包
uninstall 卸载给定的程序包
hash      哈希安装程序的帮助程序
validate  验证清单文件
settings  打开设置
features  显示实验性功能的状态
export    导出已安装程序包的列表
import    安装文件中的所有程序包

如需特定命令的更多详细信息，请向其传递帮助参数。 [-?]

下列选项可用：

-v,--version 显示工具的版本
--info 显示工具的常规信息

可在此找到更多帮助： https://aka.ms/winget-command-help
```

## 查询可升级的程序包

```ps1
# 查询可用升级
> winget upgrade

名称                                            ID                           版本         可用         源
-------------------------------------------------------------------------------------------------------------
Microsoft Visual C++ 2013 Redistributable (x86) Microsoft.VC++2013Redist-x86 12.0.30501.0 12.0.40664.0 winget
1 升级可用。
```

```ps1
# 升级所有可用的程序包
> winget upgrade --all

# 升级所有可用的程序包 包含未知版本
> winget upgrade --all --include-unknown
```

## winget settings

winget settings 配置说明: https://docs.microsoft.com/zh-cn/windows/package-manager/winget/settings

```json
{
    "$schema": "https://aka.ms/winget-settings.schema.json",
    // For documentation on these settings, see: https://aka.ms/winget-settings
    "experimentalFeatures": {
        "experimentalMSStore": true,
        "restSource": true
    },
    "source": {
        // 自动更新频率
        "autoUpdateIntervalInMinutes": 5
    },
    "visual": {
        // 彩虹进度条
        "progressBar": "rainbow"
    }
}
```

## Winget 日志及程序安装日志

`C:\Users\Administrator\AppData\Local\Packages\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe\LocalState\DiagOutputDir`


## Winget替换软件源

```sh
# 替换为USTC源
winget source remove winget
winget source add winget https://mirrors.ustc.edu.cn/winget-source

# 重置为官方源
winget source reset winget
```

[WinGet源使用帮助](https://unicom.mirrors.ustc.edu.cn/help/winget-source.html)