
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

## 应用场景

### 1. 网络配置与路由
这是CIDR最根本的用途，用来定义网络边界和路由规则。
*   **设备配置**：在路由器、交换机、服务器网卡上配置IP时，必须用CIDR表示子网。例如 `192.168.1.10/24`，`/24` 就定义了该IP所在的子网范围。
*   **路由表**：路由器通过CIDR来聚合路由条目。例如，把多个连续的子网合并成一条 `10.0.0.0/8` 的路由，大幅减少路由表规模。

### 2. 云服务与网络安全
在云平台和安全策略中，CIDR是定义“允许/拒绝哪些IP”的标准方式。
*   **安全组/防火墙**：配置规则时，源/目标地址几乎都用CIDR。例如，允许 `203.0.113.0/24` 访问，就代表允许这个网段内的所有IP。
*   **VPC/子网划分**：在AWS、阿里云等平台创建私有网络时，必须用CIDR来指定VPC和子网的地址范围，例如 `10.0.0.0/16`。
*   **访问控制列表（ACL）**：在Nginx、Redis等服务的配置中，用CIDR来限制可访问的客户端IP段。

### 3. 容器与Kubernetes网络
在容器编排系统中，CIDR是网络模型的核心。
*   **Pod/Service网段**：Kubernetes集群在初始化时，需要指定Pod和Service的CIDR范围，例如 `10.244.0.0/16`。
*   **网络策略**：K8s的NetworkPolicy用CIDR来定义允许进出Pod的IP范围。

### 4. 网络规划与地址管理
在规划一个网络时，CIDR是计算和分配地址的工具。
*   **子网划分**：将一个大的CIDR块（如 `192.168.0.0/16`）切分成多个小的子网（如 `192.168.1.0/24`、`192.168.2.0/24`），分配给不同部门或区域。
*   **IP地址管理（IPAM）**：在大型网络中，用CIDR来跟踪和管理已分配和未分配的地址段。

### 5. 日志分析与监控
在排查问题时，CIDR用于快速过滤和聚合日志。
*   **日志查询**：在ELK、Splunk等系统中，用CIDR快速筛选出来自某个网段的访问记录。
*   **流量分析**：在监控工具中，按CIDR聚合流量，观察某个网段的整体趋势。

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

```log
λ python a.py 
请输入CIDR格式（例如 192.168.1.0/24 或 2001:db8::/32）: 192.168.1.0/24                                  
                                                                                                        
CIDR解析结果：                                                                                          
网络地址: 192.168.1.0                                                                                   
广播地址: 192.168.1.255                                                                                 
子网掩码: 255.255.255.0                                                                                 
IP总数: 256                                                                                             
IP范围: 192.168.1.0-192.168.1.255       
```

## 相关链接

[CIDR 维基](https://zh.wikipedia.org/wiki/%E6%97%A0%E7%B1%BB%E5%88%AB%E5%9F%9F%E9%97%B4%E8%B7%AF%E7%94%B1)
