
## mklink 命令

```
>mklink /?
创建符号链接。

MKLINK [[/D] | [/H] | [/J]] Link Target

        /D      创建目录符号链接。默认为文件
                符号链接。
        /H      创建硬链接而非符号链接。
        /J      创建目录联接。
        Link    指定新的符号链接名称。
        Target  指定新链接引用的路径
                (相对或绝对)。
```

## 示例

### 指定 maven 仓库目录

```
mklink /D "C:\Users\Administrator\.m2\repository" "D:\repository"
```

### VSCode 工作目录, 目录较大 移动到非系统盘

```
mklink /D "C:\Users\Administrator\AppData\Roaming\Code\User\workspaceStorage" "D:\VSCode\workspaceStorage"
mklink /D "C:\Users\Administrator\AppData\Roaming\Code - Insiders\User\workspaceStorage" "D:\VSCode\workspaceStorage"
```
