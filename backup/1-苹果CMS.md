## [苹果CMS](https://github.com/magicblack/maccms10)

## 接口说明

[Provide.php](https://github.com/magicblack/maccms10/blob/master/application/api/controller/Provide.php)

### 列表
http://域名/api.php/provide/vod/?ac=list

入参：
```
ac=list 查询列表 videolist 查询列表(全字段) detail 查询详情
t=类别ID
pg=页码
wd=搜索关键字
h=几小时内的数据

isend=是否已完结 1: 已完结 0:未完结
year=查询年份 支持区间2022-2023
sort_direct=排序方向 目前按vod_time排序, 默认desc倒序, asc 正序
pagesize=单页数据量 最大限制100
```

例如： 
```
http://域名/api.php/provide/vod/?ac=list&t=1&pg=5 分类ID为1的列表数据第5页 
http://域名/api.php/provide/vod/?ac=detail&ids=123,567 获取ID为123和567的数据信息 
http://域名/api.php/provide/vod/?ac=detail&h=24 获取24小时内更新数据信息 
```

## 搜索资源
## 使用关键词
```
inurl:/api.php/provide/vod
```

[Google搜索](https://www.google.com/search?q=inurl%3A%2Fapi.php%2Fprovide%2Fvod&ie=UTF-8)

## 相关链接

[接口说明](https://github.com/magicblack/maccms10/wiki/%E5%85%A5%E5%BA%93%E6%8E%A5%E5%8F%A3%E8%AF%B4%E6%98%8E)

[字段说明](https://github.com/magicblack/maccms10/wiki/%E6%A0%87%E7%AD%BE%E6%96%87%E6%A1%A3)