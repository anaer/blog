# ADR-0014: 图标单一数据源与统一渲染

- **状态**: 已接受
- **日期**: 2026-10-08
- **相关**: `icons.py`、`Gmeek.py#renderHtml`、`templates/macro.html`、`templates/base.html#renderIcon`、`md2html.py`、`assets/toc.js`、`assets/sections.js`

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

1. **单一数据源 `icons.py`**：`ICONS`（name → 填充式 path d）+ `ICON_VIEWBOX`（画布覆盖，目前仅 subway 为 24×24）+ `viewbox()` / `render()`。约定所有图标为 16×16 填充式（`fill="currentColor"`，octicon 风格）。
2. **三方复用同一份定义**：
   - `Gmeek.py` 以 `from icons import ICONS as IconList` 注入模板，并由 `base.html` 暴露为前端全局 `IconList` / `IconViewBox` / `renderIcon()`；
   - `md2html.py` 经 `icons.render()` 生成代码块控件图标（复制/成功图标以 `__ICON_*__` 占位符在 `convert()` 中回填）；
   - `assets/toc.js`、`assets/sections.js` 经前端 `renderIcon()` 复用，删除内联 SVG。
3. **模板统一宏 `templates/macro.html`**：`icon(name, size, cls, id, d, path_cls)` 输出一致的 `<svg class="octicon" viewBox=… aria-hidden><path fill="currentColor" fill-rule="evenodd" …/></svg>`。四个模板 `{% import 'macro.html' as icons with context %}` 后统一调用；服务端可静态填充的图标一律服务端填充（顺带删除 `search/tag/plist` 中冗余的 `setAttribute` JS）。
4. **风格统一**：TOC 的 +/− 由描边式改为填充式；复制/成功图标由 20×20 灰/绿硬编码改为 16×16 的 octicon copy/check；travel 图标补 `viewBox="0 0 24 24"`（原缺失导致裁剪）。`RENDER_VERSION` 递增至 4 以触发全站帖子 HTML 重转。

## 验证

- `pytest` 126 passed（新增 `TestIconRegistry` 6 例、`TestIconTemplates` 4 例）。
- 四模板渲染无残留 `{{`/`{%`，图标服务端填充；`subway` 命中 24 画布；`md2html` 无占位符残留、旧 20×20 复制图标已移除。
- `toc.js`/`sections.js`/`nav.js` 及代码块内联脚本经 `node --check` 校验通过。

## 代价与权衡

- 模板新增一层宏间接，调试时需理解 `macro.html`；换来的是单点定义、风格一致。
- `IconList` 前端全局额外携带控件图标（数百字节），可接受。
- Jinja 注释不可嵌套：`macro.html` 头部注释内不得再书写 `{# #}` 标记（本次曾因此导致宏提前闭合）。
