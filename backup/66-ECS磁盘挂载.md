# 磁盘挂载

```bash
1. fdisk -l
2. fdisk /dev/xvdb
    n
    p
    1
    回车
    回车
    w
3. mkfs.ext3 /dev/xvdb1
4. mv /home /home1
5. mkdir /home
6. mount -t ext4 /dev/xvdb1 /home
7. mv /home1/* /home/
8. chmod 775 -R /home/*
9. vi /etc/fstab
    在最后加一行
    /dev/xvdb1 /home ext4 defaults 0 0
    :wq
10. init
11. 重启。
```
