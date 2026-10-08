# ADR-0017：深色模式兼容——正文 token 与硬编码色统一到主题变量

**状态：** 已接受
**创建时间：** 2026-10-08

> **当前状态 / 核心结论：** 深色模式兼容——正文容器 `.markdown-body` 的配色 token 改按站点开关 `data-color-mode` 重绑（不再只跟随系统 `prefers-color-scheme`），文章元信息、AI 总结框、文章页搜索按钮与目录边框 / 高亮的硬编码色统一为主题变量；2026-10-08 追加：暗色调色板由 GitHub 冷蓝深改为 WorkBuddy AI 客户端的暖灰中性方向，代码块行号槽底色与悬浮按钮配色同步调整。下一步无需后续动作。

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

4. **暗色调色板调整为 WorkBuddy 暖灰中性方向**（2026-10-08 追加）：把决策 1 中 `[data-color-mode="dark"] .markdown-body` 的 12 个 token 由 GitHub 冷蓝深改为 WorkBuddy AI 客户端的暖灰中性。背景从 `#0d1117` 升到 `#1a1c20`，边框从 `#30363d / #21262d` 升到 `#383d45 / #2b2f37`，强调蓝从 `#58a6ff / #1f6feb` 降到 `#7ab8ff / #5a8fe6`，浅字从 `#c9d1d9` 升到 `#dde2e8`，整体视觉温度由"冷蓝硬"变为"暖灰柔和"。同步对 `md2html.py` 的代码块行号槽底色做相同方向调整：`rgba(110,118,129,0.22)`（蓝灰槽）→ `rgba(255,255,255,0.045)`（中性白色微染槽），1px 分隔线 `0.45` → `0.10`。`base.html` 的 `.Label` 暗色饱和度从 45% 降到 30%，底色从 22% 降到 18%。`post.html` 的悬浮按钮由 `#007bff / #0056b3` 改为 `var(--color-accent-fg) / var(--color-accent-emphasis)`，暗色下加 1px 柔光描边 `rgba(255,255,255,0.12)` 模拟 WorkBuddy 暗色按钮浮起效果。

   - **不做什么**：不复刻 GitHub 的 `--color-prettylights-syntax-*`（项目代码高亮走 `highlight.css`，不使用 `.pl-*`）；不引入 JS 动态换肤；不修改 vendored 的 `github-markdown.min.css`（升级会覆盖上游资产不可追溯）；不替换 primer-subset.css 中的 CSS 变量取值（那个文件是 vendored）；不调整 `highlight.css` 中的语法高亮色（那是代码语义色，由 pygments 派生，独立决策）。
   - **取舍**：本决策把 `[data-color-mode="dark"] .markdown-body` 与 vendored `github-markdown.min.css` 拆开了——`test_hardcoded_tokens_match_vendored_source` 不再以"两者逐字一致"为目标，而改为"vendored 仍含原始 GitHub 取值"（用于检测上游升级后值漂移，本身不变）；模板侧的暖灰中性取值由 `test_dark_tokens_use_warm_neutral_palette` 守护。两类断言各司其职。

## 后果

- **收益**：深色下正文、元信息、目录高亮、边框全部可读；正文配色与站点开关一致（不再受操作系统偏好左右）；暗色基调由"冷蓝 + 高对比"转为"暖灰中性 + 柔和对比"，与 WorkBuddy AI 客户端的视觉温度一致，长文阅读更舒适。
- **代价 / 权衡**：`post.html` 内联约 1KB token 声明；token 取值与 `github-markdown-css@5.2.0` 拆分（暗色块走自定义 WorkBuddy 调色板，浅色块仍逐字匹配上游）；升级该依赖时需同步（已由单测防漂移）。
- **未解决风险**：`--color-prettylights-syntax-*` 未重绑——本项目代码高亮走 `highlight.css`（`data-color-mode` 驱动），不使用 `.pl-*`，故无影响；若将来启用 `.pl-*` 需一并补齐。`primer-subset.css` 仍含 GitHub 风格的冷蓝 token，正文容器 `.markdown-body` 之外的元素（按钮、计数器等）会继续走 GitHub 冷蓝——这是 vendored 限制，不在本 ADR 范围内。

## 实施位置

- 模板：`templates/post.html`（`.markdown-body` token 重绑、`.post-meta`、`.post-summary`、搜索按钮色、暗色暖灰中性调色板、悬浮按钮主题变量化）
- 脚本：`assets/toc.js`（边框与高亮色）、`md2html.py`（代码块控件与暗色行号槽底色）
- 模板：`templates/base.html`（`.Label` 暗色饱和度调整）
- 测试：`tests/test_pipeline.py`（新增 `TestDarkModeContrast` 与 `test_dark_tokens_use_warm_neutral_palette` / `test_floating_button_uses_theme_var`）

## 验证

- `pytest` 205 passed（暗色 WorkBuddy 改造新增 3 例：`test_dark_tokens_use_warm_neutral_palette` 守护 8 个新 token 取值 + 8 个旧冷蓝 token 抑制、`test_floating_button_uses_theme_var` 守护硬编码 `#007bff / #0056b3` 撤掉、`TestCodeBlockResponsiveCss::test_gutter_background_dark_theme` 守护 `rgba(255,255,255,…)` 中性色替换 `rgba(110,118,129,…)`）。
- `tests/test_pipeline.py` 中 `test_hardcoded_tokens_match_vendored_source` 保留：检测 `github-markdown.css@5.2.0` 上游升级后值是否漂移，自身不要求模板侧与上游逐字一致。
- 本地端到端：见 `C:\Users\Administrator\AppData\Local\Temp\dark_theme_preview.html` —— 同一段文章内容，OLD (GitHub 冷蓝) vs NEW (WorkBuddy 暖灰) 并排对照，可直接打开浏览器预览。

## 下一步

- 可考虑：替换 `primer-subset.css` 的 GitHub 风格 token（同方向调整）。该文件是 vendored, 需谨慎评估升级策略与维护成本。
