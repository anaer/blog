# CHANGELOG

## 26.1008.1130

1. 同步文档: 更新 ADR 正文、CONFIG.md 与 README 中已与实现不符的描述

## 26.1008.1125

1. 深色模式兼容: 修复正文与元信息等内容在深色下不可见的问题

## 26.1008.1110

1. 修复主题切换按钮无法切到深色的问题

## 26.1008.1055

1. 修复 search.html 搜索框样式: 尺寸改用 Pagefind 的 --pagefind-ui-scale 统一缩放(原单独覆盖 height 导致放大镜图标偏下、清除按钮溢出输入框); 新增几何居中回归测试(见 ADR-0007 修订)

## 26.1008.1042

1. 修复代码块行距翻倍(.cl 之间裸换行)与自动换行失效(.cl 继承 pre>code 的 white-space:pre); 硬换行只作用于围栏外, 代码不再被塞尾随空格; 补充移动端/触屏样式(控件常显、加大点按、顶部留白不遮代码)(见 ADR-0015, RENDER_VERSION 6)

## 26.1008.1028

1. 图标风格统一为 24x24 线性描边(简洁现代, Lucide 风): icons.py 的 ICONS 改为内部标记并统一 viewBox/stroke-width, 宏 macro.html、前端 renderIcon()、代码块控件同步; 新增 svg.octicon 覆盖 primer 的填充规则; 主题切换图标改由 innerHTML 回填(见 ADR-0014 修订, RENDER_VERSION 5)

## 26.1008.0930

1. 图标统一: 新增 icons.py 单一数据源, 模板经 macro.html 统一渲染, 代码块控件与前端 JS(toc/sections)复用同一套图标(见 ADR-0014)
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
