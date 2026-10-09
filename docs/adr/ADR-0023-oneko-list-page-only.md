# ADR-0023：oneko 小猫仅列表页展示

**状态：** 已接受
**创建时间：** 2026-10-09

> **当前状态 / 核心结论：** oneko.js 从 `base.html` 全站加载收敛为仅列表页（`plist.html`）加载；文章页、标签页、检索页不再加载。下一步：实施后触发一次构建使存量页面生效。

---

## 背景

oneko.js 是纯装饰性脚本（鼠标跟随小猫），当前经 `base.html` 加载于全站每个页面。文章页读者以阅读为主，装饰动画干扰注意力且白耗 5.2KB/页。列表页停留时间短、浏览属性强，保留装饰合理。

## 决策

1. **加载范围收敛到列表页**：`templates/base.html` 中删除 oneko `<script>` 引用；`templates/plist.html` 在 `script` 块（或 body 末尾）单独引入。
2. **仅主列表页生效**：`tag.html`、`search.html`、`post.html`、单页均不加载。用户表述「只在列表页展示」取最小实现——不扩展到标签/检索页。
   - 不做什么：不加配置开关（当前无此需求）；不改 oneko.js 内部逻辑。

## 后果

- **收益：** 文章页减少 5.2KB 无用脚本；阅读体验无装饰干扰。
- **代价 / 权衡：** 标签页、检索页同步失去小猫（用户未明确要求保留）；若后续希望标签页也有，需另开决策。

## 实施位置

- 移除：`templates/base.html`（oneko script 引用）
- 新增：`templates/plist.html#script`（script 块引入 oneko）
- 测试：`tests/test_pipeline.py#TestOnekoListPageOnly`

## 下一步

实施后触发一次 `workflow_dispatch` 全量构建，使存量文章页移除 oneko 加载。
