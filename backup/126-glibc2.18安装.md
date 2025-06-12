# 前因
doris manager 安装studio时 报错提示
```
/lib64/libc.so.6: version `GLIBC_2.18' not found (required by /lib64/libstdc++.so.6)
```

# 安装编译依赖
```sh
sudo yum install -y bison gcc make
```

# 下载源码
```sh
wget https://ftp.gnu.org/gnu/glibc/glibc-2.18.tar.gz
tar -zxvf glibc-2.18.tar.gz
cd glibc-2.18
```

# 创建编译目录
```sh
mkdir build && cd build
../configure --prefix=/usr --disable-profile --enable-add-ons
```

# 编译安装
```sh
make -j$(nproc)
sudo make install
```

# 验证
```
strings /lib64/libc.so.6 | grep GLIBC_2.18
```