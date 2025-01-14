```sh
tcpdump tcp port 22 and host 1.1.1.1 -w ./output.cap
```

1) tcp 过滤数据包的类型 
2) port 目标端口 
3) host 目标主机 
4) -w ./output.cap 输出cap文件, 可用[wireshark](https://www.wireshark.org/download.html)打开分析 