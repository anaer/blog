# ADR-0025：站点 UI 图形一律走图标注册表，不用 emoji

**状态：** 已接受
**创建时间：** 2026-10-09

> **当前状态 / 核心结论：** 文章页浏览量 👁、编辑悬浮按钮 🖋、新增悬浮按钮 `+` 三处改走 `icons.py` 注册表（`eye` / `pen` / `plus`）；约定站点 UI 图形不以 emoji 或文本字符充当。下一步：触发一次全量构建。

---

## 背景

ADR-0014 已把站点图标收敛到 `icons.py`，但文章页仍残留三处非注册表图形：👁 浏览量、🖋 编辑按钮、`+` 新增按钮——emoji 各平台渲染不一致且不受主题色控制，文本字符与图标风格脱节。

## 决策

1. `icons.py#ICONS` 新增 `eye`、`pen`（`plus` 已有，24×24 线性描边）。
2. `post.html` 三处改为宏渲染：`icons.icon('eye', size=16, svg_class='vercount-icon')`、`icons.icon('pen', size=16)`、`icons.icon('plus', size=16)`；悬浮按钮内图标 `stroke=currentColor` 继承按钮配色，浏览量图标另加 `.vercount-icon`（`vertical-align:calc(0.35em - 8px)` + `--color-fg-muted`），与相邻 `.post-meta` 同基线同色。
3. 约定：站点 UI 图形（悬浮按钮、行内计数、元信息前缀）一律取自注册表，不以 emoji / 文本字符替代。
4. 不做什么：`.github` workflow 提交信息里的 🎉、`docs/review` 报告里的 ✅ 不进页面，保持原样。

## 实施位置

- `icons.py#ICONS`（`eye` / `pen`）；`templates/post.html`（vercount 容器、`.edit-post`、`.new-post`、`.vercount-icon` 样式）
- 测试：`tests/test_pipeline.py#TestIconRegistry.REQUIRED`、`tests/test_pipeline.py#TestIconTemplates#test_post_ui_glyphs_are_svg_not_emoji`

## 验证

- `pytest` 214 passed（新增 1 例守卫「页面无 emoji / 文本字符残留」）。

## 关联文档

- [ADR-0014](ADR-0014-icon-registry-single-source.md)：本 ADR 复用其注册表与渲染宏，补全其覆盖范围（UI 图形不用 emoji）。

## 下一步

实施后触发一次 `workflow_dispatch` 全量构建，使已发布文章页生效。
