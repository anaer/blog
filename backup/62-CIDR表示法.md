
## CIDR 表示法

CIDR（Classless Inter-Domain Routing，无类域间路由）是一种简化的 IP 地址分配和路由选择协议，它使用了一种叫做 CIDR 表示法的方法来表示 IP 地址范围。

CIDR 表示法使用 IP 地址和前缀长度的组合来表示一个 IP 地址段，其中前缀长度指的是 IP 地址中网络部分的长度。

如，192.168.0.0/30 表示了一个包含 4 个 IP 地址的地址段，其中前 30 位是网络地址，后 2 位是主机地址。

| 配置           | ip 地址段                   |
| -------------- | --------------------------- |
| 192.168.0.0/30 | 192.168.0.0-192.168.0.3     |
| 192.168.0.0/24 | 192.168.0.0-192.168.0.255   |
| 192.168.0.0/16 | 192.168.0.0-192.168.255.255 |
| 192.168.0.0/8  | 192.168.0.0-253.255.255.255 |
| 172.16.0.0/12  | 172.16.0.0-172.31.255.255   |
| 10.0.0.0/8     | 10.0.0.0-10.255.255.255     |
| 188.180.0.0/22 | 188.180.0.0-188.180.3.255   |

## 转换脚本

```py
# python 3.12.7
import ipaddress

def cidr_to_ip_range(cidr):
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        return {
            "network": str(network.network_address),
            "broadcast": str(network.broadcast_address),
            "netmask": str(network.netmask),
            "cidr": network.prefixlen,
            "total_ips": network.num_addresses,
            "start_ip": str(network.network_address),
            "end_ip": str(network.broadcast_address)
        }
    except ValueError as e:
        return f"错误：{str(e)}"

if __name__ == "__main__":
    cidr_input = input("请输入CIDR格式（例如 192.168.1.0/24 或 2001:db8::/32）: ")
    result = cidr_to_ip_range(cidr_input)

    if isinstance(result, dict):
        print("\nCIDR解析结果：")
        print(f"网络地址: {result['network']}")
        print(f"广播地址: {result['broadcast']}")
        print(f"子网掩码: {result['netmask']}")
        print(f"IP总数: {result['total_ips']:,}")
        print(f"IP范围: {result['start_ip']}-{result['end_ip']}")
    else:
        print(result)

```

## 相关链接

[CIDR 维基](https://zh.wikipedia.org/wiki/%E6%97%A0%E7%B1%BB%E5%88%AB%E5%9F%9F%E9%97%B4%E8%B7%AF%E7%94%B1)
