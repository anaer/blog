生成 Python 项目的 requirements.txt 文件

## 1. 使用 `pip freeze` 命令。
在项目的根目录下，打开终端或命令提示符，执行以下命令：

```sh
pip freeze > requirements.txt
```

这个命令会将当前环境中已安装的所有第三方库及其版本信息写入到 requirements.txt 文件中。

## 2. 使用 `pipreqs` 工具
`pipreqs` 是一个用于生成项目依赖的 requirements.txt 文件的工具。它可以分析项目中的 Python 代码，自动检测项目所使用的第三方库，并生成相应的 requirements.txt 文件。
在项目的根目录下，打开终端或命令提示符，执行以下命令：

```sh
pip install pipreqs
pipreqs . --encoding=utf8 --force
```

这个命令会在当前目录下生成 requirements.txt 文件，其中包含了当前项目所依赖的所有 Python 包及其版本号。


## 检测requirements.txt 文件中的版本更新

### pip自带命令
列出 requirements.txt 中已安装依赖包的更新版本
```
pip list --outdated
```

### pip-review

```
pip install pip-review

pip-review
```