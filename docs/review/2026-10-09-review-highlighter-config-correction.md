# Review Report: 高亮配置清理（更正版）

**Mode**: review
**Reviewer**: WorkBuddy agent / 2026-10-09
**Scope**: `md2html.py`、`tests/test_pipeline.py`（工作区改动，`git diff HEAD`）
**Rule config**: `sha256:a94011598e4f51a6dcfe56d5df80cf4ef487afc6fcacb5c7144b6925d7c05b23`（来源：system）
**Coverage**: 2 reviewed / 2 total / 0 excluded

> **本报告取代** `2026-10-09-review-codehilite-cleanup.md`——那份报告基于 40 篇抽样，漏掉了缩进代码块这一低频用法，得出了错误结论（详见「更正」节）。

## Summary

最终落地的清理范围：**移除 `pygments_style: monokai`（实测无效）与 `fenced_code` 扩展（实测冗余）；保留 `codehilite` 扩展及其 `css_class: highlight`**。

整体质量：**改动等价、守卫到位**。0 critical / 0 high / 0 medium / 0 low。

- **等价性**：219 篇源文章在改动前后**逐字节一致**。
- **守卫测试**：4 条，含 2 条针对真实风险（缩进块高亮、`css_class` 一致性），反证均成立。
- 全量 `250 passed`。

## 更正

前一份报告的核心前提「`codehilite` 扩展及其配置块对输出零影响」**不成立**。逐项复核（全量 219 篇）结果：

| 对象 | 实测差异篇数 | 结论 |
|---|---|---|
| `pygments_style`（含改成 `default`/`friendly`/`github-dark`） | **0** | **确实无效** → 移除 |
| `linenums` / `wrapcode` / `use_pygments` | 0 | 与默认一致 → 可留（表达意图） |
| **`css_class: highlight`** | **2** | **有效** → 必须保留 |
| **`codehilite` 扩展** | **2** | **有效** → 必须保留 |
| `fenced_code` 扩展 | 0 | 冗余 → 移除 |

**根因**：站内有**缩进代码块**（4 空格缩进、无围栏，35 行 → 9 个块，集中在 `28-Git配置文件说明.md` 与 `60-pm2常用命令.md`）。`pymdownx.highlight` **只处理围栏块**，缩进块由 `codehilite` 处理；`css_class` 则决定这些块能否套上 `assets/highlight.css` 的配色。删掉任一项，这些块会**静默失去高亮**（无报错、无日志）——`60-pm2常用命令.md` 单篇掉 345 个 token。

**漏检原因**：前次验证只跑了 40 篇抽样，恰好不含缩进代码块。**教训：删除式改动的回归验证必须跑全量语料。**

## Issues

无 critical / high / medium / low。

审查中主动核对的两点：

1. **`codehilite` 是否为遗留冗余** —— 曾据此删除，全量复核后确认**不是**，已恢复（见「更正」）。
2. **守卫测试断言定位** —— 前一份报告记录的 low（`<div class="highlight">.*?</div>` 被内层 `</div>` 截断）已修，现断言基于 `<pre>`。

## Severity Distribution

- Critical: 0
- High: 0
- Medium: 0
- Low: 0

## Language-Specific Notes

| Rule group | Pattern | Rule file | Source | Files |
|------------|---------|-----------|--------|-------|
| 1 | `**/*.{py,pyi,pyw,ipynb}` | python.md | system | 2 |

- **python.md**：本次为删除式改动，按「删除前验证」执行——① 全仓无对 `fenced_code` 的引用；② 全量测试通过；③ **219 篇全量**逐字节比对。无可变默认参数、异常处理、资源管理改动。
- **测试代码**：新增 4 条守卫用例，每条均经反证（去掉被守护的配置项 → 用例失败）。

## Coverage Detail

| File | Status | Note |
|------|--------|------|
| `md2html.py` | reviewed | 移除 `pygments_style` 与 `fenced_code`；保留 `codehilite` + `css_class` |
| `tests/test_pipeline.py` | reviewed | `TestHighlighterStack` 4 例 |

### ADR 边界 / 注释约定（Step 2.7 + 2.8）

- `check_comment_conventions.py md2html.py --check-refs`：**通过**。
- 新增注释为自描述文本，说明「两条高亮路径各管一类代码块」这一非显而易见的事实，无 ADR 编号或 `docs/adr` 链接。

## Follow-Up

无需后续动作。

## 决策性内容

本次改动**确认**了一项非显而易见的设计事实，建议是否沉淀：

- **站内并存两条高亮路径**：`pymdownx.highlight`（围栏块）+ `codehilite`（缩进块），后者靠 `css_class: highlight` 对齐同一套 CSS。这是「两条路径缺一不可」的约定，且**没有任何报错会提示违反它**（删错只会静默丢高亮）——正是这次踩坑的原因。

是否要通过 `design-manager`（adr 模式）沉淀进 ADR？[是 / 仅对话讨论不落盘 / 跳过]
