
# 生成扩展包工程目录

## 安装 Yeoman 工具

默认源下载慢的话, 可以通过chsrc测速改源

```Bash
npm install -g yo generator-code
```

## 创建扩展包工程

```bash
yo code
```

# 扩展打包

## 安装 vsce 打包工具

```bash
npm install -g @vscode/vsce
```

## 生成扩展
新版vsce需要使用Node 18或者更高版本, 低版本执行存在语法兼容问题

```bash
$ cd myExtension
$ vsce package
# myExtension.vsix generated

$ vsce publish
# <publisherID>.myExtension published to VS Code Marketplace

$ vsce login anaer
# 输入PAT 进行更新
```

如果提示vsce命令未找到, 可以将vsce.cmd命令所在目录添加到环境变量PATH中: C:\Users\Administrator\AppData\Roaming\npm

## 获取PAT
token最大有效期1年

https://dev.azure.com/anaer/_usersSettings/tokens

