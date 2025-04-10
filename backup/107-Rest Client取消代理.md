因为VSCode配置了代理, 而用rest-client时 基本上不要代理, 又没有关代理的配置
虽然rest-client提供了excludeHostsForProxy配置, 但是经常性要加新域名, 已配置近30个了

可以修改以下文件:
c:\Users\Administrator\.vscode\extensions\humao.rest-client-0.25.1\dist\extension.js

修改获取代理配置, 改名, 让找不到代理配置即可
workspace.getConfiguration("http") -> workspace.getConfiguration("http1")

不过环境变量如果配置了http.proxy, 应该还能用, 未测试.