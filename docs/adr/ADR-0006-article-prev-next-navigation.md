# ADR-0006：文章上一篇/下一篇导航——运行时计算 + 构建期兜底

**状态：** 已接受
**创建时间：** 2026-09-30

> **当前状态 / 核心结论：** 上一篇/下一篇改为「构建期输出全站导航数据 `nav.json` + 文章页运行时计算填充」，解决增量构建导致的相邻链接过期；同时保留服务端静态渲染作为无 JS 兜底，并让增量构建连带刷新相邻文章以保持兜底正确。下一步为部署后触发一次全量构建。

---

## 背景

上一篇/下一篇原为构建期由 Jinja 直接写死进静态 HTML（`Gmeek.py#nav_neighbors` 计算、`Gmeek.py#GMEEK.createPostHtml` 赋值、`templates/post.html` 渲染）。但 `runOne`（issue 事件触发的增量构建）只重渲染当前这一篇，不刷新相邻文章 → 相邻文章里的链接停留在其上次渲染时的顺序，互相矛盾。线上实证：`post/166` 的 next=167，但 `post/167` 的 prev=168（若 166→167，则 167 的 prev 必须是 166）。

## 决策

1. **构建期输出全站导航数据**：每次构建（全量/增量）写出 `docs/nav.json`，为按**列表序**（`Gmeek.py#list_order`：置顶优先、更新时间降序、编号兜底）排列的 `[{number,title,url}]`，作为唯一数据源。
   - **序列单一来源**：列表页、导航数据、`runAll` 预排一律走 `Gmeek.py#list_order`，不得各写一套排序——此前三处分别用 `(top, updatedAt)`、`(top, createdAt)`、`(createdAt, number)`，键与方向均不一致，正是「文章页上一篇/下一篇与列表上下相邻对不上」的成因。
2. **运行时计算并填充**：文章页由 `assets/nav.js` 拉取 `nav.json`，用页面上的当前文章编号定位，重写 `.previous_page`/`.next_page` 的 href 与文案；该方向无相邻文章时移除对应链接。方向与列表一致——**上一篇 = 列表中的上一条（更新），下一篇 = 下一条（更旧）**。
3. **静态渲染保留为兜底**：服务端仍将 prev/next 渲染进 HTML（无 JS/爬虫可读）；增量构建 `runOne` 连带重渲染旧/新相邻文章（`neighbor_keys`），使兜底也保持正确。
   - 不做什么：不把导航数据内联进每篇文章页（各页仍冻结在各自构建时刻，无法解决过期）；不引入运行期额外服务。

## 后果

- **收益：** 上一篇/下一篇始终与最新文章顺序一致，不依赖该页自身何时被构建；无 JS 环境仍有可用链接。
- **代价 / 权衡：** 每篇文章页多一次 `nav.json` 请求；链接在 JS 执行后才校正（首屏可能短暂显示静态值）；`nav.json` 拉取失败时回退静态兜底（可能过期）。
- **未解决风险：** 若构建未运行，静态兜底仍可能过期，此时以运行时结果为准。

## 实施位置

- 导航数据：`Gmeek.py#GMEEK.createNavJson`、`Gmeek.py#GMEEK.runAll`、`Gmeek.py#GMEEK.runOne`
- 相邻刷新：`Gmeek.py#neighbor_keys`、`Gmeek.py#GMEEK.runOne`
- 模板：`templates/post.html`（`data-nav-url`/`data-post-number`、分页两端对齐）
- 运行时：`assets/nav.js`
- 测试：`tests/test_pipeline.py`

## 验证

- `pytest` 74 passed（含导航序、相邻刷新、`nav.json` 输出、模板钩子）。
- 列表/导航同序：`TestListNavOrderConsistency` 断言 `nav_order` 与 `list_order` 出自同一序列，且按 `updatedAt`（而非 `createdAt`）排序；`TestNavNeighbors` 覆盖置顶改变相邻关系、已关闭沉底、编号兜底。
- Node + 最小 DOM 桩验证 `assets/nav.js`：中间文章双链接、端点仅单链接、无相邻时移除、拉取失败保留静态兜底。

## 下一步

部署后触发一次全量构建（`workflow_dispatch`），生成 `nav.json` 并修正线上既有链接。
