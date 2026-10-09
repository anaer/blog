# ADR-0021：检索结果展示文章标签与 issue 入口

**状态：** 已接受
**创建时间：** 2026-10-08
**最近更新：** 2026-10-08（标签 chip 改为 `.Label` 类并跳转 `tag.html#`）

> **当前状态 / 核心结论：** 文章页输出两条 Pagefind meta（`labels` 为标签名 JSON 数组、`source` 为 issue 链接）；检索页在结果渲染后，把标签 chip 与 issue 图标作为标题行的一部分插入，与原标题同排。下一步无需后续动作。

---

## 背景

检索结果此前只显示标题与摘要：看不出文章归属哪些标签，也没有回到 issue 的入口——读者判断相关性只能靠摘要，想溯源或评论还得回列表页再找。

Pagefind 的组件 UI（`pagefind-ui.js`）**不提供结果模板**：与渲染相关的可配置项只有 `processResult`（渲染前修改结果对象）。结果 DOM 里虽有 `pagefind-ui__result-tags` 结构，但它由**过滤器**驱动——启用会额外带出筛选面板，超出「只展示标签」的范围。

## 决策

1. **文章页输出 meta**：`templates/post.html` 的 `head` 增加两条——
   - `data-pagefind-meta="labels[content]"`：标签名 **JSON 数组**（`|tojson`）
   - `data-pagefind-meta="source[content]"`：`postSourceUrl`（issue 链接）

   必须写成 `[content]` 形式：默认取元素 `textContent`，而 `<meta>` 的 textContent 为空，会**静默不入索引**；且**同名多个元素只保留最后一个**，故标签须合并成一个值，而非每个标签一个元素。
2. **检索页把元信息挂在标题行内**：`processResult` 按 URL 收集 meta，`MutationObserver` 在结果渲染后为每张卡片把 `.pagefind-ui__result-meta`（标签 chip + issue 图标）插入 `.pagefind-ui__result-title` 元素的子节点末尾，与标题链接同排；标题行已设 `display:flex; gap:8px; flex-wrap:wrap`，空间不足时整体换行，不再额外占第二行。
   - **挂载兜底**：若 `querySelector('.pagefind-ui__result-title')` 为空（Pagefind 类名未来变动），依次回退到 `.pagefind-ui__result-inner`、卡片本身。
   - **幂等标记**：补挂自身会再次触发观察器，故卡片加 `data-gm-decorated` 标记阻断循环。
   - **URL 双索引**：同时按完整 URL 与 pathname 建索引，规避 Pagefind 返回值与 DOM `href` 在编码 / 部署前缀上的细微差异。
3. **图标复用单一数据源**：issue 图标经 `templates/base.html#renderIcon('github')` 生成，与文章页 Issue 按钮同款，不新增图标定义。
4. **样式走主题变量**：标签 chip 配色用 `--fgColor-muted` / `--color-canvas-subtle`，issue 按钮走 `--fgColor-muted` 的 opacity 变化，明暗自适应。

   - 不做什么：不启用 Pagefind 过滤器（会额外带出筛选面板）；不引入 Pagefind 模块化 UI 重写结果模板；不把元信息放回独立的「页脚」位置（首屏可见性弱、占用垂直空间）。

5. **标签 chip 同时高亮 + 可点击跳到 tag.html**：结果里的每个标签渲染为 `<a class="Label" style="--label-hue:N" href="<homeUrl>/tag.html#<encoded>">name</a>`，而不是只读的 `<span>`。视觉上与 `post.html` / `plist.html` / `tag.html` 的标签**完全同源**——都走 `base.html` 的 `.Label` 类（`background-color: hsl(var(--label-hue) 50% 90%)` / 主题化字色 / 边框 / 圆角），按名派生色相，明暗自适应。点击后跳到 `tag.html` 的 hash 锚点；`tag.html` 的 `setClassDisplay(decodeURIComponent(location.hash.slice(1)))` 会自动滚到对应标签并高亮，闭环已通。
   - 色相注入：`templates/search.html` 把 `{{ blogBase['labelHueDict']|tojson }}` 注入到 JS 端为 `var labelHues`；构造 `<a>` 时 `setProperty('--label-hue', labelHues[name] ?? 210)`，缺失回退 210（与 `.Label` 默认一致）。
   - URL 编码：标签名经 `encodeURIComponent` 写入 href；`tag.html` 用 `decodeURIComponent` 读出。中英文、含特殊字符（`?`、`/`、`#`）的标签名都能正确还原。
   - 不做什么：不重新发明主题样式（直接复用 `.Label` 类，避免搜结果与文章/列表页颜色/尺寸错位）；不在 search.html 内维护一份重复的色相表（以 `blogBase` 为单一来源）。

## 后果

- **收益：** 结果卡片首行即可看见标签与 issue 入口，水平密集地展示相关性线索；零新增依赖，索引体积量级不变（每篇两条 meta）。标签 chip 同时承担「视觉识别」与「点击跳到 tag.html」两种角色，无需为结果页另写一套样式。
- **代价 / 权衡：** 结果 DOM 由脚本二次加工，依赖 Pagefind 的结果类名（`.pagefind-ui__result*`，属其公开类名空间）；`processResult` 与观察器均为运行时逻辑，无 JS 时退化为原本的标题 + 摘要。标签色相由 `blogBase['labelHueDict']` 决定，状态文件里没记录的标签回退默认 210（视觉上仍和谐，但失去了「同名标签同色」的稳定性——仅限老数据）。
- **未解决风险：** 标签存为单个 JSON 值，标签极多时会拉长该 meta；当前量级无影响。

## 实施位置

- 索引输入：`templates/post.html`（`head` 的两条 meta）
- 结果渲染：`templates/search.html`（`processResult`、`decorate`、标题行 flex 样式）
- 图标：`templates/base.html#renderIcon`、`icons.py#ICONS`

## 验证

- 端到端实测：真实模板渲染一篇文章 → `npx pagefind` 建索引 → 解压 fragment，确认 `meta.labels` 为 `["前端","blog"]`、`meta.source` 为 issue 链接。
- `pytest`（变更相关用例 50 passed）：`TestSearchResultMeta`（含 meta 语法与取值、标签合并为单值且只有一条 meta、检索页具备补挂钩子与同款图标、meta 挂在标题行内）、`TestSearchResultLabelLink`（6 条：色相字典注入、空字典兜底、装饰器创建 `<a class="Label">`、`.Label` 类复用、URL 编码结构、元信息整块仍挂标题行内）、`TestLabelHueTheme`、`TestLabelColorMode`、`TestNavNeighbors`、`TestListNavOrderConsistency`、`TestTocIndicators`、`TestSearchBox`、`TestIconButtonUnification`、`TestSectionsFold`。
- `node --check` 校验检索页内联脚本通过；Node + 最小 DOM 桩验证 `processResult` 入参收集、跨前缀 pathname 兜底、无 meta 时不挂、**meta 父节点为 `.pagefind-ui__result-title`**、重复触发不重复挂载；**新增**：每个标签 `<a>` 的 `className === 'Label'`、注入 `--label-hue`（真实色相 17/42/290 而非默认 210）、`href === "<homeUrl>/tag.html#" + encodeURIComponent(name)`，覆盖中英 / ASCII / 含 `?` 的标签名。

## 关联文档

- [ADR-0007](ADR-0007-on-site-search-pagefind.md)：本 ADR 在其检索页与索引范围之上扩展结果的展示内容。
- [ADR-0026](ADR-0026-pagefind-search-performance.md)：在本 ADR 的 `processResult` / 装饰器结构之上做精简（取消 URL 双键、装饰器 raf 节流），不改变结果展示内容。

## 下一步

无需后续动作。
