## 注册表

可以使用Autoruns软件 可以方便的跳转注册表

regedit 打开注册表, 定位以下路径
`HKCU\Software\Microsoft\Windows\CurrentVersion\Run`

添加字符串值, 填名称和对应脚本路径

## 启动文件夹

按 Win + R 输入 shell:startup 回车

```
C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
```

添加需要自启动的快捷方式