# ADR-0022：文章页用「按标签关联文章」取代「上一篇/下一篇」

**状态：** 已接受
**创建时间：** 2026-10-08
**取代：** ADR-0006（文章上一篇/下一篇导航）

> **当前状态 / 核心结论：** 文章页底部不再渲染上一篇/下一篇，改为按共享标签数排序的「相关文章」列表；关联数据由 `nav.json`（新增 `labels` 字段）提供，`assets/nav.js` 在运行时计算并渲染，无命中则整块移除。相邻刷新机制（`nav_neighbors`/`neighbor_keys`/`get_nav_keys`）随之删除。下一步：部署后触发一次全量构建，让所有文章页拿到新模板。

---

## 背景

上一篇/下一篇是「按列表序的相邻两篇」，对读者的实际价值有限：相邻关系只反映发布时间的巧合，与内容相关性无关（`post/166` 的下一篇可能是一个完全不同主题的短文）。同时它带来持续的构建期成本——为了保持静态兜底正确，`runOne` 每次增量构建都要连带重渲染旧邻与新邻。

标签是站内已有的、语义最强的相关性信号（`tag.html` 已用它做筛选），且新文章的关联位不需要旧文章回刷——只要数据源是全量的。

## 决策

1. **关联度 = 与当前文章共享的标签数**：`assets/nav.js` 读取文章页 `data-labels`，对 `nav.json` 每条算共享标签数，剔除自身与 0 分条目，按分数降序取前 5 条。
   - **同分不另设优先级**：`Array.prototype.sort` 稳定，因此同分条目直接沿用 `nav.json` 的列表序（置顶优先、更新时间降序，见 `Gmeek.py#list_order`），无需把 `updatedAt` 一并下发。
   - 不做语义相似度/embedding、不按标题词重合打分：站内没有相应基础设施，标签已由作者手工维护，是成本最低且可解释的信号。
2. **纯运行时渲染，取消静态兜底**（相对 ADR-0006 的主要改变）：
   - 服务端不再往文章页写任何相邻链接；`createPostHtml` 只输出「当前文章是谁、打了哪些标签」四个钩子（`data-nav-url`/`data-post-number`/`data-labels`/`data-heading`）。
   - `nav.json` 每次构建全量重写并新增 `labels`，因此新增文章、修改标签都不需要回刷其他文章页 → 删除 `nav_neighbors`、`neighbor_keys`、`GMEEK.get_nav_keys`、`GMEEK._nav_keys`，`runOne` 只渲染变更的那一篇。
   - 承继 ADR-0006 的判断：数据不内联进各页（会冻结在各自构建时刻），改用**单一、全量、每次重建**的数据文件；`nav.json` 可被浏览器跨文章页复用。
   - 文件名保留 `nav.json`：增量部署只重写文件内容、不改名字，改名会在 `docs/` 留下上一版的孤儿文件。
3. **空结果一律收起**：当前文章无标签、无任何共享标签的候选、数据拉取失败或格式异常，都由脚本 `box.remove()` 移除整个区块，不留空壳与占位。
4. **视觉沿用列表页语言**：容器复用 Primer 的 `SideNav` + `border`，条目用 `SideNav-item` 加 `renderIcon('post', …)` 图标（与 `plist.html`、`tag.html` 同一套），标题单行省略。不引入新配色。

## 后果

- **收益：** 关联位从「时间巧合」变成「主题相近」；增量构建的连带重渲染归零（每篇变更少渲染 1–2 个页面）；`nav.json` 仍是唯一数据源，序与列表页一致。
- **代价 / 权衡：**
  - 无 JS 环境（以及搜索引擎爬虫）看不到关联链接——ADR-0006 的静态兜底换来了这一点，本次按用户选择放弃。
  - Pagefind 索引在构建期生成，运行时注入的关联链接不进检索索引。
  - 每篇文章页仍有一次 `nav.json` 请求（与旧方案同量级，可被浏览器缓存）。
  - 老文章页在**下一次全量构建之前**仍是旧模板产物：不含 `.related-posts` 容器，新 `nav.js` 找不到容器会静默返回，于是这些页面既不显示关联也没有报错，但会显示上一次构建残留的上一篇/下一篇。故必须触发一次 `workflow_dispatch` 全量构建。
- **未解决风险：** 单页（`singlePage`，如 `link`/`about`）不在 `nav.json` 内；若某篇普通文章恰好带上与单页同名的标签，该单页会显示关联区块。当前无此数据，不为此加特判。

## 实施位置

- 关联数据：`Gmeek.py#GMEEK.createNavJson`（新增 `labels`）、`Gmeek.py#nav_order`
- 文章页钩子：`Gmeek.py#GMEEK.createPostHtml`、`templates/post.html`（`.related-posts` 区块与样式）
- 运行时：`assets/nav.js`
- 增量构建：`Gmeek.py#GMEEK.runOne`（不再回刷相邻）
- 文案：`Gmeek.py#i18nCN`/`i18n` 的 `relatedPosts`
- 测试：`tests/test_pipeline.py`（`TestRelatedOrder`、`TestRunOneRendersOnlyChangedPost`、`TestCreatePostHtmlRelated`、`TestCreateNavJson`、`TestTemplateSmoke`、`TestRelatedArticlesContract`）

## 验证

- `pytest` 201 passed。关键守护：
  - `TestCreateNavJson::test_exports_labels_for_relation_scoring` / `test_missing_labels_default_empty`：`labels` 必须导出，老状态文件缺字段不得崩。
  - `TestRunOneRendersOnlyChangedPost`（负向控制）：新增或重排都只渲染变更那一篇，旧实现会连带渲染相邻。
  - `TestCreatePostHtmlRelated::test_no_neighbor_fields_written` 与 `test_list_pagination_fields_are_not_leaked`：文章页数据里不得出现 prev/next 字段（含从列表页 `blogBase` 复制而来的残留）。
  - `TestTemplateSmoke::test_post_has_no_prev_next_markup`：模板不再输出分页区块；`test_post_related_labels_survive_quotes` 钉死 `data-labels` 用 `|tojson` 的 HTML 安全转义仍可被 `JSON.parse` 还原。
  - `TestRelatedArticlesContract`：模板属性名/类名与 `nav.js` 读取一致，且两侧都无 prev/next 残留。
- Node + 最小 DOM 桩逐条跑 `assets/nav.js`（临时脚手架，未入库）：分数降序且同分保序、上限 5 条、自身排除、无命中/无标签/坏 JSON/缺编号/拉取失败均移除整块、条目缺 `labels` 时跳过、页面无容器时静默返回。
- `TestAdrBoundary` 通过：代码侧不写本编号。

## 下一步

部署后触发一次全量构建（`workflow_dispatch`），使所有文章页重渲染为关联区块；此后 `nav.json` 供数据，增量构建无需连带刷新。
