# ADR-0010：正文标题折叠展开

**状态：** 已接受
**创建时间：** 2026-10-08

> **当前状态 / 核心结论：** 新增 `assets/sections.js`（post.html 加载），将每个标题及其后续同级/更低级内容包裹为可折叠 `.heading-section`，标题前插入 chevron 切换按钮，默认展开。下一步浏览器验证多级嵌套折叠。

---

## 背景

长文无段落折叠能力，读者无法按标题收起某节内容。

## 决策

1. **运行时分节折叠**：`assets/sections.js` 在 `DOMContentLoaded` 后将 `#postBody` 内每个 `h1–h6` 与其后续兄弟（直到同级或更高级标题）包裹为 `.heading-section`，并在标题**内部首位**插入 `button.section-toggle`（chevron SVG）；点击经事件委托切换 `.collapsed`；默认展开。
   - **选择器约束**：按钮的父节点是标题本身而非 `.heading-section`，故样式选择器须跨过标题层级——写成 `.heading-section > :is(h1,…,h6) > .section-toggle`；若用直系子代 `.heading-section > .section-toggle` 会一条都不匹配，按钮退回浏览器原生样式（含灰底与边框）。
2. **仅隐藏内容、保留标题**：折叠时 `.heading-section.collapsed > *:not(h1…h6)` 隐藏直接子内容（含嵌套 section），标题始终可见。
3. **不影响检索索引**：分节是运行时 DOM 重组，构建期 Pagefind 索引在静态 HTML 上生成（`templates/post.html#postBody` 的 `data-pagefind-body`），不受运行时折叠影响。

## 后果

- **收益：** 长文可逐节折叠，改善可读性；纯前端、零依赖；默认展开保证禁用 JS 时内容完整可读。
- **代价 / 权衡：** 标题前的 chevron 会略微改变标题排版；与 `assets/toc.js` 同时改写标题 DOM，二者顺序无关（TOC 按标签查询，分节按包裹，互不冲突）。

## 实施位置

- `assets/sections.js`、`templates/post.html`（加载脚本 + 内联样式）

## 验证

- `tests/test_pipeline.py` 静态断言：sections.js 含 `heading-section`、`section-toggle`、`classList.toggle('collapsed')`；post.html 加载 `assets/sections.js`。

## 关联文档

- [ADR-0019](ADR-0019-icon-button-unification.md)：统一 `.section-toggle` 的交互、配色与垂直对齐（chevron 不再按 x-height 中线对齐）。

## 下一步

浏览器验证多级标题嵌套折叠正确、与 TOC 高亮共存。
