# CHANGELOG

## 26.1008.1605

1. 加 state 迁移步骤 `migrate_state`: 构建入口(默认 defaultConfig)就地补全老 blogBase.json 里的派生字段 dateLabelHue / createdDate, 由 baseline 字段确定性重算, 一次构建后落盘, 后续消费者(plist/tag_data/...)统一走真值路径
2. plist.html 第 82 行日期标签加深度防御 `.get('dateLabelHue', 210) / .get('createdDate', '')`: 即使迁移步骤被绕过, 也不再有 Jinja Undefined 渲染成空 style / 空 innerHTML
3. 新增 `TestMigrateState` 5 条回归测试, 钉死就地补全 / 幂等(已有值不被覆盖) / 不触碰其它字段 / 缺失列表键或 None 健壮性 / 与 addOnePostJson 派生值一致

## 26.1008.1540

1. tag_data 字段缺失兜底: 旧状态文件(blogBase.json)的帖子在本特性加入前已存, 缺少 dateLabelHue 等; 之前 KeyError 让整页构建崩溃; 改为每个字段按 defaults 兜底(色相 210 / 串空 / 列表空), 老数据与新数据可混存, 单条缺失不中断整页
2. 同步回归测试 `TestTagData::test_missing_fields_fall_back_to_defaults` 等三条, 钉死兜底值与键集合

## 26.1008.1520

1. post.html 调整删除线样式: `.markdown-body del` 字色与划线色都改走主题变量 `--color-fg-muted` / `--color-fg-subtle`, 旧文本自然退到背景层, 不再与当前文本抢视觉权重(明暗自适应)
2. 同步回归测试 `test_post_del_uses_muted_tokens_for_text_and_line` 与 `test_post_theme_tokens_cover_del_dependencies`, 钉死主题 token 完备与不引入硬编码颜色

## 26.1008.1511

1. 修复 CI 启动崩溃: `GMEEK.__init__` 之前在 `defaultConfig()` 之后才赋值 `self.labelHueDict`, 但 `defaultConfig` 已先读取, 故真实实例化会 AttributeError; 改为先以空 dict 占位, defaultConfig 之后按 GitHub 标签重算覆盖(见 ADR-0020 修订)
2. 修复模板拿到空色相字典: 上一步加了占位后, `defaultConfig` 把空 dict 写进了 `blogBase["labelHueDict"]`, __init__ 末尾重算结束必须再回写到 blogBase, 否则 plist/post/tag 模板消费到的仍是占位空 dict, 标签全回退默认色相 210(见 ADR-0020 修订)
3. 新增回归测试: `TestLabelHueTheme::test_init_initialises_labelHueDict_before_defaultConfig`(行序)与 `test_init_resyncs_blogBase_labelHueDict_after_recompute`(回写), 钉死两层 invariant

## 26.1008.1450

1. 检索结果的标签与 issue 入口由「页脚」改为「标题行内」: 补挂到 `.pagefind-ui__result-title` 子节点末尾, 与标题链接同排, 标题行用 flex 布局, 空间不足时整体换行(见 ADR-0021 修订)

## 26.1008.1441

1. 检索结果改版: 展示文章标签并增加 issue 链接图标
2. 修复目录同级不对齐: +/− 槽位改为对所有目录项无条件预留
3. 修复文章页上一篇/下一篇与列表顺序不一致的问题: 三处排序(列表页/导航/全量预排)合并为同一序列
4. 标签配色增加配置开关: 可在「按标签名派生色相」与「取 GitHub 标签色的色相」之间切换
5. 标签配色改为按标签名派生色相, 不再依赖 GitHub 的标签色, 底色与字色随明暗主题自适应
6. 修复正文标题折叠按钮样式从未生效的问题: 选择器与按钮实际插入位置不匹配, 按钮一直按浏览器原生样式渲染
7. 统一正文标题折叠 / 目录 +− / 代码块控件三族图标按钮的交互与配色, 配色改走主题变量
8. 统一列表页 / 标签页 / 文章页的搜索框样式: 抽为共享组件, 窄屏保留并收窄
9. 同步文档: 更新 ADR 正文、CONFIG.md 与 README 中已与实现不符的描述
10. 深色模式兼容: 修复正文与元信息等内容在深色下不可见的问题
11. 修复主题切换按钮无法切到深色的问题
12. 修复 search.html 搜索框样式: 尺寸改用 Pagefind 的 --pagefind-ui-scale 统一缩放(原单独覆盖 height 导致放大镜图标偏下、清除按钮溢出输入框); 新增几何居中回归测试(见 ADR-0007 修订)
13. 修复代码块行距翻倍(.cl 之间裸换行)与自动换行失效(.cl 继承 pre>code 的 white-space:pre); 硬换行只作用于围栏外, 代码不再被塞尾随空格; 补充移动端/触屏样式(控件常显、加大点按、顶部留白不遮代码)(见 ADR-0015, RENDER_VERSION 6)
14. 图标风格统一为 24x24 线性描边(简洁现代, Lucide 风): icons.py 的 ICONS 改为内部标记并统一 viewBox/stroke-width, 宏 macro.html、前端 renderIcon()、代码块控件同步; 新增 svg.octicon 覆盖 primer 的填充规则; 主题切换图标改由 innerHTML 回填(见 ADR-0014 修订, RENDER_VERSION 5)
15. 图标统一: 新增 icons.py 单一数据源, 模板经 macro.html 统一渲染, 代码块控件与前端 JS(toc/sections)复用同一套图标(见 ADR-0014)
16. 修复 runAll 分页迭代与命令行路由缺陷(手动触发误入 runOne(0)), 并增加 CI 发布安全闸门, 避免清空线上帖子(见 ADR-0013)

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
