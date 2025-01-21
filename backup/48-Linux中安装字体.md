
# Linux 中安装字体

## 查看系统中的字体

```sh
fc-list
```

## 查看系统中的中文字体

```sh
fc-list :lang=zh
```

将字体文件拷贝到/usr/share/fonts/中

```bash
cp simsun.ttc /usr/share/fonts
cd /usr/lshare/fonts
mkfontscale
mkfontdir
```

## 检验：

```bash
fc-list :lang=zh
```

就可以看到刚安装的字体了

## Ubuntu

```bash
apt-get install fontconfig
apt-get install xfonts-utils
```

## CentOS

```bash
yum -y install fontconfig #安装字体库
yum -y install ttmkfdir mkfontscale #安装字体索引信息
```
