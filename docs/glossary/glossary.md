# 术语表（glossary）

> 单一事实来源的「术语 → 是什么」索引：每行一句话讲清这个词指代什么；只收录跨 ADR 复用或易歧义的专属术语。

| 术语 | 定义 |
|------|------|
| **全量构建 / 增量构建** | 两种生成入口：全量重建整个站点（runAll），增量只重建单个 issue 相关页面与列表（runOne）（见 ADR-0001） |
| **blogBase.json** | 构建状态文件，持久化文章索引与摘要/构建时间缓存，供后续构建增量复用（见 ADR-0001） |
| **postListJson** | 普通文章索引集合，收录非单页 issue 的元数据与缓存字段（见 ADR-0001） |
| **singeListJson** | 单页索引集合，收录命中 singlePage 标签的页面条目（见 ADR-0001） |
| **buildedAt** | 文章条目的构建缓存标记，等于生成时该 issue 的更新时间；未变更的文章凭它跳过重复转换（见 ADR-0001） |
| **置顶状态（top）** | 文章排序状态位：1=置顶、0=普通、-1=已关闭（列表排最后）（见 ADR-0001） |
| **单页（singlePage）** | 以单一专属标签（如 link、about）标识的独立页面，生成到站点根路径而非文章列表（见 ADR-0002） |
| **检索索引** | 构建期由 Pagefind 扫描生成产物目录得到的静态检索数据，输出到 `pagefind/`，仅在检索页按需加载（见 ADR-0007） |
| **删除清理（prune）** | 构建时将持久化索引与仓库实况（issue 是否存在）对账，剔除已删除 issue 的索引条目与 HTML 的机制（runOne 捕获 404 或 `--prune` 全量对账）（见 ADR-0008） |
| **图标注册表（icons.py）** | 站点图标的单一数据源，统一为 24×24 线性描边（`fill=none stroke=currentColor stroke-width=1.5`，Lucide 风），供模板宏 `macro.html`、代码块控件与前端 `renderIcon()` 三方复用（见 ADR-0014） |
| **renderIcon()** | `base.html` 暴露的前端图标渲染函数，按 `IconList`/`IconViewBox`/`IconStrokeWidth` 生成统一线性描边 `<svg>`，供 toc.js、sections.js 等复用（见 ADR-0014） |
| **行 span（.cl）** | 代码块内每个逻辑行包裹的 `<span class="cl">`，行号由 CSS 计数器生成；因 `pre>code` 的 `white-space:pre` 会经继承压制换行，须在 `.cl` 上显式 `white-space:pre-wrap` 才能自动换行（见 ADR-0005 / ADR-0015） |
| **硬换行注入（_add_hard_breaks）** | 渲染前给围栏代码块之外的每行末尾追加两个空格，使 Markdown 单换行渲染为 `<br>`；代码块内跳过，避免污染代码内容（见 ADR-0015） |
| **站内搜索框（.site-search）** | 列表页 / 标签页 / 文章页共用的搜索框组件，样式只在 `base.html` 定义一次；圆角输入框 + 图标提交按钮，配色随主题，窄屏保留并收窄（见 ADR-0018） |
