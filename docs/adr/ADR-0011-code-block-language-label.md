# ADR-0011：代码块语法语言标签

**状态：** 已接受
**创建时间：** 2026-10-08

> **当前状态 / 核心结论：** 代码块左上角展示围栏语法（如 python/bash）。高亮器会丢弃 `language-xxx`，故在转换前按出现顺序预扫描围栏语言，转换后按 `<pre>` 顺序回填 `<span class="code-lang">` 标签。下一步无。

---

## 背景

代码块（含复制/折叠按钮，`md2html.py`）不显示所用语言；pygments 高亮后 `language-xxx` 类被丢弃，渲染结果里取不到语言。

## 决策

1. **预扫描 + 顺序回填**：`md2html.py#Markdown2GithubHtml._extract_fence_langs` 在转换前按出现顺序提取围栏语言；`md2html.py#Markdown2GithubHtml._add_controls` 在遍历 `<pre>` 时按相同顺序取用，生成 `<span class="code-lang">lang</span>`；无语言（纯 ```）不加标签。
2. **样式与留白**：命中语言时包装器加 `has-lang` 类（顶部留白避免压字），标签左上角展示，配色随明暗模式（`md2html.py#Markdown2GithubHtml.EXTRA_JS`）。
   - 不做什么：不强行改高亮器以保留 `language-` 类（会牵动高亮 CSS/主题），仅在展示层回填。
   - 已知限制：纯缩进代码块（无围栏）无语言；若正文同时含围栏与缩进代码块，标签按「围栏顺序」对齐、缩进块不计入——本博客约定用围栏，风险低。

## 后果

- **收益：** 代码块可见语法提示；纯前端、零新增依赖。
- **代价 / 权衡：** 标签依赖「围栏顺序 = `<pre>` 顺序」的假设，与渲染器内部结构耦合（已在测试中断言顺序一致）。

## 实施位置

- `md2html.py#Markdown2GithubHtml._extract_fence_langs`、`md2html.py#Markdown2GithubHtml._add_controls`、`md2html.py#Markdown2GithubHtml.EXTRA_JS`

## 验证

- `tests/test_pipeline.py` 断言：围栏语言提取顺序、转换后含 `class="code-lang"` 与语言文本、纯围栏无标签、双围栏标签顺序正确。

## 关联文档

- [ADR-0015](ADR-0015-code-block-line-height-wrap-mobile.md)：修订本 ADR 决策 2 的 `has-lang` 顶部留白（移动端间距随之调整）。

## 下一步

无需后续动作。
