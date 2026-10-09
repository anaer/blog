# ADR-0024：文章列表项标题后添加 issue 入口

**状态：** 已接受
**创建时间：** 2026-10-09

> **当前状态 / 核心结论：** 列表页每篇文章条目在标题后追加 issue 链接图标，指向该文章对应的 GitHub issue（`postSourceUrl`）；视觉沿用 ADR-0021 检索结果的 issue 图标样式。下一步：实施后触发一次构建。

---

## 背景

列表页当前只能点击标题跳转到文章页，无法直达对应 GitHub issue（评论、编辑、原始 Markdown）。页头虽有全局「Issue」按钮（跳转 issue 列表页），但缺少逐篇直达入口。`postListJson` 每条已含 `postSourceUrl` 字段（`Gmeek.py#GMEEK.addOnePostJson` 生成），数据无需新增。

## 决策

1. **入口位置**：`templates/plist.html` 列表项内，标题 `<span>` 之后、右侧 `.listLabels` 之前，插入 issue 图标链接。
2. **链接目标**：`postSourceUrl`（该文章对应的 GitHub issue URL），`target="_blank"` 新开。
3. **视觉样式**：复用 `base.html#renderIcon('github')` 图标（与页头 Issue 按钮、文章页 Issue 按钮同源）；常态 `opacity:.6` + muted 色，hover 转不透明（对齐 ADR-0019 内容区图标按钮语言）。窄屏不隐藏。
4. **不做什么：** 不在 `tag.html` / 检索页列表项重复添加（检索页已有 ADR-0021 的 issue 入口；标签页暂无此需求）。

## 后果

- **收益：** 列表页直达每篇文章的 issue，评论/编辑路径缩短；`postSourceUrl` 已有数据，零后端改动。
- **代价 / 权衡：** 列表项视觉元素增多一枚图标；标题过长时图标与标题同行可能挤压——用 `opacity` 低对比弱化，不抢标题视觉权重。

## 实施位置

- 模板：`templates/plist.html`（列表项标题后 `.list-issue-link`，经 `<object>` 包裹规避嵌套 `<a>`）
- 样式：`templates/plist.html#style`（`.list-issue-link` 低对比 + hover 提亮）
- 图标：`icons.py#github` 经 `templates/macro.html#icon` 渲染
- 测试：`tests/test_pipeline.py#TestListItemIssueEntry`

## 下一步

实施后触发一次 `workflow_dispatch` 全量构建，使列表页所有分页生效。
