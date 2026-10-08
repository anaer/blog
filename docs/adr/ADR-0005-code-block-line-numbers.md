# ADR-0005：代码块展示——行号、自动换行与高亮清理

**状态：** 已接受
**创建时间：** 2026-09-30

> **当前状态 / 核心结论：** 「行 span + CSS 计数器」行号方案、自动换行、折叠首行预览、starry-night 清理、`RENDER_VERSION` 均已落地；控件图标为内联 SVG（跟随主题色）、代码块行距 `line-height:1.45`、折叠态强制单行（`pre` + 横向滚动）。下一步无需后续动作。

---

## 背景

代码块当前无行号；折叠按钮为常显黑色 ▲、与灰色复制按钮观感不一（"突兀"主因之一）；每帖随机加载的 starry-night 样式实测零作用（只定义 `:root` 变量与 `.pl-*` 规则，pygments 产出为 `.k`/`.s` 等类，页面无 `.pl-*` 对象）；帖子 HTML 有构建缓存，渲染逻辑变更不会自动重转旧文（历史文章拿不到新行号）。

## 决策

1. **行号方案（行 span + CSS 计数器）**：`md2html` 生成期把每个逻辑行包成 `<span class="cl">`（跨行标签闭合/重开），行号由 CSS 计数器在左侧槽位生成；自动换行时续行不带号、文本对齐（编辑器软换行观感）；复制内容不含行号（CSS 生成）。不采用 pygments 表格列行号（代码换行后行号列错位）。
2. **自动换行**：`.highlight .cl` 显式声明 `white-space: pre-wrap`（`pre>code` 的 `white-space:pre` 会经继承压制换行，须在元素自身覆盖），配合 `overflow-wrap: anywhere` 保证长 token（URL 等）断行；开关关闭时以 `.code-block-wrapper.nowrap .cl{white-space:pre}` 真正禁止换行。
3. **块控件：低调化、首行预览与开关**：黑色 ▲ 改主题灰（浅色 #6e7681 / 深色 #8b949e），块控件默认半透明、悬停清晰；折叠行为改为**保留首行预览**（隐藏 `.cl ~ .cl`，不再整块隐藏），单行代码块隐藏折叠按钮；复制按钮改用 `textContent`，折叠态复制仍为全文；右上角新增「自动换行」「行号」两个开关（**默认开启**，关闭时分别以 `nowrap`/`nolines` 类纯 CSS 生效）。
4. **移除 starry-night 加载**：删除文章页的条件加载与生成器中的随机样式选择逻辑（实测零作用，省 2–6KB/页）；资产目录暂留，无引用后可再清理。
5. **渲染缓存版本标记**：新增 `RENDER_VERSION` 并纳入 HTML 缓存校验（`buildedAt` + 版本）；渲染逻辑变更时递增 → 下次全量构建全站自动重转（本次同时让图片懒加载在全站生效）。扩展 ADR-0001 决策 1 的缓存字段。
   - 不做什么：不改高亮配色（`highlight.css` 双主题保留）；不启用 pygments 表格行号。
6. **控件图标 SVG 化与折叠态单行**：块控件 `wrap-toggle`/`lines-toggle`/`fold-btn` 用内联 SVG（`stroke="currentColor"` 跟随按钮主题灰），不使用文本字符 ↵/#/▲/▼；折叠箭头经 CSS 旋转（`.folded` 时 `rotate(180deg)`）；`.highlight .cl` 设 `line-height:1.45` 收紧行距；折叠态 `.code-block-wrapper.folded` 内 `pre`/`.cl` 用 `white-space:pre` + 横向滚动，保证首行预览严格为一行（长首行不再换行撑高）；折叠点击监听用 `e.target.closest('.fold-btn')`（按钮含 SVG 后 `classList.contains` 不再可靠）。
   - 不做什么：不引入外部图标字体（bootstrap-icons/font-awesome）只为代码块控件；复制按钮的 SVG 双态（复制/已复制）保持不变。

## 后果

- **收益：** 代码块带行号且长行换行不错位；复制干净；控件观感统一；每帖少载 2–6KB 无效 CSS；渲染变更可全站自动生效（含历史文章）。
- **代价 / 权衡：** `md2html` 输出行结构变化、行号样式随页面内联（EXTRA_JS）；渲染器再变更时需记得递增 `RENDER_VERSION`。
- **未解决风险：** 多行 token（跨行 span）依赖闭合/重开算法，已用单测覆盖；上线后建议抽查一篇含长代码的旧文。

## 实施位置

- 行号与样式：`md2html.py#Markdown2GithubHtml._wrap_code_lines`、`md2html.py#Markdown2GithubHtml.convert`（EXTRA_JS 样式块）
- 模板：`templates/post.html`（移除 starry-night 条件加载）
- 生成器：`Gmeek.py#RENDER_VERSION`、`Gmeek.py#is_html_stale`、`Gmeek.py#carry_cache`、`Gmeek.py#GMEEK.createPostHtml`（移除 starryNight 逻辑）
- 测试：`tests/test_pipeline.py`

## 验证

- `pytest` 全绿（含跨行 span 闭合/重开、末尾空行不编号、老帖子无版本必须重转的负向控制）；本地渲染抽查行号/换行结构。

## 关联文档

- [ADR-0001](ADR-0001-generation-pipeline-correctness.md)：本 ADR 决策 5 扩展其决策 1 的缓存字段与校验。
- [ADR-0015](ADR-0015-code-block-line-height-wrap-mobile.md)：修复本 ADR 行号 / 自动换行方案的三处缺陷（行距翻倍、换行失效、移动端）。

## 下一步

无需后续动作（全部已落地，含 D6 三项精炼）。
