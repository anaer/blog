# Pagefind 站内检索集成文档

> 本仓库（Gmeek 静态博客）的 Pagefind 集成说明：**构建期生成索引 + 运行时纯前端检索**。
> 覆盖工作原理、本项目的接线方式、中文短词子串索引（轻量双轨）、已知限制与排错，供后续维护参照。

---

## 1. 为什么是 Pagefind

静态站点没有服务端，检索只能在「构建期预建索引 + 浏览器端查询」与「外挂检索服务」之间取舍。

| 方案 | 形态 | 中文短语 | 集成成本 | 运维 |
|------|------|----------|----------|------|
| **Pagefind（本项目采用）** | 构建期索引，纯前端 | 弱（分词切分，短词易漏） | 低 | 无（纯静态文件） |
| **Pagefind + 子串索引（本项目已采用，轻量版）** | 构建期索引 ×2，纯前端 | 标题/小节短词已覆盖 | 低 | 无 |
| FlexSearch / MiniSearch | 纯前端 | 可配 CJK encoder | 中高（需自写 UI） | 无 |
| Lunr + 中文扩展 | 构建期索引 | 依赖分词词典 | 中高 | 无 |
| Meilisearch / Typesense | 独立服务 | 好 | 高 | 需 Docker/进程 |
| Algolia DocSearch | SaaS | 好 | 低（需符合条件） | 云端 |

选 Pagefind 的核心理由：**零服务端依赖、零运行时外部请求**（索引与站点同源部署）、不向仓库引入常驻依赖（CLI 由 CI 临时下载并锁定版本）、自带结果 UI 与摘要高亮。

代价是**中文分词适配度低**——检索单位是 token（词），不是「任意连续汉字串」。本项目用一条轻量子串索引补齐短词档（§6）。

参考：[Pagefind 官方文档](https://pagefind.app/) · [Blog 增加搜索功能（elmagnifico）](https://elmagnifico.tech/2026/06/04/Pagefind/)

---

## 2. 工作原理

Pagefind 把检索拆成两个互不耦合的阶段：

**构建期（离线）**
1. 扫描站点 HTML，只取标记了 `data-pagefind-body` 的正文区域；
2. 按语言规则分词，生成倒排索引，输出到 `pagefind/` 目录（`.pf_index` / `.pf_meta` / `.pf_fragment` 等，附 WASM 运行时）；
3. 索引随站点一起部署。

**运行时（浏览器）**
1. 检索页加载 `pagefind.js` + WASM（Rust 编译产物，首次查询时实例化）；
2. 用户输入 → 客户端同样分词 → 在索引中匹配、排序；
3. 按需拉取摘要片段（fragment）并渲染。

可以理解为：**离线建好「词 → 哪些页面」的表，上线后只在浏览器里查这张表**。索引按 fragment 分片、按需加载，因此站点体积与首屏开销不随文章数线性增长。

---

## 3. 本项目集成架构

```
构建期（GitHub Actions）
  Gmeek.py 渲染站点 ──► docs/*.html
        │                    │
        │  文章页带           │
        │  data-pagefind-body│
        ▼                    ▼
  blogBase.json     ┌── scripts/build_search_index.py  ← 抽取「标题 + 小节标题」
  （状态文件）       │        └─► docs/search-index/index.json   （子串轨）
                     └── npx -y pagefind@1.5.2 --site docs
                              └─► docs/pagefind/  ← 倒排索引 + WASM + UI 资源

运行时（浏览器）
  plist.html / post.html
   └─ 搜索框 GET ──► search.html?q=…
                          ├─ <link rel=preload> pagefind-ui.js
                          ├─ <script defer> pagefind-ui.js
                          ├─ fetch search-index/index.json （首次查询时）
                          └─ new PagefindUI({…}) → triggerSearch(q)
                                     │
                                     ├─ processTerm  → 子串精确匹配 → #exactMatches
                                     └─ 结果渲染 → decorate() 补挂标签 + issue 入口
```

### 关键文件

| 角色 | 位置 |
|------|------|
| 构建脚本 | `.github/workflows/Gmeek.yml`（`Build substring search index` + `Build search index`） |
| 语言与链接前缀派生 | `Gmeek.py#search_settings` |
| 子串索引生成器 | `scripts/build_search_index.py` |
| 索引范围标记 | `templates/post.html`（`data-pagefind-body`） |
| 结果 meta | `templates/post.html`（`data-pagefind-meta`） |
| 检索页 | `templates/search.html` |
| 检索入口 | `templates/plist.html`、`templates/post.html` |
| 首页预热 | `templates/base.html` |
| 回归测试 | `tests/test_pipeline.py` |

---

## 4. 构建链路

CI 在**合并后的完整站点**上依次生成两套索引：

```bash
python3 /opt/Gmeek/scripts/build_search_index.py docs   # 子串轨（仅标准库）
npx -y pagefind@1.5.2 --site docs                        # 倒排索引轨
```

两者**都必须跑在合并后的完整站点上**——增量构建时生成目录只含本次重渲染的文章，在其上建索引会丢掉其余全部文章。子串索引脚本从 `/opt/Gmeek`（源码 clone）取，用系统 `python3` 直跑，不依赖 `uv` 环境（`blog` 分支只含 `backup/`、`blogBase.json`、`docs/`，没有 `scripts/`）。

本项目**不使用 `pagefind.yml` 配置文件**，全部走 CLI 默认 + 模板标记；需要调整时优先在 CI 命令加 flag（保持配置单一来源）。上游支持的常用 flag：

| Flag | 作用 |
|------|------|
| `--site <PATH>` | 站点根目录（必填） |
| `--output-subdir <DIR>` | 索引输出子目录，默认 `pagefind` |
| `--root-selector <S>` | 索引根元素，默认 `html`（本项目改用 `data-pagefind-body` 更精确） |
| `--exclude-selectors <S>` | 排除区域（等价于 `data-pagefind-ignore`） |
| `--force-language <LANG>` | 忽略自动检测，强制单一语言索引 |
| `--glob <GLOB>` | HTML 发现模式，默认 `**/*.{html}` |

> 注：Pagefind CLI **没有** `--fragment-size` 这类调分片的 flag，分片由内部按内容长度自动切。

---

## 5. 索引范围与结果元数据

### 索引范围

只有文章页正文容器带 `data-pagefind-body`：

```html
<!-- templates/post.html -->
<div class="markdown-body" id="postBody" data-pagefind-body>
```

列表页、标签页、检索页**不带**该标记，整体不进索引。文章标题经 `<title>` 入索引（已实测可检索）。子串索引（§6）用同一标记界定范围，保证两轨覆盖面一致。

### 结果元数据

检索结果需要展示「文章标签 + issue 入口」，靠文章页输出的两条 meta：

```html
<meta data-pagefind-meta="labels[content]" content='["前端","blog"]' />
<meta data-pagefind-meta="source[content]" content="https://github.com/…/issues/7" />
```

两条约束（易踩）：

1. **必须写成 `[content]` 形式**——默认取元素 `textContent`，而 `<meta>` 的 textContent 为空，会**静默不入索引**；
2. **同名 meta 多个元素只保留最后一个**——故标签必须合并成一个 JSON 数组值，不能一个标签一个元素。

检索页在 `processResult` 中按 URL 收集 meta，结果渲染后由装饰器把标签 chip 与 issue 图标挂到标题行内。

---

## 6. 语言与中文检索（核心限制 + 轻量双轨）

### 语言标记

站点语言经 `<html lang>` 交给 Pagefind 做分词与界面本地化：

```html
<html lang="{{ blogBase['lang'] }}" …>
```

`blogBase['lang']` 由 `Gmeek.py#search_settings` 派生：`i18n` 为 CN 时 `zh-CN`，否则 `en`。

> 与上游写法的差异：上游常见做法是在 `pagefind.yml` 里写 `force_language: zh-cn`。本项目改用 `<html lang>`，因为实测 `--force-language zh` **不改变**检索结果（语言已由 `<html lang>` 正确识别）。

### 中文检索的真实限制（已量化）

Pagefind 的中文索引是**词级切分**，与查询侧分词不一致时短词落空。用 29 篇真实文章实测：

| 查询形态 | 漏检率 | 样本量 |
|---|---|---|
| 完整标题 | 0% | 29 |
| 小节标题 `h2`/`h3` | 0% | 65 |
| 正文高频两字词 → 目标文章 | 12.1% | 107 |
| **标题内两字词 → 目标文章** | **31.5%** | 89 |

漏检的是**真实词**（`入参` / `出参` / `说明` / `常用` / `修改` / `导航`），而 `配置` / `搜索` / `请求头` 正常——**哪些两字词能搜、哪些不能不可预测**。

### 已落地的子串轨（轻量版）

只对「标题 + 小节标题」建一条**连续子串**索引，补齐标题短词档：

- **生成**：`scripts/build_search_index.py`（仅标准库）扫描带 `data-pagefind-body` 的页面，抽取 `<title>` 与正文容器内 `h1–h6` 文本，写 `search-index/index.json`（实测 29 篇 3.3KB，163 篇约 19KB）。
- **匹配**：检索页首次查询时 `fetch` 该 JSON，对 `标题 + 小节标题` 做 `indexOf`（大小写不敏感）；词长 < 2 不触发，命中封顶 10 条。
- **挂接**：经 PagefindUI 的 `processTerm` 回调触发（Pagefind 每次查询前都会调用，已按其 `debounceTimeoutMs` 去抖），无需额外监听输入事件。
- **展示**：独立容器 `#exactMatches` 插到 `.pagefind-ui__drawer` 内、`.pagefind-ui__results-area` 之前 → 视觉上「输入框 → 精确匹配 → Pagefind 结果」，**两轨并列，不隐藏也不过滤 Pagefind 结果**。
- **降级**：索引缺失 / 加载失败时静默跳过，退化为原 Pagefind 检索。

**为什么不做正文轨**：缺口集中在标题短词；正文多字词组 Pagefind 已能命中。加正文前 800 字会把索引从 ~11KB 抬到 ~177KB（gzip ~59KB），工程量与收益之比不划算。正文内两字词（实测 12.1%，以跨词碎片为主）仍未覆盖——若该档影响明显，再评估。

### 不推荐的路线

魔改 Pagefind（改 Rust/WASM 分词）能显著改善中文，但需长期跟进上游合并，且引入编译环境依赖（上游实测：编译产物在旧 CentOS 上跑不了、老 VPS 内存不足无法编译，最终放弃）。**个人站点维护一个搜索引擎分支不划算。**

---

## 7. 检索界面

`templates/search.html` 加载 Pagefind **默认 UI**（`pagefind-ui.js`）：

```js
var ui = new PagefindUI({
    element: "#search",
    baseUrl: "{{ blogBase['searchBaseUrl'] }}",  // 子路径部署需补全前缀
    pageSize: 20,            // 高于默认 5, 减少 "Load more" 触发
    showSubResults: true,    // 保留段落级匹配高亮
    showImages: false,
    debounceTimeoutMs: 250,  // 略紧于默认 300, 减少连续键入的冗余查询
    processResult: function (result) { … },   // 收集 meta, 供装饰器补挂
    processTerm:   function (term) { … }      // 触发子串精确匹配(§6)
});
```

> 上游另有更新的 **Component UI**（`pagefind-component-ui.js` + `<pagefind-config>` / `<pagefind-modal>` 等 Web Components）。本项目仍用默认 UI——结果模板虽不开放，但 `processResult` + 装饰器已能满足「标签 chip + issue 入口」的定制需求。

### 样式接入

尺寸**只经 `--pagefind-ui-scale` 调整**（本项目取 `0.75`）。Pagefind 的输入框高度、放大镜图标位置、清除按钮尺寸都是 `scale` 的联动值，单独覆盖 `height` / `font-size` 会让图标与按钮偏出垂直中心甚至溢出。配色经 CSS 变量映射到站点主题变量，明暗自适应。

### 结果装饰（标签 + issue 入口）

Pagefind 默认 UI **不提供结果模板**，故在结果渲染后二次加工：

- `processResult` 按 URL 收集 `labels` / `source` 到 `metaByUrl`；
- `MutationObserver` 监听结果容器，为每张卡片补挂 `.pagefind-ui__result-meta`；
- 卡片加 `data-gmDecorated` 幂等标记（补挂自身会再次触发观察器，无标记会死循环）；
- 观察器用 `requestAnimationFrame` 节流——同帧内多次插入合并为一次扫描。

> 子串轨的条目**刻意不复用** `.pagefind-ui__result` 类名，避免被该装饰器当成 Pagefind 卡片二次加工。

---

## 8. 检索入口

| 入口 | 位置 | 行为 |
|------|------|------|
| 列表页搜索框 | `templates/plist.html` | GET 提交到 `search.html`，`name="q"` |
| 文章页搜索框 | `templates/post.html` | 同上（复用 `base.html` 的共享 `.site-search` 组件） |
| 标签页筛选 | `templates/tag.html` | 本地 JS 过滤，**不走** Pagefind |
| 深链 | 任意 `search.html?q=…` | `ui.triggerSearch(q)` 承接 |

三处搜索框统一定义在 `base.html` 的 `.site-search`，样式单点维护。

---

## 9. 性能优化

检索页的等待时间主要在「UI 包下载 + WASM 实例化 + 索引分片拉取」。已落地的优化：

| 手段 | 位置 | 效果 |
|------|------|------|
| `pagefind-ui.js` 加 `defer` + `<link rel="preload">` | `search.html` head | 与 HTML 解析并行下载，不阻塞解析 |
| 首页 `requestIdleCallback` 预拉 UI 包 | `base.html` | 「首页 → 检索页」路径省下 ~250KB 冷下载 |
| `pageSize` 上调到 20 | `search.html` | 减少 "Load more" 往返 |
| `debounceTimeoutMs: 250` | `search.html` | 减少连续键入的冗余查询 |
| `MutationObserver` raf 节流 | `search.html` | 减少结果渲染时的重复 DOM 扫描 |
| loading 态 spinner（仅 loading 消息） | `search.html` | 等待反馈；终态消息不加 spinner |
| 子串索引懒加载（首次查询时才 fetch） | `search.html` | ~19KB，不占首屏 |

> **不要**用 Service Worker 缓存 `/pagefind/` 路径：索引更新后 SW 缓存会让**新文章搜不到**（上游实测踩坑）。若站点启用 PWA，须对 `/pagefind/` 与 `/search-index/` 走 network-only。

---

## 10. 排错清单

| 现象 | 常见原因 | 处理 |
|------|----------|------|
| 新文章搜不到 | SW 缓存了 `/pagefind/` | 对 pagefind 路径禁用 SW 缓存；或注销 SW / 硬刷新 |
| 整站检索不可用 | 索引未生成 / 资源 404 | 查 CI `Build search index` 步骤是否成功；确认 `docs/pagefind/` 已部署 |
| **精确匹配块不出现** | 子串索引未生成 / 404 / 被拦截 | 查 CI `Build substring search index`；确认 `docs/search-index/index.json` 可访问；控制台看 fetch 是否失败（失败会静默降级） |
| 精确匹配块位置错乱 | Pagefind 类名变动（`.pagefind-ui__drawer` / `__results-area`） | 升级 Pagefind 后回归；脚本找不到目标时保持原位、不报错 |
| 标签 / issue 入口不显示 | meta 写成了非 `[content]` 形式，或标签未合并为单值 | 检查 `templates/post.html` 的两条 meta |
| 标签 / issue 入口错位 | `processResult` 与 DOM 的 URL 前缀不一致 | 两侧都经 `absUrl()` 归一化；确认 `baseUrl` 与部署子路径一致 |
| 结果链接 404 | 子路径部署未补全前缀 | 确认 `searchBaseUrl` 由 `homeUrl` 正确派生 |
| 中文短词仍漏检 | 该词在**正文**而不在标题/小节 | 现方案不覆盖正文轨（§6），如需再评估 |
| 搜索框图标偏位 / 溢出 | 单独覆盖了输入框 height | 只用 `--pagefind-ui-scale` 统一缩放 |
| 一直「正在搜索」 | 索引文件过大导致主线程 `JSON.parse` 卡死 | 分片 + 仅按需加载 + Worker（本项目轻量轨无此问题） |
| 终态仍显示转圈 | spinner 未限定 loading 态 | 用 `:not(:has(+ .pagefind-ui__results))` 排除计数/零结果消息 |

---

## 11. 维护须知

- **升级 Pagefind**：CI 里锁定版本（当前 `1.5.2`）。升级前确认索引产物结构、UI 类名（`.pagefind-ui__*`）、`pagefind-ui.js` 行为无破坏性变化——结果装饰器与子串轨注入都依赖这些类名。
- **改索引范围**：只动 `data-pagefind-body` / `data-pagefind-meta` 标记；不要改用 `--root-selector` 全局索引（会把导航、页脚一并纳入）。子串轨沿用同一标记，范围自动跟随。
- **改子串轨**：索引内容在 `scripts/build_search_index.py#extract_entry`（只抽标题 + `h1–h6`）；匹配与渲染在 `templates/search.html` 的 `loadExactIndex` / `renderExact` / `placeExactBlock`。
- **改检索界面**：优先用 PagefindUI 的配置项与 CSS 变量；结果模板类定制集中在 `search.html` 的 `processResult` / `decorate`。
- **回归防线**：`tests/test_pipeline.py` 的 `TestSearchIndexBuilder` / `TestExactMatchSearch` / `TestSearchPerformance` / `TestIdlePrefetch` / `TestSearchResultMeta` / `TestSearchResultLabelLink` / `TestSearchBoxSizing` / `TestSearchSettings` 覆盖了上述关键约束，改动后必须全绿。
- **相关决策记录**：见 `docs/adr/` 下 ADR-0007（检索页与索引范围）、ADR-0012（文章页搜索框）、ADR-0018（搜索框统一）、ADR-0021（结果 meta）、ADR-0026（性能优化）、ADR-0027（中文短词子串索引）。

---

## 参考

- [Pagefind 官方文档](https://pagefind.app/)（CLI 配置 / UI 配置 / 搜索 API）
- [Blog 增加搜索功能 — elmagnifico](https://elmagnifico.tech/2026/06/04/Pagefind/)（中文双轨方案、踩坑清单、方案对比）
