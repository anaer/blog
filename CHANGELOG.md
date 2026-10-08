# CHANGELOG

## 26.1008.0930

1. 图标统一: 新增 icons.py 单一数据源, 模板经 macro.html 统一渲染, 代码块控件与前端 JS(toc/sections)复用同一套 16x16 填充式图标(见 ADR-0014)
2. 修复 runAll 分页迭代与命令行路由缺陷(手动触发误入 runOne(0)), 并增加 CI 发布安全闸门, 避免清空线上帖子(见 ADR-0013)

## 25.219.1731

1. 添加ai生成摘要

## 25.121.1035

1. post.html使用prevTitle判断, prevUrl可能存在等于disabled的情况
2. 保存markdown2html执行结果, 防止接口请求频繁导致请求失败
3. markdown2html添加重试, 请求异常时默认重试3次

## 25.117.956

1. 调整摘要生成逻辑 markdown->html->plaintext

## 25.108.1048

1. html链接使用issue.number, 简单点, 同时可以避免修改标题导致的链接变更问题以及计数问题
2. post标题采用issue.number+issue.title
3. 调整vercount实现方式, 加载时先使用localstorage中缓存的site数据, page数据使用接口返回

## 25.102.1647

1. 调整列表排序以及日期标签颜色
2. 列表页添加issues链接
