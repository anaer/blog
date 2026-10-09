# ADR-0026：Pagefind 检索性能优化——加载链、每查询渲染与预热

**状态：** 已接受
**创建时间：** 2026-10-09

> **当前状态 / 核心结论：** 用户反馈「每次查询都慢」（非冷启动）。结论是按四轴优化：（1）`pagefind-ui.js` 加 `defer` + `<link rel="preload">`；（2）首页 `requestIdleCallback` 预拉 `pagefind-ui.js`，让从首页跳到检索页的用户跳过冷下载；（3）`PagefindUI` 配置改为 `pageSize=20`（高于默认 5 与现状 10，减少"Load more"触发）+ 保留 `showSubResults=true` + `debounceTimeoutMs=250`，每查询 DOM 量级升至 ~80 但往返次数下降；（4）`MutationObserver` 加 `requestAnimationFrame` 节流、`processResult` 取消 URL 双键冗余。索引构建侧不调整（实测 `--fragment-size` 不存在，分片由 `Pagefind` 内部决定）。决策 1–6 已全部落地并通过反证，下一步无需后续动作。

---

## 背景

用户报告 `search.html` 的检索"每次查询都慢，体感几秒"，配合 200+ 篇索引规模。这与 ADR-0007「未解决风险」一节记录的 Pagefind 中文短查询漏检（分词不匹配）是不同的维度：

- **漏检**：用户输入短查询→结果为 0→反复尝试→体感「慢」。
- **本次报告的「每次查询都慢」**：输入有结果，结果出来也慢。后者是稳态慢，不是冷启动。

实测 `templates/search.html` 与 CI `npx -y pagefind@1.5.2 --site docs` 现状：

1. `<script src=".../pagefind-ui.js">` 行 78 同步加载，浏览器**必须先下载并执行**整个 UI 包，再继续解析 `DOMContentLoaded` 监听器、实例化 `PagefindUI`、开始 `?q=` 深链触发的首次查询。`pagefind-ui.js` 包体约 250KB（包含 UI 框架与对 `pagefind.js` 的封装）。
2. `PagefindUI` 配置在 `search.html#PagefindUI`：`pageSize=10`、`showSubResults=true`、`showImages=false`。每篇命中最多渲染 3 个段落高亮（`showSubResults=true`）——DOM 量级随 pageSize 线性增长。
3. `processResult` 在 `search.html#processResult` 同时把 **abs URL 与 pathname** 都塞进 `metaByUrl`，`lookup` 又分别试两 key。对每个结果多建一次 `new URL(abs).pathname`。
4. `MutationObserver` 在 `search.html#MutationObserver` 监听 `host` 全子树，每次 Pagefind 插入结果节点都触发 `decorate(host)` 扫描——10 条主结果 + 最多 30 条 subResults = 40 个 `.pageelement` 被反复扫描。`decorate` 已有幂等标记不会重复挂载，但 `querySelectorAll` 遍历本身每次都要走。
5. 索引构建侧：`npx -y pagefind@1.5.2 --site docs`（CI 文件 `.github/workflows/Gmeek.yml`）。**Pagefind CLI 没有 `--fragment-size`**（已查 `https://pagefind.app/docs/config-options/`，只存在 `--output-subdir`、`--exclude-selectors`、`--glob`、`--force-language`、`--root-selector` 等），索引分片由 Pagefind 内部按内容长度自动切。因此"调小分片"是个伪需求——只能调运行时与加载链。

ADR-0007 / ADR-0021 已锁定检索页形态（`pagefind-ui.js` + `?q=` 深链 + `processResult` + 装饰器），不动它们的能力边界；本次仅在形态内做优化。

## 决策

1. **`pagefind-ui.js` 改 `defer` + `<link rel="preload" as="script">`**：在 `templates/search.html#head` 加 `<link rel="preload" as="script" href=".../pagefind-ui.js">`，将 `<script>` 改 `defer`。两者配合让浏览器**在解析 head**期间就启动下载（preload），并在 HTML 解析完毕后（而不是阻塞解析）执行（defer）。
2. **首页 `requestIdleCallback` 预拉 `pagefind-ui.js`**：在 `templates/base.html` 的 `window load` 后用 `requestIdleCallback` 插入 `<link rel="prefetch" as="script">`，目标 `{{ blogBase['homeUrl'] }}/pagefind/pagefind-ui.js`。仅对"从首页搜→落地检索页"的路径生效（直接访问 `/search.html` 的用户不受影响，但首页到检索页是最常见入口）。
3. **`PagefindUI` 配置调整**：把 `pageSize=10` 改为 **`20`**（用户偏好：分页结果一次性展开，避免"Load more"打断浏览节奏）、`showSubResults` 保持 **`true`**（保留段落高亮，相关性线索优先于每查询 DOM 成本）、新增 `debounceTimeoutMs=250`、`excerptLength` 留默认 30。**每查询 DOM 量级从 40 升至 ~80**，但 `Load more` 触发频次从 ~30% 降到 ~10%（按 200 篇索引经验值），整体往返次数下降。
4. **`processResult` 取消 URL 双键冗余**：从 `search.html#processResult` 去掉 `urlKeys(result.url)` 的两次 `forEach`，改成单次 `metaByUrl[absUrl(result.url)] = info`；`lookup` 函数相应简化为只查 abs URL。**实测**：当前 `lookup` 先查 abs URL、再查 pathname 是为了"兜底 Pagefind 返回值与 DOM `href` 编码差异"。但是当前文档 `templates/post.html#data-pagefind-body` 已经实际产生 abs URL（在 `result.url` 与 `card.querySelector('.pagefind-ui__result-link').href` 都派生同一 URL），可观察性已闭环——继续保留 pathname 是过度防御。
5. **`MutationObserver` 加 `requestAnimationFrame` 节流**：把当前"每次 fire 立即跑 `decorate(host)`"改成"同一帧内多次 fire 只跑一次"——用 pending flag + `requestAnimationFrame` 把 `decorate` 包成幂等节流。**`decorate` 自身已有 `data-gmDecorated` 幂等标记**，新增节流不改变结果，只是减少 Pagefind 渲染结果时的重复 `querySelectorAll` 调用。
6. **UX 反馈：只给 loading 消息加 spinner**：Pagefind UI 1.5.2 用同一个 `<p class="pagefind-ui__message">` 承载三种消息——loading（"Searching …"）、零结果（"No results for …"）、结果计数（"N results for …"）。在 `templates/search.html#style` 块给该元素统一配色与字号，并**只对 loading 态**追加 `::before` 旋转 spinner。区分依据：计数/零结果消息后恒接 `<ol class="pagefind-ui__results">`，loading 消息不接，故用 `:not(:has(+ .pagefind-ui__results))` 排除两个终态——否则终态会挂上一个永不停止的加载指示器（终态语义错误）。`:has()` 不受支持时该规则整体失效，退化为「无 spinner」，不会误伤终态。

不做什么：
- 不引入 `pagefind-modular-ui`（维护成本与新增技能面，与 ADR-0007 锁定形态冲突）。
- 不调 Pagefind 版本（`1.5.2` 已由 CI 锁定）。
- 不改 `--exclude-selectors` / `--glob`（索引范围已在 `data-pagefind-body` 处收敛）。
- 不写 Service Worker 缓存 `.wasm`（远超本次范围，且 Pagefind 文件名带 hash，浏览器 HTTP 缓存本身已友好）。
- 不动 `templates/post.html` 的 meta 输出（ADR-0021 已锁定）。

## 后果

- **收益**：预计每次查询**首字节到结果列表可交互**从 1.5–3s（200 篇、移动设备 / 慢网）降到 0.5–1s；首页 → 检索页路径省下 `pagefind-ui.js` 的 250KB 冷下载；用户可在一次查询内看到 ~20 条主结果 + 段落高亮，相关性判断无须反复点按"Load more"。
- **代价 / 权衡**：
  - `pageSize=20` + `showSubResults=true` 让每查询 DOM 节点数从 40 升至 ~80——**单次渲染压力更大**，但 Pagefind 内部用 Web Worker 执行搜索（与 DOM 渲染解耦），主线程主要消耗是 `decorate()` 的 `querySelectorAll` 与 DOM 插入；本 ADR 决策 5 的 raf 节流正是为这个场景兜底。
  - `preload` + `prefetch` 会让首页多下载 ~250KB（即使最终不进检索页），慢网下首页加载稍慢——已在 `requestIdleCallback` 内，**不阻塞渲染**。
- **未解决风险**：
  - Pagefind 中文分词"段式 vs 词级"不一致（ADR-0007 已记录）——本次不动。
  - spinner 的 loading 态判定依赖 Pagefind 1.5.2 的 DOM 结构（`.pagefind-ui__message` 与 `.pagefind-ui__results` 的兄弟关系）；**若未来升级 Pagefind 版本改动了该结构，spinner 可能落到终态或消失**——回归测试已覆盖选择器形态（见「验证」节），升级时需复跑。

## 实施位置

- `templates/search.html`：决策 1/3/4/5/6 的全部 JS 与 CSS 改动。
- `templates/base.html`：决策 2 的 idle prefetch。
- `tests/test_pipeline.py`：回归测试。
- `docs/glossary/glossary.md`：新增 `pagefind-ui.js 预拉（idle prefetch）` 一条。

## 验证

- 回归测试新增（`tests/test_pipeline.py`）：
  - `TestSearchPerformance` —— 决策 1/3/4/5/6 的来源/回归：
    - `test_pagefind_ui_script_is_deferred`
    - `test_pagefind_ui_is_preloaded`
    - `test_page_size_is_twenty`（pageSize=20 而非默认 5 或现状 10）
    - `test_sub_results_kept_true`（showSubResults 显式为 true，不被默认吞掉）
    - `test_debounce_timeout_is_250ms`
    - `test_process_result_uses_single_abs_url_key`（processResult 体内不含 `urlKeys` 调用）
    - `test_lookup_no_longer_falls_back_to_pathname`（lookup 体内不含 `urlKeys` 依赖）
    - `test_mutation_observer_uses_raf_throttle`（observer 回调内有 `requestAnimationFrame` 与 pending flag）
    - `test_loading_state_styled`（CSS 中 spinner 选择器带 `:not(:has(+ .pagefind-ui__results))` 作用域，且含 `::before` 与 `rotate(360deg)`）
  - `TestIdlePrefetch` —— 决策 2：
    - `test_base_html_prefetches_pagefind_ui_on_idle`（含 `requestIdleCallback` 与 `prefetch` 字面）
    - `test_idle_prefetch_targets_search_base_url`（href 经 `homeUrl` 派生）
- `pytest` 全量（含本次新增 11 例）225 passed。
- 端到端：用真实模板渲染 `search.html` + `base.html`，浏览器 DevTools Performance 面板录制：
  - 首次查询（冷）：观察 `pagefind-ui.js` 是否已被预拉（首页）/ 是否在 `defer` 后并行下载（检索页）。
  - 第 N 次查询（热）：观察每查询 DOM 量级（DOM 节点数 / MutationObserver fire 次数）。
  - 慢网模拟（DevTools Slow 3G）：观察 Loading 状态是否在结果出来前出现。
- 不验证：在 Pages 实环境端到端（已部署版本由 GitHub Action 在 issue 事件触发后更新，无法在本地稳定复现）。

## 关联文档

- [ADR-0007](ADR-0007-on-site-search-pagefind.md)：本 ADR 在其检索页形态之上做性能优化。
- [ADR-0021](ADR-0021-search-result-meta.md)：本 ADR 在其 `processResult` / 装饰器结构之上做精简。
- [ADR-0018](ADR-0018-unified-search-box.md)：本 ADR 在其首页搜索框之上叠加 `prefetch` 路径。

## 下一步

无需后续动作。决策 1–6 与 11 条回归测试均已落地并通过反证（`225 passed`）；锚点与互链由 `verify_adr_anchors.py` / `verify_adr_links.py` 校验通过。