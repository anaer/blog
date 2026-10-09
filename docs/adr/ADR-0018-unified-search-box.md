# ADR-0018：三处搜索框统一为共享组件

**状态：** 已接受
**创建时间：** 2026-10-08

> **当前状态 / 核心结论：** 列表页 / 标签页 / 文章页的搜索框统一为 `base.html` 的共享 `.site-search` 组件（圆角输入框 + 图标提交按钮，配色走主题变量），窄屏保留并收窄；旧的两套实现（`.subnav-search` / `.post-search`）与两处无样式、无 JS 引用的游离图标一并移除。下一步无需后续动作。

---

## 背景

三处搜索框此前是三套互不相干的实现，视觉与窄屏行为均割裂：

| 位置 | 输入框 | 按钮 | 窄屏 | 冗余 |
|------|--------|------|------|------|
| `templates/plist.html` | Primer `.form-control` 160px、右侧直角 | `.btn` 文字「搜索」、左侧直角 | ≤767px 整块隐藏 | 游离图标（无任何 CSS 定义） |
| `templates/tag.html` | 同上 + 内联 `height:32px` | 同上 | 保留 | 游离图标 + `id="searchSVG"`（无任何 JS 引用） |
| `templates/post.html` | 自定义圆角 6px、120→170px(focus) | 透明图标按钮 | 保留 | — |

差异集中在四点：分段式（form-control + 文字按钮）vs 圆角输入框 + 图标按钮；窄屏行为不一致（列表页隐藏、另两页保留）；标签页硬编码内联高度；两套类名。

## 决策

1. **抽为共享组件 `.site-search`**：样式只在 `templates/base.html` 定义一次，三页复用。列表页 / 文章页用 `<form class="site-search">`；标签页用 `<div class="site-search">`——其搜索是本地筛选，按钮走 `searchShow()` 而非提交。
2. **视觉以文章页那套为基准**：圆角输入框 + 图标提交按钮，宽度聚焦时展开；配色走 Primer 两级回退（`--fgColor-* → --color-*`），明暗自适应，不再需要单独的深色覆盖。
3. **窄屏保留**：≤767px 收窄输入框（104px、聚焦 132px）而非整块隐藏——此前列表页隐藏搜索框，既与另两页不一致，也使移动端失去检索入口。
4. **清死代码**：移除两处游离搜索图标（无 CSS 定义、`searchSVG` 无 JS 引用）；标签页的 JS 钩子由 `.subnav-search-input` 改为 `.site-search-input`。

   - 不做什么：不改标签页的本地筛选行为（仍是 JS 过滤，不提交检索页）；不为搜索框新增 Enter 提交等交互。

## 后果

- **收益：** 三处视觉与窄屏行为一致；样式单点维护；深色模式无需逐页覆盖；移动端恢复检索入口。
- **代价 / 权衡：** 组件样式上移到 `base.html`，改动会影响全部三页（属预期）；`base.html` 内联样式增加约 0.6KB。

## 实施位置

- 组件样式：`templates/base.html`（`.site-search`）
- 使用方：`templates/plist.html`、`templates/tag.html`（含 `searchShow` 使用的 `.site-search-input` 钩子）、`templates/post.html`

## 验证

- `pytest` 153 passed（新增 `TestSearchBoxUnification` 5 例：三页均含 `class="site-search"`、组件仅在 base 定义一次、旧类名与 `searchSVG` 无残留、窄屏保留、标签页 JS 钩子已换）。
- 渲染核对：三页均无 `.post-search` / `.subnav-search`；`node --check` 校验标签页内联脚本通过。

## 关联文档

- [ADR-0012](ADR-0012-post-page-search-box.md)：本 ADR 将其 `form.post-search` 与文章页内联样式并入共享组件。
- [ADR-0026](ADR-0026-pagefind-search-performance.md)：本 ADR 的共享组件被其「首页 idle 预拉 pagefind-ui.js」复用——`base.html` 在 `.site-search` 同一上下文里追加 idle prefetch。

## 下一步

无需后续动作。
