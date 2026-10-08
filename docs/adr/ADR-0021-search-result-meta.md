# ADR-0021：检索结果展示文章标签与 issue 入口

**状态：** 已接受
**创建时间：** 2026-10-08
**最近更新：** 2026-10-08（决策 2 的挂载点由页脚改为标题行内）

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

## 后果

- **收益：** 结果卡片首行即可看见标签与 issue 入口，水平密集地展示相关性线索；零新增依赖，索引体积量级不变（每篇两条 meta）。
- **代价 / 权衡：** 结果 DOM 由脚本二次加工，依赖 Pagefind 的结果类名（`.pagefind-ui__result*`，属其公开类名空间）；`processResult` 与观察器均为运行时逻辑，无 JS 时退化为原本的标题 + 摘要。
- **未解决风险：** 标签存为单个 JSON 值，标签极多时会拉长该 meta；当前量级无影响。

## 实施位置

- 索引输入：`templates/post.html`（`head` 的两条 meta）
- 结果渲染：`templates/search.html`（`processResult`、`decorate`、标题行 flex 样式）
- 图标：`templates/base.html#renderIcon`、`icons.py#ICONS`

## 验证

- 端到端实测：真实模板渲染一篇文章 → `npx pagefind` 建索引 → 解压 fragment，确认 `meta.labels` 为 `["前端","blog"]`、`meta.source` 为 issue 链接。
- `pytest`（变更相关用例 44 passed）：`TestSearchResultMeta`（含 meta 语法与取值、标签合并为单值且只有一条 meta、检索页具备补挂钩子与同款图标、meta 挂在标题行内）、`TestLabelHueTheme`、`TestLabelColorMode`、`TestNavNeighbors`、`TestListNavOrderConsistency`、`TestTocIndicators`、`TestSearchBox`、`TestIconButtonUnification`、`TestSectionsFold`。
- `node --check` 校验检索页内联脚本通过；Node + 最小 DOM 桩验证 `processResult` 入参收集、跨前缀 pathname 兜底、无 meta 时不挂、**meta 父节点为 `.pagefind-ui__result-title`**、重复触发不重复挂载。

## 关联文档

- [ADR-0007](ADR-0007-on-site-search-pagefind.md)：本 ADR 在其检索页与索引范围之上扩展结果的展示内容。

## 下一步

无需后续动作。
