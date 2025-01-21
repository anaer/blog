
## QR Server 二维码接口

size 尺寸大小
margin 边框大小, 范围 0-50

```
https://api.qrserver.com/v1/create-qr-code/?size=100×100&data=https://www.xxx.com
```

## 搜藏共享二维码接口

```
https://wenhairu.com/static/api/qr/?size=100&text=https://www.xxx.com
```

需用 urlencode 编码

## ISOYU 二维码接口

p 二维码像素尺寸 可选范围 1-40
m 边框像素尺寸
e 级别

```
https://api.isoyu.com/qr/?m=0&e=L&p=10&url=https://www.xxx.com
```
