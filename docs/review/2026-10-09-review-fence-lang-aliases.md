# Review Report: 围栏语言别名映射（Pygments 不识别语言的等价映射）

**Mode**: review
**Reviewer**: WorkBuddy agent / 2026-10-09
**Scope**: `md2html.py`、`tests/test_pipeline.py`（工作区改动，`git diff HEAD`）
**Rule config**: `sha256:a94011598e4f51a6dcfe56d5df80cf4ef487afc6fcacb5c7144b6925d7c05b23`（来源：system）
**Coverage**: 2 reviewed / 2 total / 0 excluded

## Summary

本次改动为「Pygments 不认识的围栏语言名」建立确定性别名映射：在转换前把围栏 info string 的首个 token 换成等价词法，标签仍显示原文。取代了先前评估的 `guess_lang` 方案（实测自动识别在本站内容上不可靠）。

整体质量：**实现正确、边界处理完整**。发现 **0 critical / 0 high / 0 medium、2 low**，均属测试强度与判断依据的记录问题，不阻塞合并。关键点已逐条复核：

- **围栏状态机**：开/闭围栏判定与既有 `_extract_fence_langs` 同一口径（只比较首个字符），两处不会失配；未闭合围栏不吞后续行（单测覆盖）。
- **只替换首个 token**：`split(None, 1)` 后重组，`title="…"` 等尾部原样保留（单测覆盖）。
- **标签与映射解耦**：`_extract_fence_langs` 读原始文本、`_normalize_fence_langs` 另供高亮，二者共用同一 `md_text`；反证证明去掉映射后标签不变。
- **非围栏文本不受影响**：正文中提及语言名不会被改（单测覆盖）。
- **无 `err` token**：`conf`→`ini` 在 nginx 风格与 ini 风格样本上均为 0 个 `err` token（实测）。
- 全部 11 个映射目标均已在 Pygments 中验证存在（单测守护）。

实测改进：全站 694 块中，有高亮的块 **502 → 575**（+73）。

## Issues

| # | Severity | File:Line | Category | Finding | Recommendation |
|---|----------|-----------|----------|---------|----------------|
| 1 | Low | `tests/test_pipeline.py`（`TestFenceLangAliases.test_aliased_langs_get_highlighted`） | test | 只断言 `token > 0`，**不校验映射目标是否正确**。若把 `conf` 错映射到 `python`，该用例仍会通过（目标存在性由另一条用例守护，但「选得对不对」无人守） | 追加一条断言：被映射块不得出现 `err` token（`class="err"` 计数为 0）。**注意该断言只覆盖「目标词法对内容报错」这一类错映射**（实测 12 组错映射中抓到 4 组），抓不到「能着色但着错」（如 `conf`→`python` 给 13 个 token、0 err）。映射选择本身仍是判断，无法自动化校验 |
| 2 | Low | `md2html.py#Markdown2GithubHtml.FENCE_LANG_ALIASES` | maintainability | 映射目标的选择是**判断**而非事实（尤其 `conf`→`ini`：34 块中 15 ini 风格 / 6 nginx 指令 / 13 其他）。依据写在代码注释里，但无测试可校验该判断，未来改动者缺少回归信号 | 无需改；注释已给出抽样依据与「不误导」的判据。若后续发现 `conf` 误配明显，再按内容重新划分 |

## By Severity

### Critical

无。

### High

无。

### Medium

无。

### Low

- **`tests/test_pipeline.py`** [test] — `test_aliased_langs_get_highlighted` 不校验映射正确性。
  > 建议：补 `assert 'class="err"' not in html`（已应用）。**作用范围有限**：实测 12 组错映射中只抓到 4 组（目标词法对内容报错者，如 `conf`→`json` 产生 11 个 err token）；对「能着色但着错」的错映射无效（`conf`→`python` 给 13 token、0 err，仍通过）。
- **`md2html.py`** [maintainability] — 映射目标是判断，无可自动化校验的回归信号。
  > 建议：不改（注释已记录依据）；如判断被推翻，按内容重划。

## Severity Distribution

- Critical: 0
- High: 0
- Medium: 0
- Low: 2

## Language-Specific Notes

| Rule group | Pattern | Rule file | Source | Files |
|------------|---------|-----------|--------|-------|
| 1 | `**/*.{py,pyi,pyw,ipynb}` | python.md | system | 2 |

- **python.md**：核对可变默认参数（`FENCE_LANG_ALIASES` 为类级**不可变字典常量**，只读不写；`_normalize_fence_langs` 内 `out` 为局部列表）、异常处理（本改动无新增 try/except）、边界（空 info string、未闭合围栏、正文提及语言名均已单测覆盖）、性能（O(行数) 单遍扫描，无循环内重操作）。
- **测试代码**：断言钉死期望值（标签全等断言、token 计数、`_normalize_fence_langs` 输出全等）；无网络请求；无 `or` 链兜底。Finding 1 即此维度的强度不足。

## Coverage Detail

| File | Status | Note |
|------|--------|------|
| `md2html.py` | reviewed | 新增常量与归一化方法 + `convert` 调用点；Finding 2 |
| `tests/test_pipeline.py` | reviewed | 新增 `TestFenceLangAliases` 9 例；Finding 1 |

### ADR 边界 / 注释约定（Step 2.7 + 2.8）

- `check_comment_conventions.py <2 文件> --check-refs`：**本次改动零新增违规**；剩余 4 处均为 HEAD 既有（`tests/test_pipeline.py` 的 `:195` C2、`:1045`/`:1510`/`:1511` C1）。
- 新增注释全部为自描述文本（说明映射依据与实测判据），无 ADR 编号或 `docs/adr` 链接。

## Follow-Up

1. Finding 1 为一行断言加固，建议随手补上。
2. Finding 2 记录不改。
3. 本次为**实现后自动触发的审查**，未改动上述代码；如需修复请确认。

## 决策性内容

本次改动引入一项**判断性设计**，建议由用户拍板是否落 ADR：

- **围栏语言别名映射表**（11 条）——把 Pygments 不认识的站内语言名映射到等价词法，并明确**不采用** `guess_lang`（附实测依据：自动识别 45 块只猜对 5 块）。这是一项会被后续内容长期引用的约定（新文章若用 `conf`/`jinja2` 等写法即受其影响），且含「`conf` 该映射到 ini 还是 nginx」这类取舍。

是否要通过 `design-manager`（adr 模式）沉淀进 ADR 文档？[是 / 仅对话讨论不落盘 / 跳过]
