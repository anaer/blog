# CHANGELOG

## 25.117.956

1. 调整摘要生成逻辑 markdown->html->plaintext

## 25.108.1048

1. html链接使用issue.number, 简单点, 同时可以避免修改标题导致的链接变更问题以及计数问题
2. post标题采用issue.number+issue.title
3. 调整vercount实现方式, 加载时先使用localstorage中缓存的site数据, page数据使用接口返回

## 25.102.1647

1. 调整列表排序以及日期标签颜色
2. 列表页添加issues链接
