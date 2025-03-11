```sh
λ smartdns --help                                                                                                       
A cross platform local DNS server written in rust to obtain the fastest website IP for the best Internet experience, sup
port DoT, DoQ, DoH, DoH3.                                                                                                                                                                                                  
Usage: smartdns [OPTIONS] <COMMAND>                                                                                     
                                                                                                                        
Commands:                                                                                                               
  run      Run the Smart-DNS server                                                                                     
  update   Download and install new version                                                                             
  service  Manage the Smart-DNS service (install, uninstall, start, stop, restart)                                      
  resolve  Perform DNS resolution                                                                                       
  symlink  Create a symbolic link to the Smart-DNS binary (drop-in replacement for `dig`, `nslookup`, `resolve` etc.)   
  test     Test configuration and exit                                                                                  
  help     Print this message or the help of the given subcommand(s)                                                    
                                                                                                                        
Options:                                                                                                                
  -v, --verbose...  Increase logging verbosity                                                                          
  -q, --quiet...    Decrease logging verbosity                                                                          
  -h, --help        Print help                                                                                          
  -V, --version     Print version                                                                                       
```

```sh
λ smartdns service --help
Manage the Smart-DNS service (install, uninstall, start, stop, restart)

Usage: smartdns service [OPTIONS] <COMMAND>

Commands:
  install    Install the Smart-DNS as service
  uninstall  Uninstall the Smart-DNS service
  start      Start the Smart-DNS service
  stop       Stop the Smart-DNS service
  restart    Restart the Smart-DNS service
  status     Print the service status of Smart-DNS
  help       Print this message or the help of the given subcommand(s)

Options:
  -v, --verbose...  Increase logging verbosity
  -q, --quiet...    Decrease logging verbosity
  -h, --help        Print help
```

## 配置示例

```conf
#region 配置说明
  # https://github.com/pymumu/smartdns/blob/doc/docs/configuration.md
#endregion

# 在本地 53 端口监听
bind 127.0.0.1:53

#### 上游DNS服务 ####
#指定上游服务器解析DOH，搭配下面的nameserver避免各方打架，不参与默认解析
server 8.8.8.8 -group google -exclude-default-group
server 8.8.4.4 -group google -exclude-default-group
server 1.1.1.1 -group cloudflare -exclude-default-group
server 1.0.0.1 -group cloudflare -exclude-default-group
server 9.9.9.9 -group quad9 -exclude-default-group
server 208.67.222.222 -group opendns -exclude-default-group
server 223.6.6.6 -group alidns -exclude-default-group
server 223.5.5.5 -group alidns -exclude-default-group
server 119.29.29.29 -group dnspod -exclude-default-group
server 119.28.28.28 -group dnspod -exclude-default-group
server 101.101.101.101 -group twnic -exclude-default-group

#CN组服务器，用于解析中国域名列表，不参与默认解析，防止泄露
server-https https://dns.alidns.com/dns-query -group cn -exclude-default-group
server-https https://doh.pub/dns-query -group cn -exclude-default-group
server 114.114.114.114 -group cn -exclude-default-group
server 1.2.4.8 -group cn -exclude-default-group

#默认组
server-https https://dns.google/dns-query
server-https https://dns.quad9.net/dns-query
server-https https://doh.opendns.com/dns-query
server-https https://cloudflare-dns.com/dns-query
server-https https://dns.twnic.tw/dns-query

#指定上游解析DOH服务器
nameserver /alidns.com/alidns
nameserver /doh.pub/dnspod
nameserver /dns.google/google
nameserver /quad9.net/quad9
nameserver /opendns.com/opendns
nameserver /cloudflare-dns.com/cloudflare
nameserver /twnic.tw/twnic

#### 日志 ####
# 设置日志级别 off、fatal、error、warn、notice、info 或 debug
log-level debug

# 日志文件路径
log-file C:/Users/Administrator/smartdns/smartdns.log

# 日志大小
log-size 1M

# 日志归档个数
log-num 3

# 设置审计启用
audit-enable yes

# 审计日志文件路径
audit-file C:/Users/Administrator/smartdns/smartdns-audit.log

# 审计日志大小
audit-size 1M

# 审计日志归档个数
audit-num 3

#### 缓存 ####
# 域名结果缓存个数，1 条缓存占内存 512 字节。
# 0 关闭缓存，不配置为系统自动设置
#（系统内存 128 M，自动缓存 32768 条占内存 16 M；
#  系统内存 256 M，自动缓存 65536 条占内存 32 M；
#  系统内存 512 M，自动缓存 131072 条占内存 64 M；
#  系统内存大于 512 M，自动缓存 262144 条占内存 128 M）。
#cache-size 65536
# 是否持久化缓存。自动，当 cache-file 所在的位置有超过 128 MB 的可用空间时启用，否则禁用
cache-persist yes
# 缓存持久化文件路径
cache-file C:/Users/Administrator/smartdns/cache.dump

#缓存预获取（域名TTL即将超时时，再次发送查询请求）
prefetch-domain yes
#过期缓存（即乐观缓存）
serve-expired no
#关于预获取和过期缓存，有四种情况，需要分别讨论。
#情况1：开启预获取，开启过期缓存：缓存过期一定时间后，再次发送查询请求，缓存新结果。（与情况3相比，缓解开启预获取导致的CPU压力）
#情况2：关闭预获取，开启过期缓存：客户端查询时，即使该域名缓存已过期（TTL为0），仍然返回已缓存IP，同时向上查询并缓存最新结果。若5s（默认值，可改）后客户端再此查询，则返回新结果。（与开启乐观缓存的AGH效果相同）
#情况3：开启预获取，关闭过期缓存：域名缓存即将过期（TTL即将为0）时，再次发送查询请求，缓存新结果。（本配置使用的情况，效果最好，但请求频率较高）
#情况4：关闭预获取，关闭过期缓存：客户端查询时，若该域名缓存已过期（TTL为0），则向上查询，返回结果并缓存。

#### IPV6 #####
# 双栈 IP 优选。关闭
dualstack-ip-selection no
# 强制 AAAA 地址返回 SOA。禁用ipv6
force-AAAA-SOA yes

#### 测速 ####
# 测速模式
speed-check-mode ping,tcp:80,tcp:443
# 首次查询响应模式。模式：
#[first-ping]: 最快ping响应地址模式，DNS上游最快查询时延+ping时延最短，查询等待与链接体验最佳;
#[fastest-ip]: 最快IP地址模式，查询到的所有IP地址中ping最短的IP。需等待IP测速;
#[fastest-response]: 最快响应的DNS结果，DNS查询等待时间最短，返回的IP地址可能不是最快。
response-mode first-ping

#### 其它 ####
# 强制指定 qtype 返回 SOA。禁用 SOA 65
force-qtype-SOA 65
# TCP 链接空闲超时时间
tcp-idle-time 120
```


## 相关链接

1. [配置参数说明](https://github.com/pymumu/smartdns/blob/doc/docs/configuration.md)
