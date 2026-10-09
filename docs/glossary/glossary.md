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
| **内容区图标按钮** | 文章页三族图标按钮（正文标题折叠 `.section-toggle`、目录 `+−` `.toc-toggle`、代码块控件）共用的交互与配色语言：常态 `opacity:.6` + 主题 muted 色，hover 转不透明（目录与代码块控件另加主题背景，标题折叠为具名豁免）；图标尺寸按上下文保留 12/14/16（见 ADR-0019） |
| **标签色相（--label-hue）** | 标签与日期标签的配色基准：底色与字色在 CSS 里按主题推导（浅色浅底深字、深色深底浅字）。色相来源由配置项 `labelColorMode` 决定——`derived`（默认）按标签名经 `md5` 派生，`github` 取 GitHub 标签色的色相；两种模式共用同一套渲染（见 ADR-0020） |
| **列表序（list_order）** | 全站文章的唯一排列：置顶优先 → 更新时间降序 → 编号兜底（已关闭沉底）。列表页、关联数据 `nav.json`、全量构建预排三处共用；`nav.json` 的序即文章页「相关文章」同分条目之间的次级序（见 ADR-0022） |
| **关联文章（.related-posts）** | 文章页底部区块：关联度 = 与当前文章共享的标签数，由 `assets/nav.js` 运行时按 `nav.json` 算出并渲染，最多 5 条；无命中、无标签或数据拉取失败时整块移除（见 ADR-0022） |
| **Pagefind UI 预拉（idle prefetch）** | 首页 `requestIdleCallback` 内插入 `<link rel="prefetch" as="script" href="<homeUrl>/pagefind/pagefind-ui.js">`，让"首页→检索页"路径省下 `pagefind-ui.js` 的冷下载；不影响首页渲染（见 ADR-0026） |
| **Pagefind 装饰器（decorate）** | 检索页在 `PagefindUI` 渲染结果后挂标签 chip + issue 图标的脚本；通过 `MutationObserver` 触发，幂等标记 `data-gmDecorated` 防重挂载（见 ADR-0021）；`requestAnimationFrame` 节流见 ADR-0026 |
