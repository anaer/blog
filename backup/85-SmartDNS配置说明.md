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


## 相关链接

1. [配置参数说明](https://github.com/pymumu/smartdns/blob/doc/docs/configuration.md)
