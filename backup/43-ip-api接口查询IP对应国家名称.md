## 代码

```python
import json
import requests


def getCountryNameByHttp(ip):
    '''
    查询ip对应国家代码
    如果未查询到, 或者查询异常, 返回空
    '''
    country = ''
    try:
        rq = requests.get("http://ip-api.com/json/{}?lang=zh-CN".format(ip))
        ip_info = json.loads(rq.content)
        if (ip_info['status'] == 'success'):
            country = ip_info['country']
        return country
    except Exception as e:
        print("getCountryCode异常.", ip, e)
        return country


print(getCountryNameByHttp("8.8.8.8"))
# 美国
```