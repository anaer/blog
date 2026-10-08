# ADR-0012：文章页搜索框

**状态：** 已接受
**创建时间：** 2026-10-08

> **当前状态 / 核心结论：** 文章页头部新增搜索表单，GET 提交到站内检索页 `homeUrl/search.html?q=`，复用 ADR-0007 的检索页（读取 `?q=` 触发）。不引入新依赖、不经过 GitHub。下一步无。

---

## 背景

站内检索页（`search.html`，见 ADR-0007）已从列表页可达，但文章页无检索入口，读者需返回列表才能发起检索。

## 决策

1. **复用既有检索页**：`templates/post.html` 头部新增搜索表单，`action="{{ blogBase['homeUrl'] }}/search.html"`、`method="get"`、输入 `name="q"`；提交后落到 ADR-0007 的检索页，`?q=` 由 Pagefind UI 的 `triggerSearch` 承接。
2. **样式复用共享组件**：表单用 `templates/base.html` 的 `.site-search`（圆角输入框 + 图标提交按钮，配色随主题），文章页不再自带搜索框样式。
   - 不做什么：不在文章页内嵌独立检索结果（避免重复加载 Pagefind 与结果 UI）；不跳转 GitHub。

## 后果

- **收益：** 文章页可直接发起检索，入口与列表页一致；零新增依赖、零运行时成本（仅静态表单）。
- **代价 / 权衡：** 提交会离开当前文章页进入检索页（与列表页行为一致）。

## 实施位置

- `templates/post.html`（header 的 `.site-search` 表单）

## 关联文档

- 复用检索页与索引逻辑：[ADR-0007 站内检索](ADR-0007-on-site-search-pagefind.md)
- [ADR-0018](ADR-0018-unified-search-box.md)：本 ADR 引入的 `form.post-search` 与内联样式已并入共享 `.site-search` 组件。

## 验证

- `tests/test_pipeline.py` 断言：post.html 含 `class="site-search"`、表单 `action` 指向 `search.html`、输入 `name="q"`。

## 下一步

无需后续动作。
