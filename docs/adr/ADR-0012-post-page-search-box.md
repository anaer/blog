# ADR-0012：文章页搜索框

**状态：** 已接受
**创建时间：** 2026-10-08

> **当前状态 / 核心结论：** 文章页头部新增搜索表单，GET 提交到站内检索页 `homeUrl/search.html?q=`，复用 ADR-0007 的检索页（读取 `?q=` 触发）。不引入新依赖、不经过 GitHub。下一步无。

---

## 背景

站内检索页（`search.html`，见 ADR-0007）已从列表页可达，但文章页无检索入口，读者需返回列表才能发起检索。

## 决策

1. **复用既有检索页**：`templates/post.html` 头部新增 `form.post-search`，`action="{{ blogBase['homeUrl'] }}/search.html"`、`method="get"`、输入 `name="q"`；提交后落到 ADR-0007 的检索页，`?q=` 由 Pagefind UI 的 `triggerSearch` 承接。
2. **内联样式、明暗自适应**：输入框 + 图标提交按钮，宽度聚焦时展开；配色走 Primer 变量两级回退（`templates/post.html` 的 style 块）。
   - 不做什么：不在文章页内嵌独立检索结果（避免重复加载 Pagefind 与结果 UI）；不跳转 GitHub。

## 后果

- **收益：** 文章页可直接发起检索，入口与列表页一致；零新增依赖、零运行时成本（仅静态表单）。
- **代价 / 权衡：** 提交会离开当前文章页进入检索页（与列表页行为一致）。

## 实施位置

- `templates/post.html`（header 表单、`{% block style %}` 的 `.post-search` 样式）

## 关联文档

- 复用检索页与索引逻辑：[ADR-0007 站内检索](ADR-0007-on-site-search-pagefind.md)

## 验证

- `tests/test_pipeline.py` 断言：post.html 含 `class="post-search"`、表单 `action` 指向 `search.html`、输入 `name="q"`。

## 下一步

无需后续动作。
