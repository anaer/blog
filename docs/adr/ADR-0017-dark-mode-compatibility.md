# ADR-0017：深色模式兼容——正文 token 与硬编码色统一到主题变量

**状态：** 已接受
**创建时间：** 2026-10-08

> **当前状态 / 核心结论：** 深色模式兼容——正文容器 `.markdown-body` 的配色 token 改按站点开关 `data-color-mode` 重绑（不再只跟随系统 `prefers-color-scheme`），文章元信息、AI 总结框、文章页搜索按钮与目录边框 / 高亮的硬编码色统一为主题变量。下一步无需后续动作。

---

## 背景

站点用 `<html data-color-mode="light|dark">` + `localStorage.meek_theme` 做手动主题切换（见 `base.html#modeSwitch`）。审计发现三类内容在深色下会「消失」：

### 1. 正文容器与站点开关不同步（影响最大）

`github-markdown-css@5.2.0` 只用 **`@media (prefers-color-scheme: …)`** 切换它自己的 `--color-*` token，**完全不看 `data-color-mode`**：

```css
@media (prefers-color-scheme:dark){ .markdown-body{color-scheme:dark;--color-fg-default:#c9d1d9;…} }
@media (prefers-color-scheme:light){ .markdown-body{color-scheme:light;--color-fg-default:#24292f;…} }
```

而 `.markdown-body` 又是 `color:var(--color-fg-default)`、`background-color:var(--color-canvas-default)`。于是「系统浅色 + 站点切到深色」时，页面底变深、正文仍是 `#24292f` 深字 → **整篇正文不可见**。

### 2. 硬编码颜色只在浅色下可读

| 位置 | 原值 | 深色下表现 |
|------|------|-----------|
| `post.html` 文章元信息（发布于/更新于） | 内联 `color:#666`、`<time color:#333>` | 深灰压深底 → 不可见 |
| `post.html` AI 总结框边框 | `1px dashed #ccc` | 刺眼、与主题不符 |
| `post.html` 文章页搜索按钮 | `color:#6e7681` | 偏暗 |
| `toc.js` 目录当前项高亮 | `background-color:#b6e3ff`（固定浅蓝） | 文字 `--color-diff-blob-addition-num-text` 深色下为 `#e6edf3`，浅字压浅蓝 → 几乎同色 |
| `toc.js` 目录边框 | `#e1e4e8` / `#ddd` | 结构线消失 |

### 3. 已正确跟随主题的部分（无需改动）

`primer-subset.css`、`highlight.css`（`[data-color-mode="dark"] .highlight …`）、`md2html.py` 代码块控件（均有 `[data-color-mode="dark"]` 覆盖）——这些是本次的对照基线。

## 决策

1. **正文 token 按站点开关重绑**：在 `post.html` 中按 `data-color-mode` 重新声明 `.markdown-body` 消费的 12 个 token（取值逐字取自 `github-markdown-css@5.2.0` 的明/暗两块）：

   ```css
   [data-color-mode="light"] .markdown-body{ --color-fg-default:#24292f; … }
   [data-color-mode="dark"]  .markdown-body{ --color-fg-default:#c9d1d9; … }
   ```

   特异性 (0,2,0) > `.markdown-body` (0,1,0)，且本 `<style>` 在 `<link>` 之后，故稳定覆盖那两个 `prefers-color-scheme` 块；正文从此跟随站点开关。

2. **硬编码色改为主题变量**：`--color-fg-muted` / `--color-fg-default` / `--color-border-default` / `--color-border-muted` / `--color-canvas-subtle` / `--color-accent-subtle`（均已在 `primer-subset.css` 中按主题定义，各 19 处）。
   - 元信息抽为 `.post-meta` / `.post-meta time`，AI 总结框抽为 `.post-summary`，去掉内联样式。
   - 目录当前项高亮 `#b6e3ff` → `var(--color-accent-subtle)`（浅 `#ddf4ff` / 深 `rgba(56,139,253,0.1)`）。

3. **渲染版本递增**：`RENDER_VERSION` 6→…→**8**（`post.html` 内联进每个文章页，需全站重转）。

   - 不做什么：不改 vendored 的 `github-markdown.min.css`（升级会覆盖，且改动上游资产不可追溯）；不引入 JS 动态换肤；不动 `toc.js` 的交互逻辑。

## 后果

- **收益**：深色下正文、元信息、目录高亮、边框全部可读；正文配色与站点开关一致（不再受操作系统偏好左右）。
- **代价 / 权衡**：`post.html` 内联约 1KB token 声明；token 取值与 `github-markdown-css@5.2.0` 耦合，升级该依赖需同步（已由单测防漂移）。
- **未解决风险**：`--color-prettylights-syntax-*` 未重绑——本项目代码高亮走 `highlight.css`（`data-color-mode` 驱动），不使用 `.pl-*`，故无影响；若将来启用 `.pl-*` 需一并补齐。

## 实施位置

- 模板：`templates/post.html`（`.markdown-body` token 重绑、`.post-meta`、`.post-summary`、搜索按钮色）
- 脚本：`assets/toc.js`（边框与高亮色）
- 版本：`Gmeek.py#RENDER_VERSION`
- 测试：`tests/test_pipeline.py`（新增 `TestDarkModeContrast`）

## 验证

- `pytest` 147 passed（新增 5 例：元信息无 `#333`/`#666`、总结框边框随主题、`.markdown-body` 双向绑定存在、硬编码 token 与 vendored 源逐字一致、`toc.js` 无浅色硬编码）。
- `node --check assets/toc.js` 通过。
- 本地端到端：真实模板渲染一篇含标题/代码块/表格/引用/AI 摘要的文章，强制 `data-color-mode="dark"` 对照，修复前正文与元信息不可见、修复后正常。

## 下一步

无需后续动作。
