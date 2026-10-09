# Review Report: ADR-0027 中文短词子串索引（轻量双轨）

**Mode**: review
**Reviewer**: WorkBuddy agent / 2026-10-09
**Scope**: `scripts/build_search_index.py`、`templates/search.html`、`.github/workflows/Gmeek.yml`、`tests/test_pipeline.py`（工作区改动，`git diff HEAD` + 未跟踪新文件）
**Rule config**: `sha256:a94011598e4f51a6dcfe56d5df80cf4ef487afc6fcacb5c7144b6925d7c05b23`（来源：system）
**Coverage**: 4 reviewed / 4 total / 0 excluded

## Summary

本次改动为检索页新增一条中文短词子串索引轨：新增仅标准库的构建期生成器、在 CI 的 pagefind 步骤前插入生成步骤、在检索页用 PagefindUI 的 `processTerm` 回调触发匹配并把结果以独立容器插到 Pagefind 结果之上。

整体质量：**功能正确、防御到位**。发现 **0 critical / 0 high / 0 medium、3 low**，均属防御性加固与运维权衡，不阻塞合并。关键正确性点已逐条复核：

- 生成器的正文容器深度追踪（栈 + 空元素集合）在嵌套与自闭合标签下正确；`data-pagefind-body` 外的小节标题不会被收录（单测覆盖）。
- 检索页**不隐藏、不过滤** Pagefind 结果（负向断言 + headless Chrome 实测两轨共存）。
- 渲染走 `textContent`（无 `innerHTML`），链接由构建期生成的相对路径拼 `homeUrl`，无注入面。
- `placeExactBlock` 幂等（`parentNode === drawer` 提前返回），与既有 raf 节流观察器共用，无自触发循环。
- 索引缺失 / fetch 失败静默降级为原检索（`catch` 置空数组，不重试）。

端到端实测（headless Chrome + 真实 29 篇站点）：查询「入参」时 Pagefind 返回 2 条但**不含**目标文章《OpenResty打印请求入参和出参》，精确匹配块正确补上；DOM 顺序为「输入框 → 精确匹配 → Pagefind 结果」。

## Issues

| # | Severity | File:Line | Category | Finding | Recommendation |
|---|----------|-----------|----------|---------|----------------|
| 1 | Low | `templates/search.html:110` | maintainability | `.exact-matches` 的隐藏只依赖 UA 样式表的 `[hidden]{display:none}`。当前无规则覆盖 `display`，实测隐藏生效；但日后若给 `.exact-matches` 加任何 `display` 声明，`hidden` 即失效 | 补一条防御性规则 `#search .exact-matches[hidden]{display:none;}` |
| 2 | Low | `.github/workflows/Gmeek.yml`（`Build substring search index`） | maintainability | 该步骤失败会阻断整个发布——把一个**补充性**索引做成了单点故障。与 pagefind 步骤的 fail-loud 策略一致，但 pagefind 失败会导致「整站检索不可用」，性质更重 | 保留（一致性优先，静默失败会让精确匹配悄悄失效）；建议在 ADR-0027「代价」中显式记一句「生成失败即阻断发布」 |
| 3 | Low | `scripts/build_search_index.py`（`PageParser.handle_starttag`） | maintainability | 若输入 HTML 存在**未闭合**的标题标签，`_cap` 不会被清空，后续文本会累积到下一个标题的结束处（归属错位）。本项目模板输出结构良好，实测 29 篇真实页面无此情况 | 无需改（输入受控）；如需加固，可在 `handle_starttag` 遇新标题时先冲刷旧缓冲 |

## By Severity

### Critical

无。

### High

无。

### Medium

无。

### Low

- **`templates/search.html:110`** [maintainability] — 隐藏仅靠 UA `[hidden]`，缺防御性 `display:none` 兜底。
  > 建议：`#search .exact-matches[hidden]{display:none;}`（一行，与既有 `#search .exact-matches` 规则同处）。
- **`.github/workflows/Gmeek.yml`** [maintainability] — 补充性索引失败即阻断发布。
  > 建议：保留行为（一致性 + 不静默），在 ADR-0027 记明该取舍。
- **`scripts/build_search_index.py`** [maintainability] — 未闭合标题标签下的文本归属错位（输入受控，当前不可触发）。
  > 建议：不改；作为已知边界记录。

## Severity Distribution

- Critical: 0
- High: 0
- Medium: 0
- Low: 3

## Language-Specific Notes

| Rule group | Pattern | Rule file | Source | Files |
|------------|---------|-----------|--------|-------|
| 1 | `**/*.{py,pyi,pyw,ipynb}` | python.md | system | 2 |
| 2 | `default`（HTML/Jinja） | default.md | system | 1 |
| 3 | `**/.github/workflows/*.yml` | github-workflows.md | system | 1 |

- **group 1（Python）**：按 python.md 核对——无可变默认参数（`PageParser.__init__` 全为不可变初值）、资源用 `with` 打开、无裸 `except`（`main` 的 `except (AttributeError, ValueError)` 已收敛到具体类型）、无循环内重操作。测试代码按「测试代码」节核对：断言钉死期望值（`extract_entry` 用全等断言、无 `or` 链兜底），无真实网络请求。
- **group 2（HTML/Jinja）**：核对注入面（`{{ blogBase[...] }}` 均为配置派生值，非用户输入）、负向控制（断言不隐藏 Pagefind 结果）。
- **group 3（GitHub Actions）**：核对步骤顺序（子串索引在 pagefind 之前）、脚本路径与执行环境（`/opt/Gmeek` 取脚本 + 系统 `python3`，不依赖 uv）、失败传播（fail-loud）。

## Coverage Detail

| File | Status | Note |
|------|--------|------|
| `scripts/build_search_index.py` | reviewed | 新增生成器；解析器防御性检查通过，Finding 3 |
| `templates/search.html` | reviewed | 容器/挂接/注入/样式；Finding 1 |
| `.github/workflows/Gmeek.yml` | reviewed | 步骤插入位置与执行环境正确；Finding 2 |
| `tests/test_pipeline.py` | reviewed | 新增 12 例；断言有效，未发现弱断言 |

### ADR 边界 / 注释约定（Step 2.7 + 2.8）

- `check_comment_conventions.py <本次 3 个代码文件> --check-refs`：**本次改动零新增违规**；剩余 4 处（`tests/test_pipeline.py` 的 `:195` C2、`:1045`/`:1510`/`:1511` C1）均为 HEAD 既有、超出本次 diff。
- 新增代码内无 ADR 编号或 `docs/adr` 链接；设计意图均以自描述文本表达。

## Follow-Up

1. Finding 1 为一行防御性加固，建议随手补上。
2. Finding 2 建议在 ADR-0027 补记「生成失败即阻断发布」的取舍。
3. Finding 3 记录为已知边界，不改。
4. 本次为**实现后自动触发的审查**，未改动上述代码；如需修复请确认。

## 决策性内容

本次审查**确认**（而非新产生）了 ADR-0027 已记录的两项取舍，无需新落 ADR：

- 只做「标题 + 小节标题」轨、不做正文轨（依据：实测缺口集中在标题短词）。
- 两轨并列展示、不隐藏/不过滤 Pagefind 结果（依据：上游踩过「过滤藏光结果 + 注入被重绘清掉」）。

Finding 2 建议补记的那句取舍，属对 ADR-0027 正文的补充，非新决策。
