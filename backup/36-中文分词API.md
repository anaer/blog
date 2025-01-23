
## 中文分词API

### http://api.pullword.com/

```sh
// param1 出词概率阈值(0-1之间的小数)，1表示只有100%有把握的词才出
// param2 模式 0: 正常模式 1: 调试模式(显示概率)
// json=1 返回json格式
http://api.pullword.com/get.php?source=" + URLEncoder.encode(searchTitle) + "&param1=0&param2=0&json=1
```

### 哈工大 php 中文分词 api 
```sh
curl -X POST http://39.96.43.154:8080/api -H 'Content-Type: application/json' -d '{"text":"待分词的文本，1024个字或256个词以内"}'
```

**相关链接**
[demo页](http://39.96.43.154:8080/demo.html)

[介绍文章](https://blog.csdn.net/Deng_Xian_Sheng/article/details/118575782)

### 在线分词

```sh
curl 'https://tl.beer/api/v1/fenci' -H 'content-type: application/x-www-form-urlencoded' --data-raw 'cont=%E4%B8%AD%E6%96%87%E8%AF%8D%E6%80%A7%E6%A0%87%E6%B3%A8%E5%AF%B9%E7%85%A7%E8%A1%A8&cixin=false&model=false'
```
