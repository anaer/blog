# Review Report: ADR-0026 检索性能优化（Pagefind 加载链 / 每查询渲染 / 装饰器节流）

**Mode**: review
**Reviewer**: WorkBuddy agent / 2026-10-09
**Scope**: `templates/base.html`、`templates/search.html`、`tests/test_pipeline.py`（工作区改动，`git diff HEAD`）
**Rule config**: `sha256:a94011598e4f51a6dcfe56d5df80cf4ef487afc6fcacb5c7144b6925d7c05b23`（来源：system）
**Coverage**: 3 reviewed / 3 total / 0 excluded

## Summary

本次改动目标是缩短站内检索的等待时间：`pagefind-ui.js` 由同步加载改 `defer` + `preload`，`base.html` 增加首页 `requestIdleCallback` 预拉，`PagefindUI` 配置调整（`pageSize` 10→20、`debounceTimeoutMs` 250、保留 `showSubResults`），`processResult`/`lookup` 去掉 URL 双键冗余，`MutationObserver` 加 `requestAnimationFrame` 节流，并给加载中的 `.pagefind-ui__message` 加视觉提示。

整体质量：**功能改动正确，核心逻辑（raf 节流、URL 归一化、defer 与 DOMContentLoaded 的时序）经复核无缺陷**。发现 **2 个 medium、3 个 low**，均集中在「加载状态视觉提示的作用域」与「新回归用例的断言有效性」两处——不影响功能正确性，但前者会产生可见的 UX 瑕疵，后者削弱了回归防护的可信度。

- 无 critical / high。
- `defer` 与内联 `DOMContentLoaded` 监听器的时序正确：defer 脚本在解析完成后、`DOMContentLoaded` 前执行，回调里 `new PagefindUI` 时全局已定义。
- `processResult` 与 `lookup` 都经同一 `absUrl()` 归一化（`URL.href` 会统一百分号编码与相对路径），去掉 pathname 兜底后两侧仍派生同一字符串——该简化**成立**。
- raf 节流不丢工作：`decorate` 扫描 scope 内全部结果且带 `data-gmDecorated` 幂等标记，节流只推迟不跳过。

## Issues

| # | Severity | File:Line | Category | Finding | Recommendation |
|---|----------|-----------|----------|---------|----------------|
| 1 | Medium | `templates/search.html:40` | bug | `.pagefind-ui__message::before` 的旋转 spinner 会作用于**全部**三种消息态。Pagefind UI 1.5.2 中该 class 用于：loading（"Searching …"）、零结果（"No results for …"）、结果计数（"N results for …"）。后两者是终态，却会显示一个**永不停止的加载指示器** | 用 `:has()` 限定到 loading 态：`#search .pagefind-ui__message:not(:has(+ .pagefind-ui__results))::before`（计数/零结果消息后恒接 `<ol class="pagefind-ui__results">`，loading 消息不接）；或去掉 spinner 只保留配色 |
| 2 | Medium | `tests/test_pipeline.py:1154` | test | `test_process_result_uses_single_abs_url_key` 为**假阳性**。正则 `\{(.*?)\}` 非贪婪，捕获止于 `result.meta \|\| {}` 的首个 `}`，实际赋值行 `metaByUrl[absUrl(result.url)] = info;` 根本不在捕获范围内；断言之所以通过，仅因**注释文本**含 `absUrl(result.url)` | 把捕获锚定到 `return result;`（如 `\{(.*?)\n\s*return result;`），并断言 `"urlKeys(" not in body` 与 `"metaByUrl[absUrl(result.url)] = info" in body` |
| 3 | Low | `tests/test_pipeline.py:1169` | test | `test_lookup_no_longer_falls_back_to_pathname` 的 `assert "new URL(" not in body` 是**空断言**：改动前的实现走 `urlKeys(u)`（`new URL().pathname` 在另一个函数体内），真实的回归路径不会把 `new URL(` 引入 `lookup` 体。用例仍能拦住回归，但靠的是 `absUrl` 缺失，而非这条断言 | 改为断言 `"urlKeys" not in body`，或直接钉死单键形态 `metaByUrl[absUrl(u)]` |
| 4 | Low | `tests/test_pipeline.py:1177` | test | `test_mutation_observer_uses_raf_throttle` 的正则要求 `})` 与 `.observe(` **紧邻**，仅适配新的单行写法；还原为改动前的多行 `.observe(` 形态时正则失配，用例会以「MutationObserver 创建语句未找到」失败——**报错信息与真实原因（缺 raf 节流）不符**。此外 `rafPending` 断言扫的是整篇 HTML 而非捕获到的回调体 | 正则允许 `.observe(` 前有空白（`\}\)\s*\.observe\(`），并把 pending-flag 断言收敛到捕获到的 `body` |
| 5 | Low | `tests/test_pipeline.py:1183` | test | `test_loading_state_styled` 只校验 CSS 片段存在（`.pagefind-ui__message` / `::before` / `rotate(360deg)`），**不校验作用域**，因此对 Finding 1 给出虚假信心。附带：`"rotate(360deg)" in html or "rotate(360deg" in html` 的第二个析取项是第一个的子串，`or` 冗余 | 修正 Finding 1 后，补一条断言（如 `:has(+ .pagefind-ui__results)` 选择器存在），使用例能反映作用域约束 |

## By Severity

### Critical

无。

### High

无。

### Medium

- **`templates/search.html:40`** [bug] — spinner 作用于 loading / 零结果 / 结果计数三种 `.pagefind-ui__message`，终态仍显示无限旋转的加载指示器。
  > 建议：`:not(:has(+ .pagefind-ui__results))` 限定 loading 态（计数与零结果消息后恒有 `<ol class="pagefind-ui__results">`，loading 消息无）。代码注释已意识到「同名选择器在零结果态也会被使用」，但结论「只加视觉修饰」未覆盖「spinner 本身就是加载语义」这一点。
- **`tests/test_pipeline.py:1154`** [test] — `test_process_result_uses_single_abs_url_key` 假阳性。
  > 建议：见上表；已用反证确认——还原为改动前的 `urlKeys(...)` 实现（保留同段注释）后该用例**仍然通过**。

### Low

- **`tests/test_pipeline.py:1169`** [test] — `new URL(` 断言空转，实际拦截靠 `absUrl` 缺失。
  > 建议：改断言 `"urlKeys" not in body`。
- **`tests/test_pipeline.py:1177`** [test] — 正则对旧形态失配，失败信息误导；pending-flag 断言范围过宽。
  > 建议：允许 `.observe(` 前空白，并把断言收敛到捕获体。
- **`tests/test_pipeline.py:1183`** [test] — 只校验 CSS 存在、不校验作用域，掩盖 Finding 1。
  > 建议：修正 Finding 1 后补作用域断言。

## Severity Distribution

- Critical: 0
- High: 0
- Medium: 2
- Low: 3

## Language-Specific Notes

| Rule group | Pattern | Rule file | Source | Files |
|------------|---------|-----------|--------|-------|
| 1 | `default`（HTML/Jinja） | default.md | system | 2 |
| 2 | `**/*.{py,pyi,pyw,ipynb}` | python.md | system | 1 |

- **group 1（`templates/*.html`）**：按通用规则核对——注入面（`{{ blogBase['homeUrl'] }}` 拼入 `href`/`src`，值为配置派生，非用户输入）、资源释放、死代码。`defer`/`preload`/`prefetch` 的浏览器语义与站点无 CSP 的现状相容。
- **group 2（`tests/test_pipeline.py`）**：按 python.md「测试代码」节核对，重点即弱断言/假阳性（Finding 2/3/4）——本轮 11 条新用例中 3 条存在断言有效性问题，1 条（defer/preload/pageSize/subResults/debounce）经反证确认有效。

### 反证记录（新增用例的有效性验证）

| 用例 | 反证方法 | 结果 |
|------|----------|------|
| `test_pagefind_ui_script_is_deferred` | 还原同步 `<script>` | ✅ 失败（用例有效） |
| `test_pagefind_ui_is_preloaded` | 删除 preload 行 | ✅ 失败（用例有效） |
| `test_page_size_is_twenty` | `pageSize` 还原 10 | ✅ 失败（用例有效） |
| `test_process_result_uses_single_abs_url_key` | 还原 `urlKeys` 旧实现（保留注释） | ❌ **仍通过 → 假阳性** |
| `test_lookup_no_longer_falls_back_to_pathname` | 还原旧 `lookup` | ✅ 失败（但归因于 `absUrl` 缺失，非 `new URL` 断言） |
| `test_mutation_observer_uses_raf_throttle` | 还原无 raf 的多行 observer | ✅ 失败（但归因于正则失配，非 raf 断言） |

## Coverage Detail

| File | Status | Note |
|------|--------|------|
| `templates/base.html` | reviewed | idle prefetch 脚本；`requestIdleCallback` 降级与 `window load` 时序正确 |
| `templates/search.html` | reviewed | preload/defer、PagefindUI 配置、processResult/lookup 简化、raf 节流、loading 样式 |
| `tests/test_pipeline.py` | reviewed | 11 条新用例；3 条断言有效性存疑（Finding 2/3/4） |

本次范围的文档改动（`docs/adr/ADR-0026-*.md`、`docs/glossary/glossary.md`、`docs/adr/ADR-0007/0018/0021`、`CHANGELOG.md`）不在代码评审范围；ADR 编号在 `docs/` 内属合法落点，未计入问题。

### ADR 边界 / 注释约定（Step 2.7 + 2.8）

- 运行 `check_comment_conventions.py <3 files> --check-refs`，**本次引入的 2 处 C1 已修复**（`TestSearchPerformance` / `TestIdlePrefetch` 的 docstring 原含 `docs/adr` 路径，已改为自描述文本）。
- 剩余 4 处命中均为 **HEAD 既有、超出本次 diff 范围**，仅记录不处置：`tests/test_pipeline.py:195`（C2「旧实现」措辞）、`:1045`（C1 `docs/adr`）、`:1402`/`:1403`（C1，校验 CI 工作流删除 `docs/adr` 的断言）。项目自有 `TestAdrBoundary` 仅守护「编号」形态（`ADR-\d{4}`），比通用检查器宽松，故这些行在其下不报——属项目约定与通用检查器的口径差，非本次回归。

## Follow-Up

1. **建议先修 Finding 1**（medium，可见 UX 瑕疵）：给 spinner 加 `:not(:has(+ .pagefind-ui__results))` 作用域，并补一条作用域断言。
2. **建议修 Finding 2**（medium，假阳性用例）：重写捕获锚点与断言，使其真能拦住 `urlKeys` 回归。
3. Finding 3/4/5 为 low，可合并到同一批测试加固中处理。
4. 修复后按 `references/fix-verification.md` 复跑反证，确认新断言在「还原旧实现」时确实失败。
5. 本次为**只审查**请求，未改动上述代码（仅修复了本次引入的 2 处 C1 注释越界，已在「注释约定」节披露）；如需继续修复请确认。

## 决策性内容

本次审查**确认**（而非新产生）了两项既有设计取舍，均已在 `docs/adr/ADR-0026` 记录，无需新落 ADR：

- `processResult`/`lookup` 去掉 pathname 双键冗余的**前提**是「两侧 URL 均经 `absUrl()` 归一化」——已复核成立。
- `MutationObserver` 采用 raf 节流而非取消观察——节流不丢工作的依据是 `decorate` 的全量扫描 + `data-gmDecorated` 幂等标记。

无新增决策需要沉淀。
