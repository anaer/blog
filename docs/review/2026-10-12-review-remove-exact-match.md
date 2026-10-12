# Review Report: 移除中文短词精确匹配（轻量双轨）特性

**Mode**: review
**Reviewer**: WorkBuddy agent / 2026-10-12
**Scope**: `templates/search.html`、`.github/workflows/Gmeek.yml`、`tests/test_pipeline.py`、`scripts/build_search_index.py`（已删）、`docs/adr/ADR-0027-*.md`（已删）、`docs/review/2026-10-09-review-adr0027-substring-index.md`（已删）、`docs/glossary/glossary.md`、`docs/pagefind-integration.md`、`docs/adr/ADR-0007-*.md`、`docs/adr/ADR-0026-*.md`、`CHANGELOG.md`（11 文件，`git diff HEAD`）
**Rule config**: `sha256:a94011598e4f51a6dcfe56d5df80cf4ef487afc6fcacb5c7144b6925d7c05b23`（来源：system）
**Coverage**: 11 reviewed / 11 total / 0 excluded

## Summary

本次改动目标是**移除**站内检索的「中文短词精确匹配（子串索引，轻量双轨）」特性，使检索回归单一的 Pagefind 方案：删除 `search.html` 中加载/匹配/注入子串索引的全部 JS、CSS、HTML 容器，删除构建脚本 `scripts/build_search_index.py` 与其 CI 步骤，删除对应的 12 个测试，并回退 ADR-0027、glossary、pagefind 集成文档到单轨叙述。

整体质量：**清理彻底、链路自洽，无 critical / high / medium 问题**。逐文件复核及全仓悬空引用扫描确认：

- 检索页 `search.html` 已无任何精确匹配残留（变量 `exactHost`/`exactEntries`/`exactTerm`/`EXACT_*`、函数 `loadExactIndex`/`renderExact`/`placeExactBlock`、空壳 `processTerm`、容器 `#exactMatches`、MutationObserver 内两处 `placeExactBlock()` 调用、`.exact-matches*` CSS 全部删除）；保留的 `PagefindUI` 接入、`decorate()`、`processResult`、`?q=` 承接逻辑完整且未被破坏。
- 全仓扫描「`exact*` / `精确匹配` / `search-index` / `build_search_index` / `processTerm` / `子串索引` / `双轨` / `轻量轨` / `ADR-0027`」在活跃文件（排除 `.git`、`CHANGELOG.md` 历史条目）中 **0 命中**。
- 删除 12 个测试后无遗留 import 或孤儿依赖：被删类仅用函数内 `import importlib.util` 加载脚本，模块级 `os`/`json` 仍被其他用例使用；`tests/__pycache__` 旧字节码含已删符号，已清理（pytest 本就从源码重新编译，属良性）。
- 文档与代码事实一致：ADR-0007「未解决风险」改写为「目前未做补充索引，中文短词漏检属已知限制」；pagefind-integration.md §6 同步回退为「已知限制」单段，架构图 / 构建命令 / 角色表 / §7 / §9 / §10 / §11 / 参考链接中所有双轨、子串、精确匹配分支均已清除；ADR-0007 与 ADR-0026 的 ADR-0027 反向链接已移除。
- 全量 pytest 复跑：**227 passed**（原 239，移除 12），无回归。

## Issues

| # | Severity | File:Line | Category | Finding | Recommendation |
|---|----------|-----------|----------|---------|----------------|
| 1 | Low | `tests/__pycache__/test_pipeline.cpython-*.pyc` | build-artifact | 旧字节码仍含已删的 `build_search_index` / `TestSearchIndexBuilder` / `TestExactMatchSearch` 符号；运行期无害（pytest 按源码 mtime/哈希重编译），但会造成 `grep` 误报且不利于审计 | 已清理；建议在 CI 中加入 `find . -name __pycache__ -type d -prune -exec rm -rf {} +`（或 `pytest --cache-clear`）避免遗留 |
| 2 | Info | `docs/adr/ADR-0027-*.md`（整文件删除） | adr-convention | ADR-0027 采用**整文件删除**而非「标记 Superseded 保留」。父决策 ADR-0007 的「未解决风险」已改写、反向链接已移除，决策链路自洽；但 ADR 惯例通常保留被取代的 ADR 并加 `Superseded by` 头，以保留演进史与回溯能力 | 鉴于用户明确「一并清理」且全仓已无引用，保留删除结论；若未来需要审计「为何曾引入又移除」，可在 `docs/adr/` 加一条极短的 deprecation 纪要（可选，非必须） |
| 3 | Info | `CHANGELOG.md:32-39` | changelog-policy | 历史条目（特性新增）仍完整保留，与新条目 `26.1012.0838`（特性移除）并存 | 符合「仅追加」CHANGELOG 策略，属预期行为，无需处置；提示后续读者「该特性已被 `26.1012.0838` 移除」 |

## By Severity

### Critical

无。

### High

无。

### Medium

无。

### Low

- **`tests/__pycache__/test_pipeline.cpython-*.pyc`** [build-artifact] — 旧字节码含已删符号，已清理；补一条 CI 清理即可杜绝复现（见 Issue 1）。

### Info（非缺陷，仅记录）

- **`docs/adr/ADR-0027-*.md` 整文件删除** — 父 ADR 反向链接与「未解决风险」已同步改写，无悬空引用；删除 vs 标记 superseded 属约定取舍（见 Issue 2）。
- **`CHANGELOG.md` 历史条目保留** — 仅追加策略，预期行为（见 Issue 3）。

## Severity Distribution

- Critical: 0
- High: 0
- Medium: 0
- Low: 1
- Info: 2

## Language-Specific Notes

| Rule group | Pattern | Rule file | Source | Files |
|------------|---------|-----------|--------|-------|
| 1 | `.github/workflows/*.yml` | github-workflows.md | system | 1 |
| 2 | `default`（HTML/Jinja/Markdown） | default.md | system | 6 |
| 3 | `**/*.{py,pyi,pyw,ipynb}` | python.md | system | 4（含 2 个已删文件） |

- **group 1（`Gmeek.yml`）**：仅删除 `Build substring search index` 步骤（含注释），保留 `Build search index`（pagefind）及其「必须跑在合并后的完整站点上」注释。步骤顺序、缩进、依赖无破坏；检索构建回归单轨。
- **group 2（`search.html` / `pagefind-integration.md` / `glossary.md` / `ADR-0007` / `ADR-0026`）**：按通用规则核对注入面、死代码、文档事实一致性。`search.html` 仍仅拼入 `{{ blogBase['homeUrl'] }}`（配置派生，非用户输入）；文档中凡涉及「子串轨 / 双轨 / 精确匹配 / `processTerm` / `#exactMatches`」的叙述已全部清除，且与现状（仅 Pagefind）一致。
- **group 3（`tests/test_pipeline.py` / `scripts/build_search_index.py` 已删）**：按 python.md 测试节核对——删除 `TestSearchIndexBuilder`（6 例）与 `TestExactMatchSearch`（6 例）后，无遗留 import、无孤儿依赖；模块级 `os`/`json` 仍被其他用例使用；函数内 `import importlib.util` 随类一起删除。其余检索相关用例（`TestSearchPerformance` / `TestIdlePrefetch` / `TestSearchResultMeta` / `TestSearchResultLabelLink` / `TestSearchBoxSizing` / `TestSearchSettings`）保持完整，回归防线覆盖 Pagefind 单轨形态。

### 悬空引用扫描（用户指定检查项①）

全仓（排除 `.git` 与 `CHANGELOG.md` 历史条目）对以下 token 扫描均 0 命中：

```
exact / exactMatches / loadExactIndex / renderExact / placeExactBlock / processTerm
build_search_index / search-index / EXACT_MIN_LEN / EXACT_MAX_HITS
精确匹配 / 子串索引 / 双轨 / 轻量轨 / ADR-0027
```

→ 无变量 / 函数 / 类名 / CI 步骤 / ADR 反向链接悬空。

### 测试遗留依赖扫描（用户指定检查项②）

`grep build_search_index tests/` 在源码层 0 命中（仅在已清理的旧 `__pycache__` 字节码中命中，已删除）。

### 文档—代码一致性（用户指定检查项③④）

- ④ 注释指向已删逻辑：`search.html` 与 `pagefind-integration.md` 中均无任何指向已删 `loadExactIndex`/`renderExact`/`placeExactBlock`/`processTerm`/`#exactMatches` 的残留注释（此前 §10「轻量轨无此问题」措辞已在前序清理中改为「pagefind 已内部处理」）。
- ③ 文档一致性：ADR-0007「未解决风险」与 pagefind-integration.md §6 均统一为「未引入补充索引轨，中文短词漏检属已知限制」，口径一致；glossary 的「子串检索索引」词条已删。

## Coverage Detail

| File | Status | Note |
|------|--------|------|
| `templates/search.html` | reviewed | 删除精确匹配 JS/CSS/容器/MutationObserver 调用；保留 Pagefind 单轨逻辑完好 |
| `.github/workflows/Gmeek.yml` | reviewed | 删 `Build substring search index` 步骤；保留 pagefind 步骤 |
| `tests/test_pipeline.py` | reviewed | 删除 `TestSearchIndexBuilder` + `TestExactMatchSearch`（12 例）；无遗留依赖 |
| `scripts/build_search_index.py` | deleted | 已删除，无引用 |
| `docs/adr/ADR-0027-chinese-substring-search-index.md` | deleted | 已删除，无引用 |
| `docs/review/2026-10-09-review-adr0027-substring-index.md` | deleted | 已删除，无引用 |
| `docs/glossary/glossary.md` | reviewed | 移除「子串检索索引」词条 |
| `docs/pagefind-integration.md` | reviewed | 回退单轨：架构图 / §4 / §6 / §7 / §9 / §10 / §11 / 参考链接全部清除双轨与子串叙述 |
| `docs/adr/ADR-0007-on-site-search-pagefind.md` | reviewed | 「未解决风险」改写 + 移除 ADR-0027 反向链接 |
| `docs/adr/ADR-0026-pagefind-search-performance.md` | reviewed | 移除 ADR-0027 反向链接 |
| `CHANGELOG.md` | reviewed | 追加 `26.1012.0838` 移除条目；历史条目保留（仅追加） |

### ADR 边界 / 注释约定（Step 2.7 + 2.8）

- **ADR 边界（Step 2.7）**：被删 ADR-0027 的反向链接已从 ADR-0007、ADR-0026 移除；父决策 ADR-0007 的「未解决风险」已改为「未做补充索引，属已知限制」，与当前单轨实现一致，决策链路自洽。唯一可议点见 Issue 2（删除 vs 标记 superseded），非阻塞。
- **注释约定（Step 2.8）**：`check_comment_conventions.py` 未在本机可用，改为等价人工核查——`search.html` 与 `docs/pagefind-integration.md` 中无任何指向已删逻辑的注释，亦无越界的 `docs/adr/ADR-0027` 绝对路径串（活跃文件中 0 命中，见「悬空引用扫描」）。`CHANGELOG.md` 中出现的 `ADR-0027` 为历史条目叙述，属合法落点，不计入问题。

## Follow-Up

1. （可选）在 CI 中加入 `__pycache__` 清理步骤，杜绝旧字节码遗留（Issue 1）。
2. （可选）若需保留演进史，在 `docs/adr/` 加一条极短 deprecation 纪要指向 `CHANGELOG.md:26.1012.0838`（Issue 2）。
3. 本次为**只审查**请求：未改动任何代码（仅清理了良性遗留字节码 `tests/__pycache__` 与 `scripts/__pycache__`）。如需将上述可选项落地请确认。

## 决策性内容

本次审查**确认**（而非新产生）如下事实，均已与代码/文档现状核对一致，无需新落 ADR：

- 检索形态已稳定为 **Pagefind 单轨**；中文短词漏检为 Pagefind 词级切分的已知限制，不再由补充索引补齐。
- ADR-0007 的「未解决风险」现准确反映该限制，与 `docs/pagefind-integration.md` §6 口径一致。

无新增决策需要沉淀。
