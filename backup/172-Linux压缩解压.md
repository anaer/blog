## atool 智能压缩解压工具

atool 会根据文件类型自动选择正确的解压方式。

安装（CentOS/RedHat）：
```sh
yum install atool -y
```

解压任意压缩包：
```sh
aunpack yourfile.xxx
```

压缩：
```sh
apack out.zip file1 file2 dir/
```

识别所有常见格式，实现几乎“全自动”。


## zip格式
```sh
$ zip -r [目标文件名].zip [原文件/目录名]
$ unzip [原文件名].zip
```

## tar格式
```sh
$ tar -cvf [目标文件名].tar [原文件名/目录名]
$ tar -xvf [原文件名].tar
```

## tar.gz格式
```sh
$ gzip [原文件名].tar
$ gunzip [原文件名].tar.gz

$ tar -zcvf [目标文件名].tar.gz [原文件名/目录名]
$ tar -zxvf [原文件名].tar.gz
```

## tar.bz2格式

```sh
$ bzip2 [原文件名].tar
$ bunzip2 [原文件名].tar.bz2

$ tar -jcvf [目标文件名].tar.bz2 [原文件名/目录名]
$ tar -jxvf [原文件名].tar.bz2
```

## tar.xz格式

```sh
$ xz [原文件名].tar
$ unxz [原文件名].tar.xz

$ tar -Jcvf [目标文件名].tar.xz [原文件名/目录名]
$ tar -Jxvf [原文件名].tar.xz
```

## 7z格式

```sh
$ 7z a [目标文件名].7z [原文件名/目录名]
$ 7z x [原文件名].7z
```

## jar格式

```sh
$ jar -cvf [目标文件名].jar [原文件名/目录名]
$ jar -xvf [原文件名].jar
注：如果是打包的是Java类库，并且该类库中存在主类，那么需要写一个META-INF/MANIFEST.MF配置文件，内容如下：

```mf
Manifest-Version: 1.0
Created-By: 1.8.0_27 (Sun Microsystems Inc.)
Main-class: Main.class
```
然后用如下命令打包：

```sh
jar -cvfm [目标文件名].jar META-INF/MANIFEST.MF [原文件名/目录名] 这样以后就能用“java -jar [文件名].jar”命令直接运行主类中的main方法了。
```
