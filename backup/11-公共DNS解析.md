## DNS Over HTTPS

DNS over HTTPS（缩写：DoH）是一个进行安全化的域名解析方案。其意义在于以加密的 HTTPS 协议进行 DNS 解析请求，避免原始 DNS 协议中用户的 DNS 解析请求被窃听或者修改的问题（例如中间人攻击）来达到保护用户隐私的目的

| 服务提供商     | DoH 地址                                         | DoT 地址           | IPS                      |
| -------------- | ------------------------------------------------ | ------------------ | ------------------------ |
| AdGuard        | https://dns.adguard-dns.com/dns-query            |
| AdGuard-无过滤 | https://unfiltered.adguard-dns.com/dns-query     |
| AdGuard-家庭   | https://family.adguard-dns.com/dns-query         |
| Blahdns        | https://doh-jp.blahdns.com/dns-query             |
| CleanBrowsing  | https://doh.cleanbrowsing.org/doh/family-filter/ |
| Cloudflare     | https://cloudflare-dns.com/dns-query             | cloudflare-dns.com | 1.1.1.1                  |
| DNS.SB         | https://doh.dns.sb/dns-query                     | dot.sb             |
| DNS.SB         | https://doh.sb/dns-query                         |
| Google         | https://dns.google.com/dns-query                 |
| Google         | https://dns.google/dns-query                     | dns.google         |
| OpenDNS        | https://doh.opendns.com/dns-query                |
| Quad9          | https://dns.quad9.net/dns-query                  | dns.quad9.net      |
| rixCloud       | https://doh.rixcloud.dev/dns-query               |
| 红鱼 DNS       | https://rubyfish.cn/dns-query                    |
| 阿里 DNS       | https://dns.alidns.com/dns-query                 | dns.alidns.com     |
| DNSWatch       | https://resolver2.dns.watch/dns-query            |
| 腾讯           | https://doh.pub/dns-query                        | dot.pub            | 1.12.12.12、120.53.53.53 |
| TWNIC Quad 101 | https://dns.twnic.tw/dns-query                   | dns.twnic.tw       |

## 公共 DNS

| 名称           | DNS                   |
| -------------- | --------------------- |
| 百度公共 DNS   | 180.76.76.76          |
| 114 DNS        | 114.114.114.114       |
| 阿里云公共 DNS | 223.5.5.5 / 223.6.6.6 |
| 谷歌公共 DNS   | 8.8.8.8 / 8.8.4.4     |

## 请求说明

```sh
https://dns.adguard.com/dns-query?dns=<base64url encoded data>
https://dns.adguard.com/resolve?name=<domain>&type=<DNS Q/A type>
```

### curl 请求方式

```sh
$ curl 'https://dns.adguard.com/resolve?name=www.baidu.com&type=A'
{
  "Question": [
    {
      "name": "www.baidu.com.",
      "type": 1
    }
  ],
  "Answer": [
    {
      "name": "www.baidu.com.",
      "data": "www.a.shifen.com.",
      "TTL": 12,
      "type": 5,
      "class": 1
    },
    {
      "name": "www.a.shifen.com.",
      "data": "14.119.104.189",
      "TTL": 12,
      "type": 1,
      "class": 1
    },
    {
      "name": "www.a.shifen.com.",
      "data": "14.119.104.254",
      "TTL": 12,
      "type": 1,
      "class": 1
    }
  ],
  "Extra": null,
  "TC": false,
  "RD": true,
  "RA": true,
  "AD": false,
  "CD": false,
  "Status": 0
}
```

## python 调用示例

```py
import dns.message
import requests
import base64
import json

doh_url = "https://dns.alidns.com/dns-query"
domain = "alibaba.com"
rr = "A"
result = []

message = dns.message.make_query(domain, rr)
dns_req = base64.b64encode(message.to_wire()).decode("UTF8").rstrip("=")
r = requests.get(doh_url + "?dns=" + dns_req,
                 headers={"Content-type": "application/dns-message"})
for answer in dns.message.from_wire(r.content).answer:
    dns = answer.to_text().split()
    result.append({"Query": dns[0], "TTL": dns[1], "RR": dns[3], "Answer": dns[4]})
    print(json.dumps(result))
```

```sh
$ python test_doh.py
[{"Answer": "106.11.223.101", "Query": "alibaba.com.", "RR": "A", "TTL": "133"}]
```

## DNS 污染

DNS 污染大致与以下内容为同义词：

DNS 缓存服务器污染：运营商的 DNS 服务器被污染，使用默认 DNS，网络就会被干扰。

DNS 抢答：DNS 请求没有防篡改功能，所以中间人能抢先发送错误的 DNS，网络就会被干扰。

DNS 劫持：使用自定义 DNS，同样是缺乏防篡改功能，所以中间人能劫持 DNS 请求，网络就会被干扰。

应对方法分别是：

DNS 缓存服务器污染：直接换 114.114.114.114 与 8.8.8.8 这样的非运营商的 DNS，只要没有抢答和劫持，就有效。

DNS 抢答：修改系统内核，使系统忽略错误的 DNS，因为早期 GFW 抢答给出的错误 IP 数量不多，然后真正的 DNS 返回的 IP，就能被正常使用。

DNS 劫持：使用 DNS over HTTPS（HTTP over TLS）、DNS over TLS 等方式，通过加密的协议来保护 DNS 请求。只要 GFW 没有将提供服务的域名，进行 SNI 封禁，就有效。

## DNS刷新
修改hosts文件后 刷新DNS缓存

Windows:

```sh
ipconfig /flushdns
```

Mac: 两种方式

```sh
sudo killall -HUP mDNSResponder

sudo dscacheutil -flushcache
```

## DNS泄漏检测

[DNS Leak Test](https://dnsleaktest.org/dns-leak-test)

[BrowserScan - DNS Leak](https://www.browserscan.net/dns-leak)

[DNS Leak Test - BrowserLeaks](https://browserleaks.com/dns)

[DNS泄漏测试](https://surfshark.com/zh/dns-leak-test)

[IP/DNS Detect](https://ipleak.net/)

## 相关链接

[DNS_over_HTTPS - 维基百科](https://zh.wikipedia.org/wiki/DNS_over_HTTPS)

[DNS over HTTPs(DoH)](https://www.alibabacloud.com/help/zh/alibaba-cloud-public-dns/latest/dns-over-https)

[AdGuard](https://adguard-dns.io/zh_cn/welcome.html)
