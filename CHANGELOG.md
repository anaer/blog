# CHANGELOG

## 26.1009.1640

1. 新增中文短词子串检索(轻量双轨): 实测 Pagefind 对 2 字短词不稳(29 篇真实文章: 标题内两字词约 31.5% 搜不到目标文章, 完整标题/小节标题/多字词 0% 漏检), 故只对「标题 + 小节标题」建一条连续子串索引补齐该档, 不做正文轨
2. 新增 `scripts/build_search_index.py`(仅标准库): 扫描站点 HTML 中带 `data-pagefind-body` 的页面, 抽取 `<title>` 与正文容器内 `h1–h6` 文本, 写 `search-index/index.json`(实测 29 篇 3.3KB, 163 篇约 19KB)
3. CI: 在 `Build search index`(pagefind)之前新增 `Build substring search index` 步骤, 同样跑在合并后的完整站点上(增量构建产物不完整); 脚本从 `/opt/Gmeek` 取, 用系统 `python3` 直跑, 不依赖 uv 环境
4. 检索页: 懒加载子串索引(首次查询时 fetch, 失败静默降级); 经 PagefindUI 的 `processTerm` 回调触发匹配(无需额外监听输入事件); 命中结果以独立容器 `#exactMatches` 插到 `.pagefind-ui__drawer` 内、`.pagefind-ui__results-area` 之前(输入框之下、Pagefind 结果之上), 两轨并列展示; 词长 < 2 不触发, 命中封顶 10 条
5. 不隐藏/不过滤 Pagefind 结果(上游踩过「过滤逻辑藏光结果 + 注入被重绘清掉」两个坑); 类名刻意不沿用 `.pagefind-ui__result`, 避免被结果装饰器当成 Pagefind 卡片二次加工
6. 测试: 新增 `TestSearchIndexBuilder`(6 例: 标题/小节抽取、正文外小节忽略、无 body 页跳过、空小节、空白折叠、排序与输出目录跳过)与 `TestExactMatchSearch`(6 例: 容器独立声明、`processTerm` 挂接、URL 经 homeUrl 派生、注入目标、词长守卫、不隐藏 Pagefind 结果), 共 12 例; 全量 `237 passed`
7. 端到端: 渲染真实 search.html + 真实索引, headless Chrome 验证「输入框 > 精确匹配 > Pagefind 结果」位置正确, 且「入参」这类 Pagefind 漏检的两字词被精确匹配块正确补上(Pagefind 返回的 2 条不含目标文章)
8. 文档: 新建 `ADR-0027-chinese-substring-search-index.md`; ADR-0007「未解决风险」按实测数据改写并标注已由 ADR-0027 补齐; `glossary.md` 新增「子串检索索引」; `docs/pagefind-integration.md` §6 现状改写为已实现轻量轨

## 26.1009.1610

1. 修复检索加载 spinner 误伤终态: Pagefind UI 1.5.2 用同一个 `.pagefind-ui__message` 承载 loading / 零结果 / 结果计数三种消息, 原实现给该元素无差别加旋转 `::before`, 导致「N results for …」「No results for …」这类终态也挂着永不停止的加载指示器; 改用 `#search .pagefind-ui__message:not(:has(+ .pagefind-ui__results))::before` 只作用于 loading 态(计数/零结果消息后恒接 `<ol class="pagefind-ui__results">`, loading 消息不接)
2. 修复假阳性回归用例 `test_process_result_uses_single_abs_url_key`: 原正则 `\{(.*?)\}` 非贪婪, 捕获止于 `result.meta || {}` 的首个 `}`, 真正的赋值行不在范围内, 断言仅因**注释文本**含 `absUrl(result.url)` 而通过(反证: 还原 `urlKeys` 旧实现后该用例仍通过); 改为锚定 `return result;` 并先去注释再断言
3. 测试加固: `test_lookup_no_longer_falls_back_to_pathname` 的 `new URL(` 断言为空转(真实回归路径经 `urlKeys`, 不会把 `new URL(` 引入 lookup 体), 改为断言 `urlKeys` 不存在; `test_mutation_observer_uses_raf_throttle` 的正则允许 `.observe(` 前空白以兼容多行形态, pending-flag 断言收敛到回调体内; `test_loading_state_styled` 补 spinner 作用域断言
4. 四条修复均经反证(还原修复前形态 -> 用例必须失败且失败原因与预期一致 -> 恢复后通过); 全量 `225 passed`; CSS 花括号平衡、内联 JS `node --check` 5/5 通过
5. 文档: ADR-0026 决策 6 按代码事实改写(原文引用了不存在的 `.pagebusf__search-input--loading` 类名与 `::after`, 与实现不符), 「未解决风险」「验证」同步更新, 「下一步」改为「无需后续动作」

## 26.1009.1530

1. 检索页加载链去阻塞: `pagefind-ui.js` 改 `defer` + head 内加 `<link rel="preload" as="script">` 提前声明, 让浏览器在解析 head 时就开始拉包, 与 HTML 解析并行
2. 首页 idle 预拉 `pagefind-ui.js`: `base.html` 在 `window load` 后用 `requestIdleCallback` 插入 `<link rel="prefetch" as="script">`, 对「首页/列表/文章页 → 检索页」路径省下 ~250KB 冷下载; `requestIdleCallback` 不存在时降级 `setTimeout`, 不阻塞首屏渲染
3. `PagefindUI` 配置: `pageSize` 上调到 20(分页"Load more"触发频次按 200 篇经验值从 ~30% 降到 ~10%)、`showSubResults` 显式 `true`(保留段落级相关性高亮)、新增 `debounceTimeoutMs: 250`(略紧于 Pagefind 默认 300, 减少连续键入时的冗余查询)
4. `processResult` 取消 URL 双键冗余: 历史上为"防御 `result.url` 与 DOM `href` 编码/前缀差异"曾同时按 abs URL 与 pathname 索引, 当前部署下两者派生同一字符串, 直接按 abs URL 查即可; `lookup` 函数相应简化, 体内不再调用 `new URL().pathname`
5. `MutationObserver` 加 `requestAnimationFrame` 节流: Pagefind 渲染结果时插入多个 DOM 节点, 同帧内多次触发合并为一次 `decorate`; `decorate` 自身已有 `data-gmDecorated` 幂等标记, 节流不改变结果, 仅减少反复 `querySelectorAll` 扫描
6. UX 加载提示: Pagefind UI 1.5.2 在查询中插入 `<p class="pagefind-ui__message">`(默认 "Searching [SEARCH_TERM]..."), 给该元素加主题色 + 旋转 `::before` spinner, 让等待状态更明显; 不依赖 Pagefind 内部 loading 修饰类(避免升级版本时类名漂移)
7. 测试: 新增 `TestSearchPerformance`(9 例: defer、preload、pageSize=20、showSubResults=true、debounce=250ms、processResult 单键、lookup 不走 pathname、raf 节流、`pagefind-ui__message` 样式)与 `TestIdlePrefetch`(2 例: `requestIdleCallback`+`window.load` 监听、动态创建的 `prefetch` 链属性赋值), 共 11 例; 全量 `225 passed in 3.03s`
8. 文档: 新建 `ADR-0026-pagefind-search-performance.md`(90 行); `glossary.md` 新增「Pagefind UI 预拉(idle prefetch)」「Pagefind 装饰器(decorate)」两条; ADR-0007/0021/0018 增加反向链接; ADR 编号未进入代码/测试/模板(由 `TestAdrBoundary` 守护)

## 26.1008.2130

1. 「相关文章」区块改为透明无框: 容器由 `class="SideNav related-posts border"` 收敛为 `class="related-posts"`(撤掉的这两个类正是底色 `canvas-subtle` 与 1px 边框的来源), `.related-posts` 显式 `background:none;border:0`, 去掉 `border-radius`
2. 保留与列表页同源的行样式: 条目仍用 `SideNav-item`(hover 反馈 + `renderIcon('post')` 图标), 但撤销其容器化痕迹——`padding-left/right:0` 让条目与正文左边缘对齐(实测 `itemX == #postBody X == 8px`)、`background:none`、`border-top:0`(条目间不要横线)、`:last-child{box-shadow:none}`(否则末行下方多出一道横线); 行间距只由内边距承担; 小标题内边距随之改为 `12px 0 4px`
3. 窄屏规则同步为 `padding:10px 0`, 不再保留左右留白
4. 测试: 两处类名断言随迁, 新增 `TestRelatedArticlesContract::test_related_block_has_no_box`(钉死容器透明无框无圆角、条目无底色/无左右内边距/无行间横线、末行无阴影, 并负向控制 `SideNav`/`border` 类不得回到容器上); 共 213 passed; 计算样式经浏览器实测复核(含上一轮图标 `fill:none` 未回退)
5. 文档: ADR-0022 决策 4 重写为「沿用行样式, 不套外壳」并记修订原因

## 26.1008.2100

1. 修复代码块控件图标「显示不全」: 根因是 CSS 特异性——`base.html` 的 `svg.octicon{fill:none}`(0,1,1) 压不过 github-markdown-css 的 `.markdown-body .octicon{fill:currentcolor}`(0,2,0), 正文容器内的描边图标被 `currentColor` 整体填实(copy 变成实心方块、fold/wrap 变成色块); 改为 `.markdown-body svg.octicon,svg.octicon{fill:none;stroke:currentColor}`, 前一项(0,2,1)压过正文规则, 后一项继续覆盖正文外(头部按钮、tag 列表)
2. 定位手法: 用当前代码渲染 `templates/post.html` 生成对照页, 浏览器里读 computed style 得 `fill: rgb(87,96,106)`(应为 `none`), 再遍历 `document.styleSheets` 列出所有命中该元素且声明 fill 的规则, 才找到藏在 github-markdown.min.css 里的那条(此前 ADR 只记录了 Primer 的那条)
3. 顺带排除两处误判: 单行代码块的折叠按钮 0×0 是预期行为(单行无需折叠, 脚本主动 `display:none`); 线上页面图标仍是旧样式(16 画布、无 `octicon` 类)属未重渲染的旧构建产物, 非本次缺陷
4. 新增 4 条回归 `TestIconFillOverride`: 断言 vendor 规则确实带 `.markdown-body` 前缀、我们的覆盖特异性严格大于 vendor 全部 `fill:currentcolor` 规则、正文外场景仍在选择器列表内; 负向控制钉死「单用 `svg.octicon` 会输」; 共 205 passed
5. 文档: ADR-0014 决策 4 补「修正」段(原记录只对比了 Primer 的 0-1-0, 漏了 markdown-css 的 0-2-0)

## 26.1008.2030

1. 代码块行号左移: 行号槽宽由「桌面 2.4em / 触屏 2em」两套统一为 2em(贴合行号数字自身宽度), 代码缩进 `padding-left` 由 3.2em 降到 2.8em, 行号与代码之间保留 0.8em(≈11px)空档; 深浅两主题的分隔线渐变终点同步改为 2em
2. 冗余清理: 窄屏 `@media (hover: none), (max-width: 767px)` 内针对 `.highlight .cl` 的 padding/底色/`::before` 宽覆盖整套删除(基线已等于原窄屏值), 移动端不再需要第二套行号槽宽度
3. `RENDER_VERSION` 13 → 14: 这段 CSS 内联在 `md2html` 转换后的正文 HTML 里并随 `backup/` 缓存, 不升版本则旧文章页的行号槽会冻结在上一版取值
4. 实测几何(浏览器 computed style): `padding-left` 43.52px → 38.08px、`::before` 宽 32.64px → 27.19px, 即行号右缘左移约 5.4px; 数值经计算样式核对, 截图通道不可用未做视觉比对
5. 测试: `test_gutter_background_light_theme` 改钉 2em; `test_gutter_background_narrowed_on_touch` 重写为 `test_gutter_single_width_across_viewports`, 钉死基线 2.8em/2em、明暗主题同宽, 并把 2.4em / 3.2em 作为负向控制禁止复现; 共 201 passed
6. 文档: ADR-0015 决策 6 与状态摘要同步

## 26.1008.2000

1. 文章页底部由「上一页/下一页」改为「按标签关联文章」: `nav.json` 每条新增 `labels` 字段, `assets/nav.js` 在运行时按「与当前文章共享的标签数」降序取最多 5 条并渲染, 同分沿用 `nav.json` 的列表序(稳定排序, 无需下发时间戳)
2. 静态相邻链接彻底移除(纯运行时方案): `createPostHtml` 不再写 prev/next, 只输出 `data-nav-url`/`data-post-number`/`data-labels`/`data-heading` 四个钩子; `data-labels` 用 `|tojson` 做 HTML 安全转义, 标签名含引号/尖括号也能被 `JSON.parse` 还原
3. 增量构建成本归零: 删除 `nav_neighbors`、`neighbor_keys`、`GMEEK.get_nav_keys`、`GMEEK._nav_keys`, `runOne` 不再连带重渲染相邻文章(每篇变更少渲染 1~2 个页面); `nav.json` 每次构建全量重写, 故新增文章/改标签不必回刷旧文章页
4. 空结果一律收起: 当前文章无标签、无共享标签候选、数据拉取失败或格式异常都由脚本 `box.remove()` 移除整块, 不留空壳; 旧模板残留页面(未全量重建)找不到容器同样静默返回
5. 视觉沿用列表页语言: 容器复用 Primer `SideNav` + `border`, 条目用 `SideNav-item` + `renderIcon('post')`, 标题单行省略; 撤掉 `.paginate-container` 的两端对齐与 `:not(:has(a))` 收起规则
6. 新增文案 `i18n['relatedPosts']`(相关文章 / Related posts), 标题走 `data-heading` 注入, 不在 JS 里硬编码
7. 测试: 删除 `TestNavNeighbors`/`TestNeighborKeys`/`TestRunOneRefreshesNeighbors`, 新增 `TestRelatedOrder`、`TestRunOneRendersOnlyChangedPost`(负向控制: 只渲染变更那一篇)、`TestCreatePostHtmlRelated`(负向控制: prev/next 字段不得出现在文章页数据)、`TestCreateNavJson` 补 labels 导出与缺失兜底、`TestTemplateSmoke` 补关联钩子/转义/无分页残留、`TestRelatedArticlesContract`(模板与 JS 的属性名与类名契约); Node + DOM 桩逐条验证 `nav.js` 行为(11 项全过); 共 201 passed
8. 文档: 新增 ADR-0022, ADR-0006 标记为已被取代, ADR-0002 实施位置指针与 glossary 同步
9. 待办: 部署后需触发一次全量构建(`workflow_dispatch`), 让所有文章页拿到新模板; 无 JS 环境与搜索引擎爬虫不再能看到关联链接, Pagefind 也不索引运行时注入的这些链接(选 B 方案的已知代价)

## 26.1008.1900

1. 深色主题调色板由 GitHub 冷蓝深改为 WorkBuddy AI 客户端的暖灰中性方向: `.markdown-body` 暗色 token 中 canvas-default 从 `#0d1117` 升到 `#1a1c20`、canvas-subtle 升到 `#22262c`、border 升到 `#383d45 / #2b2f37`、fg-default 升到 `#dde2e8`、accent-fg 降到 `#7ab8ff`、accent-emphasis 降到 `#5a8fe6`、neutral-muted 改为 `rgba(180,188,200,0.16)`、danger-fg 升到 `#ff7a73`
2. 代码块行号槽底色同步改为中性白色微染(`rgba(255,255,255,0.045)` 槽 + `rgba(255,255,255,0.10)` 分隔), 取代之前的蓝灰色 `rgba(110,118,129,…)`, 暗色下不再带冷色感
3. 标签暗色饱和度从 45% 降到 30%, 底色从 22% 降到 18%, 文字从 85% 降到 78%, 与 WorkBuddy 暖灰底更融合
4. 悬浮按钮配色改主题驱动: `#007bff / #0056b3` 改为 `var(--color-accent-fg) / var(--color-accent-emphasis)`, 暗色下加 1px 柔光描边 `rgba(255,255,255,0.12)` 模拟按钮浮起
5. 新增 2 条回归测试 `test_dark_tokens_use_warm_neutral_palette` + `test_floating_button_uses_theme_var`, 守护 8 个新 token 取值 + 8 个旧冷蓝 token 抑制 + 硬编码按钮色撤掉
6. 配套更新 ADR-0017(decision 4): 记录 WorkBuddy 调色板方向、vendored 与模板拆分策略、未解决问题(primer-subset.css 仍是 GitHub 风格)
7. 预览: 同一段文章内容 OLD(冷蓝) vs NEW(暖灰) 并排对照见 `C:\Users\Administrator\AppData\Local\Temp\dark_theme_preview.html`

## 26.1008.1830

1. 修复代码块空行坍缩: `.highlight .cl` 加 `min-height: 1.45em`(与 line-height 对齐), 空 `<span class="cl"></span>` 无 in-flow content 时也保留一行高度, 不再与下一行挤在一起
2. 副作用防御: 同时保证空行的行号::before 有空间渲染(原来 height:0 时::before 也会被挤掉)
3. 新增 `TestWrapCodeLines::test_blank_line_keeps_visible_height` 与 `test_blank_line_emits_empty_cl`: 前者钉死 `min-height: 1.45em`, 后者钉死 `_wrap_code_lines` 必须为空行也产生一个 `.cl` 标签(行号不跳号)
4. CSS 注释规避: 不在注释里写 `<span class="cl">` 字面量, 否则会被 `html.count('<span class="cl">')` 误计(回归: 之前一版注释踩到这个坑)

## 26.1008.1800

1. 代码块行号槽加底色: `.highlight .cl` 用 `linear-gradient` 把左 2.4em 染成低饱和度底色, 收尾 1px 分隔线; 与代码区做视觉区分, 避免行号与代码挤在一起难以分辨
2. 主题适配: 浅主题用 `rgba(175,184,193,0.28)` 槽 + `rgba(175,184,193,0.55)` 分隔; 深主题用 `rgba(110,118,129,0.22)` 槽 + `rgba(110,118,129,0.45)` 分隔, 由 `html[data-color-mode="dark"]` 覆盖
3. 行号关闭(`nolines`)时一并撤掉底色: 否则左侧会留一道与代码区不连贯的色块
4. 触屏(窄屏)同步收窄: 槽位与分隔线都从 2.4em 收窄到 2em, 避免底色超出实际行号宽度
5. 新增 4 条回归测试 `TestCodeBlockResponsiveCss`: 浅/深主题底色规则、`nolines` 撤底色、触屏收窄

## 26.1008.1730

1. 目录 +/− 切换按钮由左侧改为右侧（`right: 2px` 绝对定位），左侧不再预留槽位，链接缩进只由 `(level-1) * 10` 决定，视觉重心回到标题本身
2. 槽位（`TOGGLE_SLOT` = 22px）从 `paddingLeft` 改为 `paddingRight`，防止长标题与右侧按钮重叠
3. 新增测试 `test_toggle_anchored_to_right`：钉死 `.toc-toggle` 用 `right: 2px` 定位，旧 `left: -2px` 不得再出现
4. 重写 `test_toggle_slot_reserved_for_all_items`：钉死槽位**右侧**预留（`paddingRight` 含 `TOGGLE_SLOT` 且不得依赖 `children.length`），左侧 `paddingLeft` 不含 `TOGGLE_SLOT`
5. 同步 ADR-0009 决策 1：+/− 改为右对齐放置，槽位原则（无条件预留、不依赖 `children.length`）保留

## 26.1008.1700

1. 检索结果里的标签同时高亮 + 可点击跳到 tag.html: 渲染为 `<a class="Label" style="--label-hue:N" href="<homeUrl>/tag.html#<encoded>">`, 视觉与 post.html / plist.html / tag.html 的标签同源(都走 base.html 的 .Label 类), 点击后 tag.html 的 setClassDisplay(decodeURIComponent(...)) 自动定位并高亮对应标签
2. 色相字典注入: search.html 把 `{{ blogBase['labelHueDict']|tojson }}` 注入 JS 端为 `var labelHues`, 构造 `<a>` 时按名查表, 缺失回退默认 210(与 .Label 默认一致)
3. URL 编码: 标签名经 `encodeURIComponent` 写入 href, 中英 / ASCII / 含 `?` 等特殊字符的标签名都能正确还原
4. 新增 `TestSearchResultLabelLink` 6 条回归测试: 色相字典注入 / 空字典兜底 / 装饰器创建 `<a class="Label">` / `.Label` 类复用 / URL 编码结构 / 元信息整块仍挂标题行内
5. 同步更新 ADR-0021 决策 5 与验证清单(新增端到端标签 href / --label-hue / .Label 类的 Node 桩断言)

## 26.1008.1605

1. 加 state 迁移步骤 `migrate_state`: 构建入口(默认 defaultConfig)就地补全老 blogBase.json 里的派生字段 dateLabelHue / createdDate, 由 baseline 字段确定性重算, 一次构建后落盘, 后续消费者(plist/tag_data/...)统一走真值路径
2. plist.html 第 82 行日期标签加深度防御 `.get('dateLabelHue', 210) / .get('createdDate', '')`: 即使迁移步骤被绕过, 也不再有 Jinja Undefined 渲染成空 style / 空 innerHTML
3. 新增 `TestMigrateState` 5 条回归测试, 钉死就地补全 / 幂等(已有值不被覆盖) / 不触碰其它字段 / 缺失列表键或 None 健壮性 / 与 addOnePostJson 派生值一致

## 26.1008.1540

1. tag_data 字段缺失兜底: 旧状态文件(blogBase.json)的帖子在本特性加入前已存, 缺少 dateLabelHue 等; 之前 KeyError 让整页构建崩溃; 改为每个字段按 defaults 兜底(色相 210 / 串空 / 列表空), 老数据与新数据可混存, 单条缺失不中断整页
2. 同步回归测试 `TestTagData::test_missing_fields_fall_back_to_defaults` 等三条, 钉死兜底值与键集合

## 26.1008.1520

1. post.html 调整删除线样式: `.markdown-body del` 字色与划线色都改走主题变量 `--color-fg-muted` / `--color-fg-subtle`, 旧文本自然退到背景层, 不再与当前文本抢视觉权重(明暗自适应)
2. 同步回归测试 `test_post_del_uses_muted_tokens_for_text_and_line` 与 `test_post_theme_tokens_cover_del_dependencies`, 钉死主题 token 完备与不引入硬编码颜色

## 26.1008.1511

1. 修复 CI 启动崩溃: `GMEEK.__init__` 之前在 `defaultConfig()` 之后才赋值 `self.labelHueDict`, 但 `defaultConfig` 已先读取, 故真实实例化会 AttributeError; 改为先以空 dict 占位, defaultConfig 之后按 GitHub 标签重算覆盖(见 ADR-0020 修订)
2. 修复模板拿到空色相字典: 上一步加了占位后, `defaultConfig` 把空 dict 写进了 `blogBase["labelHueDict"]`, __init__ 末尾重算结束必须再回写到 blogBase, 否则 plist/post/tag 模板消费到的仍是占位空 dict, 标签全回退默认色相 210(见 ADR-0020 修订)
3. 新增回归测试: `TestLabelHueTheme::test_init_initialises_labelHueDict_before_defaultConfig`(行序)与 `test_init_resyncs_blogBase_labelHueDict_after_recompute`(回写), 钉死两层 invariant

## 26.1008.1450

1. 检索结果的标签与 issue 入口由「页脚」改为「标题行内」: 补挂到 `.pagefind-ui__result-title` 子节点末尾, 与标题链接同排, 标题行用 flex 布局, 空间不足时整体换行(见 ADR-0021 修订)

## 26.1008.1441

1. 检索结果改版: 展示文章标签并增加 issue 链接图标
2. 修复目录同级不对齐: +/− 槽位改为对所有目录项无条件预留
3. 修复文章页上一篇/下一篇与列表顺序不一致的问题: 三处排序(列表页/导航/全量预排)合并为同一序列
4. 标签配色增加配置开关: 可在「按标签名派生色相」与「取 GitHub 标签色的色相」之间切换
5. 标签配色改为按标签名派生色相, 不再依赖 GitHub 的标签色, 底色与字色随明暗主题自适应
6. 修复正文标题折叠按钮样式从未生效的问题: 选择器与按钮实际插入位置不匹配, 按钮一直按浏览器原生样式渲染
7. 统一正文标题折叠 / 目录 +− / 代码块控件三族图标按钮的交互与配色, 配色改走主题变量
8. 统一列表页 / 标签页 / 文章页的搜索框样式: 抽为共享组件, 窄屏保留并收窄
9. 同步文档: 更新 ADR 正文、CONFIG.md 与 README 中已与实现不符的描述
10. 深色模式兼容: 修复正文与元信息等内容在深色下不可见的问题
11. 修复主题切换按钮无法切到深色的问题
12. 修复 search.html 搜索框样式: 尺寸改用 Pagefind 的 --pagefind-ui-scale 统一缩放(原单独覆盖 height 导致放大镜图标偏下、清除按钮溢出输入框); 新增几何居中回归测试(见 ADR-0007 修订)
13. 修复代码块行距翻倍(.cl 之间裸换行)与自动换行失效(.cl 继承 pre>code 的 white-space:pre); 硬换行只作用于围栏外, 代码不再被塞尾随空格; 补充移动端/触屏样式(控件常显、加大点按、顶部留白不遮代码)(见 ADR-0015, RENDER_VERSION 6)
14. 图标风格统一为 24x24 线性描边(简洁现代, Lucide 风): icons.py 的 ICONS 改为内部标记并统一 viewBox/stroke-width, 宏 macro.html、前端 renderIcon()、代码块控件同步; 新增 svg.octicon 覆盖 primer 的填充规则; 主题切换图标改由 innerHTML 回填(见 ADR-0014 修订, RENDER_VERSION 5)
15. 图标统一: 新增 icons.py 单一数据源, 模板经 macro.html 统一渲染, 代码块控件与前端 JS(toc/sections)复用同一套图标(见 ADR-0014)
16. 修复 runAll 分页迭代与命令行路由缺陷(手动触发误入 runOne(0)), 并增加 CI 发布安全闸门, 避免清空线上帖子(见 ADR-0013)

## 25.219.1731

1. 添加ai生成摘要

## 25.121.1035

1. post.html使用prevTitle判断, prevUrl可能存在等于disabled的情况
2. 保存markdown2html执行结果, 防止接口请求频繁导致请求失败
3. markdown2html添加重试, 请求异常时默认重试3次

## 25.117.956

1. 调整摘要生成逻辑 markdown->html->plaintext

## 25.108.1048

1. html链接使用issue.number, 简单点, 同时可以避免修改标题导致的链接变更问题以及计数问题
2. post标题采用issue.number+issue.title
3. 调整vercount实现方式, 加载时先使用localstorage中缓存的site数据, page数据使用接口返回

## 25.102.1647

1. 调整列表排序以及日期标签颜色
2. 列表页添加issues链接
