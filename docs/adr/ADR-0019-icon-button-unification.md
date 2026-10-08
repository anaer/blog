# ADR-0019：内容区图标按钮统一交互与配色

**状态：** 已接受
**创建时间：** 2026-10-08

> **当前状态 / 核心结论：** 正文标题折叠、目录 +/−、代码块控件三族图标按钮统一为同一套交互与配色语言——常态 `opacity:.6` + 主题 muted 色，hover 转不透明并加主题背景，`border-radius:4px`；图标尺寸按上下文保留 12/14/16。原两级硬编码灰（`#6e7681` / `#8b949e`）全部改走主题变量。下一步无需后续动作。

---

## 背景

同一篇文章页里存在三族图标按钮，各自独立定义，彼此都不一致：

| | 标题折叠 `.section-toggle` | 目录 +/− `.toc-toggle` | 代码块控件 |
|---|---|---|---|
| 定义处 | `assets/sections.js` | `assets/toc.js` | `md2html.py` `EXTRA_JS` |
| 图标尺寸 | 14px | 12px | 16px |
| 颜色 | `inherit` | `--color-diff-blob-addition-num-text` | 硬编码 `#6e7681` / 深色 `#8b949e` |
| 常态透明度 | `opacity:.55` | 无（全不透明） | 容器 `opacity:.45` |
| hover 反馈 | `opacity:1` | **完全没有** | 容器 `opacity:1` + 背景 |
| padding | `0` | `0 2px` | `2px 6px` |

另有一处独立缺陷：标题折叠的 chevron 用 `vertical-align:middle`——该值对齐的是 **x-height 中线**而非字高中心，定尺图标在各级标题下视觉偏低约 `0.1em`。

## 决策

1. **统一交互与配色**：三族共用——常态 `opacity:.6` + `color:var(--fgColor-muted, var(--color-fg-muted))`；hover `opacity:1` + `background:var(--bgColor-muted, var(--color-canvas-subtle))`；`border-radius:4px`；`transition:opacity .2s, background .2s`；`padding:2px 4px`。
2. **图标尺寸保留差异**：12px（目录侧栏）/ 14px（标题行内）/ 16px（代码块工具栏），分别适配三种信息密度。
3. **去掉容器级透明度**：`.code-block-controls` 的 `opacity:.45` 移除，改由按钮自身承担——否则会与按钮级 `.6` 叠加成 `.27`。触屏（`hover:none`）下按钮设 `opacity:1` 常显。
4. **配色全部走主题变量**：移除 `#6e7681` / `#8b949e` 两级硬编码灰，连带复制成功态改用 `--color-success-fg`、开关关闭态改用 `--color-primer-fg-disabled`；相应 `[data-color-mode="dark"]` 覆盖随之删除。
5. **修正标题 chevron 的垂直对齐**：改用 `vertical-align: calc(0.35em - 9px)`——以半字高减去半盒高，把盒底定位到基线，使图标中心落在字高中心；该式随标题字号线性生效，h1–h6 通用。

   - 不做什么：不改三族的交互行为与事件绑定（折叠/展开逻辑、事件委托均不动）。

## 后果

- **收益：** 三族控件观感与交互一致；配色无硬编码色，深色模式无需逐处覆盖；目录 +/− 与标题 chevron 补齐 hover 反馈；键盘焦点环恢复（移除 `outline:none`）。
- **代价 / 权衡：** 代码块工具栏由「容器整体淡入」改为「逐按钮淡入」，静止时更可见（`.45`→`.6`）；`.code-toggle.off` 的浅色值由 `#c6cbd1` 变为 `--color-primer-fg-disabled`（`#8c959f`），关闭态比原先更显眼。
- **未解决风险：** `vertical-align: calc(0.35em - 9px)` 假设 cap-height ≈ 0.7em，更换字体族后需目视复核。

## 实施位置

- `assets/sections.js`（`.section-toggle`）、`assets/toc.js`（`.toc-toggle`）、`md2html.py`（`EXTRA_JS` 的控件样式、`.code-lang` 与行号色）

## 验证

- `pytest` 157 passed（新增 `TestIconButtonUnification` 4 例：三族无硬编码灰、共用同一组取值、hover 规则齐备、工具栏无容器级透明度）。
- `node --check` 校验 `toc.js` / `sections.js` 通过。

## 关联文档

- [ADR-0005](ADR-0005-code-block-line-numbers.md)：本 ADR 取代其决策 3 的代码块控件配色。
- [ADR-0009](ADR-0009-toc-children-toggle.md)：本 ADR 统一其 `.toc-toggle` 的交互与配色。
- [ADR-0010](ADR-0010-heading-fold-expand.md)：本 ADR 统一其 `.section-toggle` 的交互、配色与垂直对齐。

## 下一步

无需后续动作。
