# ADR-0014: 图标单一数据源与统一渲染

- **状态**: 已接受
- **日期**: 2026-10-08
- **相关**: `icons.py`、`Gmeek.py#renderHtml`、`templates/macro.html`、`templates/base.html#renderIcon`、`md2html.py`、`assets/toc.js`、`assets/sections.js`
- **修订**: 2026-10-08 — 统一由填充式改为 **24×24 线性描边(Lucide 风)**，见文末「修订」小节。

## 背景

站点图标此前散落在五处，风格与来源不一致，维护与扩展成本高：

| 来源 | 位置 | 问题 |
|------|------|------|
| `IconList` 字典 | `Gmeek.py` | 仅含导航图标，与控件图标分家 |
| 模板内联 `<svg>` | `post/plist/search/tag.html` | 包装器写法不一：有的带 `viewBox`、有的 20×20、有的缺 class |
| 代码块控件 | `md2html.py` | 硬编码，`viewBox 20×20`，`fill="green"`/`#555` |
| TOC +/− | `assets/toc.js` | 内联、`stroke` 描边式 |
| 标题 chevron | `assets/sections.js` | 内联、`fill` 填充式 |

同一份路径数据在多处重复，任一处调整都需同步，极易漂移。

## 决策

1. **单一数据源 `icons.py`**：`ICONS`（name → 图标内部标记）+ `VIEWBOX`（统一 `0 0 24 24`）+ `STROKE_WIDTH`（`1.5`）+ `viewbox()` / `render()`。约定所有图标为 **24×24 线性描边**（`fill="none" stroke="currentColor" stroke-width="1.5"`，圆角端点，Lucide/Feather 风）。
2. **三方复用同一份定义**：
   - `Gmeek.py` 以 `from icons import ICONS as IconList, VIEWBOX as IconViewBox, STROKE_WIDTH as IconStrokeWidth` 注入模板，并由 `base.html` 暴露为前端全局 `IconList` / `IconViewBox` / `IconStrokeWidth` / `renderIcon()`；
   - `md2html.py` 经 `icons.render()` 生成代码块控件图标（复制/成功图标以 `__ICON_*__` 占位符在 `convert()` 中回填）；
   - `assets/toc.js`、`assets/sections.js` 经前端 `renderIcon()` 复用，删除内联 SVG。
3. **模板统一宏 `templates/macro.html`**：`icon(name, size, cls, id, svg_class)` 输出一致的 `<svg class="octicon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden>…</svg>`。四个模板 `{% import 'macro.html' as icons with context %}` 后统一调用；服务端可静态填充的图标一律服务端填充（顺带删除 `search/tag/plist` 中冗余的 `setAttribute` JS）。
4. **风格统一**：TOC 的 +/−、标题 chevron、复制/成功、travel 等全部改为同一 24×24 线性描边风格（此前混杂 16/20/24 画布与描边/填充两种形态）。

## 验证

- `pytest` 128 passed（`TestIconRegistry` 6 例、`TestIconTemplates` 4 例，均已按线性描边风格更新断言）。
- 四模板渲染无残留 `{{`/`{%`，图标服务端填充；全部图标命中 24 画布且带 `stroke-width="1.5"`；`md2html` 无占位符残留、旧 20×20 复制图标已移除。
- `toc.js`/`sections.js`/`nav.js` 及代码块内联脚本经 `node --check` 校验通过；模板渲染出的 `base.html` 内联脚本亦通过 `node --check`。

## 修订：统一切换为线性描边风格（`RENDER_VERSION` 5）

初版（填充式 16×16 octicon）上线后发现两点不足：一是与站点「简洁现代」气质不符，二是 `subway` 等少数图标画布/形态与其余不一致。

- **画布与描边**：`icons.py` 中 `ICONS` 的值由「path 的 `d`」改为「图标内部标记」（可含 `path`/`circle`/`rect`），统一 `VIEWBOX="0 0 24 24"`、`STROKE_WIDTH="1.5"`；`render()` 改为包裹 `fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"`。
- **`rss` 圆点**：描边下 `r=1` 的圆会呈细环，故该 `circle` 显式 `fill="currentColor" stroke="none"` 保留实心点。
- **CSS 覆盖（关键）**：Primer 有 `.octicon{…fill:currentColor}`，会覆盖 `fill="none"` 使描边图标被填实。`base.html` 增补 `svg.octicon{fill:none;stroke:currentColor}`（特异性 0-1-1 > 0-1-0，且 `<style>` 在 `<link>` 之后）以保证描边生效。
- **主题切换重构**：`themeSwitch` 的 `id` 由 `<path>` 移到 `<svg>`，切换逻辑由 `setAttribute("d", …)` 改为 `svg.innerHTML = IconList["moon"/"sun"]`；配色改设在 `<svg>` 自身（原设在 `parentNode`，现父节点为 `.btn`，且 `.btn .octicon{color:…}` 会截断继承，直接设 svg 更稳妥）。
- **宏签名变更**：`icon(name, size, cls, id, svg_class)`，删除 `d`（占位）与 `path_cls`（改由 `svg_class` 追加到 svg 的 class，用于列表项 `svgTop0/1`）。
- `RENDER_VERSION` 递增至 **5**，触发全站帖子 HTML 重转。

## 代价与权衡

- 模板新增一层宏间接，调试时需理解 `macro.html`；换来的是单点定义、风格一致。
- `IconList` 前端全局额外携带控件图标（数百字节），可接受。
- Jinja 注释不可嵌套：`macro.html` 头部注释内不得再书写 `{# #}` 标记（本次曾因此导致宏提前闭合）。
