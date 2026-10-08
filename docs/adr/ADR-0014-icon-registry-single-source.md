# ADR-0014：图标单一数据源与统一渲染

**状态：** 已接受
**创建时间：** 2026-10-08

> **当前状态 / 核心结论：** 站点全部图标收敛到 `icons.py` 单一数据源，统一为 24×24 线性描边（`fill="none" stroke="currentColor" stroke-width="1.5"`，Lucide 风），由模板宏、代码块控件与前端 `renderIcon()` 三方复用。下一步无需后续动作。

---

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
   - `assets/toc.js`、`assets/sections.js` 经前端 `renderIcon()` 复用。
3. **模板统一宏 `templates/macro.html`**：`icon(name, size, cls, id, svg_class)` 输出一致的 `<svg class="octicon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden>…</svg>`。四个模板 `{% import 'macro.html' as icons with context %}` 后统一调用；服务端可静态填充的图标一律服务端填充（`svg_class` 追加到 svg 的 class，用于列表项 `svgTop0/1`）。
4. **描边落地的两处要点**：`rss` 的圆点在描边下会呈细环，该 `circle` 显式 `fill="currentColor" stroke="none"` 保留实心；Primer 的 `.octicon{…fill:currentColor}` 会覆盖 `fill="none"` 使描边被填实，故 `base.html` 以 `svg.octicon{fill:none;stroke:currentColor}`（特异性 0-1-1 > 0-1-0）覆盖。
5. **主题切换图标**：`themeSwitch` 的 `id` 在 `<svg>` 上，切换用 `svg.innerHTML = IconList["moon"/"sun"]`；配色设在 `<svg>` 自身——其父节点为 `.btn`，而 `.btn .octicon{color:…}` 会截断颜色继承。

## 后果

- **收益：** 图标单点定义、风格一致；`IconList` 前端全局额外携带控件图标（数百字节，可接受）。
- **代价 / 权衡：** 模板多一层宏间接，调试需理解 `macro.html`。
- **未解决风险：** Jinja 注释不可嵌套——`macro.html` 头部注释内不得再写 `{# #}` 标记，否则宏提前闭合。

## 实施位置

- 数据源：`icons.py#ICONS`、`icons.py#VIEWBOX`、`icons.py#STROKE_WIDTH`、`icons.py#render`
- 模板：`templates/macro.html`、`templates/base.html#renderIcon`、`templates/base.html`（`svg.octicon` 覆盖）
- 复用方：`Gmeek.py#renderHtml`、`md2html.py#Markdown2GithubHtml._add_controls`、`assets/toc.js`、`assets/sections.js`

## 验证

- `pytest` 128 passed（`TestIconRegistry` 6 例、`TestIconTemplates` 4 例，均已按线性描边风格更新断言）。
- 四模板渲染无残留 `{{`/`{%`，图标服务端填充；全部图标命中 24 画布且带 `stroke-width="1.5"`；`md2html` 无占位符残留、旧 20×20 复制图标已移除。
- `toc.js`/`sections.js`/`nav.js` 及代码块内联脚本经 `node --check` 校验通过。

## 下一步

无需后续动作。
