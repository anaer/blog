# ADR-0015：代码块行距 / 自动换行修复与移动端适配

**状态：** 已接受
**创建时间：** 2026-10-08
**最近更新：** 2026-10-08（行号槽宽统一为 2em、代码缩进 2.8em, 行号左移; 视口内的行号槽覆盖规则删除）

> **当前状态 / 核心结论：** 修复 ADR-0005 行号 / 换行方案的三处缺陷——`.cl` 之间的裸换行导致行距翻倍、`.cl` 继承 `pre>code` 的 `white-space:pre` 使自动换行失效、代码块内被塞入硬换行尾随空格；并补齐移动端 / 触屏样式。**后续 1**：行号槽加低饱和度底色 + 1px 分隔线, 深色主题 / `nolines` 各自适配; 槽宽经一轮「行号偏右」反馈统一为 2em（全视口单值, `padding-left` 2.8em）. **后续 2**：空 `<span class="cl"></span>` 无 in-flow content 会让 height:0, 空行坍缩与下一行挤在一起, 加 `min-height: 1.45em` 锁定到一行高度. 下一步无需后续动作。

---

## 背景

ADR-0005 落地「行 span + CSS 计数器」方案后，线上反馈三个问题：

1. **行间距过高**：`.cl` 之间用裸换行 `"\n"` 连接；`.cl` 是 `display:block`，但父级 `<pre>` 为 `white-space:pre`，该 `\n` 被当作真实换行渲染，于是每两行之间多出一条空行 → 视觉行距翻倍。
2. **自动换行失效**：`github-markdown-css` 的 `.markdown-body pre>code{white-space:pre}`（特异性 0-2-1）使 `.cl` 继承 `pre`；`white-space:pre` 下 `overflow-wrap` 不生效，故 `pre-wrap` 与「自动换行」开关均形同虚设。`post.html` 里 `pre{white-space:pre-wrap}`（0-0-1）也压不过它。
3. **移动端未适配**：块控件 `opacity:.45` 且依赖 `:hover`/`:focus-within` 显现；触屏无 hover → 控件既看不清也难点按；且控件绝对定位在 `top:6px;right:8px`，无语言标签时本就会压住代码首行。

另发现一处相关缺陷：`convert()` 为所有行统一追加两个尾随空格（Markdown 硬换行），**代码块内也照加**，导致复制的代码每行带两个空格、并影响换行断点。

## 决策

1. **行距**：`_wrap_code_lines` 改用 `"".join(lines)`。`.cl` 为 `display:block` 各自成行，无需分隔符；移除 `\n` 即消除空行。
2. **自动换行**：在 `.highlight .cl` 上**显式**声明 `white-space: pre-wrap`（元素自身属性优先于继承，不受 `pre>code` 特异性影响），配合 `overflow-wrap:anywhere` 断长 token；`word-break:normal`。开关关闭时 `.code-block-wrapper.nowrap .cl{white-space:pre}` 真正禁止换行。折叠态由 `nowrap` 改为 `pre`（`nowrap` 会吞掉缩进空格）。
3. **硬换行只作用于围栏外**：新增 `_add_hard_breaks()`，按围栏状态（``` / ~~~ 成对）跳过代码块内容，仅对块外行追加两个尾随空格。代码块内容保持原样，复制与换行不再被污染。
4. **移动端 / 触屏适配**：新增 `@media (hover: none), (max-width: 767px)`：
   - 控件常显（`opacity:1`），并为控件预留顶部空间（`.code-block-wrapper{padding-top:30px}`，同时下调 `pre` 顶部内边距），避免绝对定位按钮遮挡代码首行；
   - 加大点按区域（`padding:5px 8px`）、行号槽收窄（`padding-left:2.8em`），窄屏给代码更多宽度。
5. **渲染版本**：`RENDER_VERSION` 递增至 **6**，触发全站帖子 HTML 重转。

   - 不做什么：不改行号方案本身；不引入 JS 测量做响应式；不调整高亮配色。

6. **行号槽加底色与 1px 分隔线**（`md2html.py` 的 `EXTRA_JS`）：
   - **目的**：用户反馈行号与代码区底色完全一致, 视觉上挤在一起难以分辨, 给行号槽加低饱和度底色与列分隔线.
   - **做法**：在 `.highlight .cl` 上加 `background-image: linear-gradient(to right, <gutter> 0, <gutter> calc(W - 1px), <edge> calc(W - 1px), <edge> W, transparent W)`, 其中 W = 2em（全视口统一, 见下「触屏联动」的后续调整）; 1px 收尾分隔线用更深一档 rgba.
   - **主题**：`html[data-color-mode="dark"] .highlight .cl` 用同结构但深色 rgba 覆盖, 不引入新变量.
   - **`nolines` 联动**：行号关闭时 `.code-block-wrapper.nolines .cl { background-image: none; }`, 否则左侧会留一道与代码区不连贯的色块.
   - **触屏联动（后续调整）**：原为「桌面 2.4em / 触屏 2em」两套宽度。用户反馈行号整体偏右, 遂把桌面也收到 2em（`padding-left` 由 3.2em 同步降到 2.8em, 行号与代码之间保留 0.8em≈11px 的空档）, 槽宽贴合行号数字本身宽度; 视口内的行号槽覆盖规则因此冗余, 一并删除, 改为全视口单值.
   - **不做什么**：不在每条 `.cl` 单独用 div 包裹行号（会破坏 ADR-0005 的 CSS 计数器方案）；不动行号文本颜色（仍走 `var(--fgColor-muted, var(--color-fg-muted))`）；不引入 JS.

7. **空行保留视觉高度**（`md2html.py` 的 `.highlight .cl`）：
   - **问题**：用户反馈代码块空行「和下一行重叠了」. 根因是空 `<span class="cl"></span>` 无 in-flow content, `display:block` + `line-height:1.45` 在零内容下不产生 line box, 高度坍缩为 0; 同时行号 `::before` 也没空间挂载, 进一步加深「行号跳跃 / 空行消失」的错觉.
   - **做法**：在 `.highlight .cl` 上加 `min-height: 1.45em`(与 line-height 一致), 锁定到一行高度. min-height 是 floor 不是 ceiling, 非空行(单行/多行)不受影响.
   - **不动 Python 端**：`md2html._wrap_code_lines` 仍为每行(含空行)生成一个 `.cl` 标签, 行号与原顺序一致, 不跳号.
   - **CSS 注释规避**：注释里不再用 `<span class="cl">` 字面量, 避免被 `html.count('<span class="cl">')` 这类回归测试误计（之前一版注释踩到这个坑, 导致 `test_convert_produces_line_spans` 误报）.

## 后果

- **收益**：代码块行距恢复正常；「自动换行」开关真正可用（默认开启即软换行，关闭则横向滚动）；复制的代码干净无尾随空格；移动端控件可见、可点、不遮代码。
- **代价 / 权衡**：`.cl` 的 `white-space` 需同时维护 wrap/nowrap/folded 三态；移动端顶部预留 30px 空白（换取可点按与不遮挡）。
- **未解决风险**：缩进式代码块（4 空格缩进、无围栏）仍会命中 `_add_hard_breaks` 的「块外」分支而带上尾随空格——本仓库统一使用围栏，暂不处理。

## 实施位置

- 渲染逻辑：`md2html.py#Markdown2GithubHtml._wrap_code_lines`（连接符）、`md2html.py#Markdown2GithubHtml._add_hard_breaks`（新增）、`md2html.py#Markdown2GithubHtml.convert`
- 样式：`md2html.py` 的 `EXTRA_JS`（`.highlight .cl`、`nowrap`/`folded`、移动端媒体查询）
- 版本：`Gmeek.py#RENDER_VERSION`
- 测试：`tests/test_pipeline.py`（`TestWrapCodeLines` 断言更新，新增 `TestHardBreaks`、`TestCodeBlockResponsiveCss`）

## 验证

- `pytest` 136 passed（较此前 +8：无裸换行、硬换行围栏感知、代码无尾随空格、`pre-wrap`/`nowrap` 开关、触屏媒体查询）。
- 生成产物抽查：`.cl` 之间无 `\n`；代码行无 `  ` 尾随；含 `white-space: pre-wrap` 与 `@media (hover: none), (max-width: 767px)`。

## 关联文档

- [ADR-0005](ADR-0005-code-block-line-numbers.md)：本 ADR 修复其行号/换行方案的三个缺陷。
- [ADR-0011](ADR-0011-code-block-language-label.md)：语言标签与控件同处顶部条，移动端预留空间一并覆盖。

## 下一步

无需后续动作。
