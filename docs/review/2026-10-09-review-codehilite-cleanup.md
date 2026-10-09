# Review Report: 清理失效的高亮配置（codehilite）

> ## ⚠️ 本报告结论已被推翻（2026-10-09 后续复核）
>
> 本报告的核心前提「`codehilite` 扩展及其配置块对输出零影响」**是错的**。
> 验证只跑了 40 篇抽样，恰好不含**缩进代码块**（4 空格缩进、无围栏）——而 `codehilite` 正是负责这类块的：
> `pymdownx.highlight` 只处理围栏块。全量 219 篇复核后确认，删掉 `codehilite` 或 `css_class` 会让
> 2 篇文章的 9 个缩进块**静默失去高亮**（单篇掉 345 个 token）。
>
> 处置：已恢复 `codehilite` 与 `css_class: highlight`，只移除真正无效的 `pygments_style` 与冗余的 `fenced_code`。
> 更正后的审查见 `2026-10-09-review-highlighter-config-correction.md`。
>
> **教训**：删除式改动的回归验证必须跑**全量语料**，抽样会漏掉低频用法。

**Mode**: review
**Reviewer**: WorkBuddy agent / 2026-10-09
**Scope**: `md2html.py`、`tests/test_pipeline.py`（工作区改动，`git diff HEAD`）
**Rule config**: `sha256:a94011598e4f51a6dcfe56d5df80cf4ef487afc6fcacb5c7144b6925d7c05b23`（来源：system）
**Coverage**: 2 reviewed / 2 total / 0 excluded

## Summary

本次改动移除 `codehilite` 扩展及其整个配置块——经实测它们对渲染输出**零影响**（实际生效的是 `pymdownx.highlight` 经 `superfences`），原 `pygments_style: monokai` 属误导性死配置。同时新增 2 条守卫测试。

整体质量：**改动安全、验证充分**。发现 **0 critical / 0 high / 0 medium、1 low**（审查过程中发现并已修复）。关键点：

- **删除前验证**：40 篇真实文章 + 一份覆盖表格/emoji/删除线/脚注/引用内围栏/嵌套列表的丰富文档，清理前后输出**逐字节一致**；逐项拆解 5 个配置项，单独去掉任一项输出均不变，去掉扩展本身亦不变。
- **守卫测试有效**：`test_codehilite_extension_absent` 反证成立（恢复扩展即失败）；`test_tokens_use_classes_not_inline_styles` 反证成立（`noclasses` 模式下 Pygments 产出 `<pre style="line-height: 125%;">`，被抓住）。
- 全量 `248 passed`。

## Issues

| # | Severity | File:Line | Category | Finding | Recommendation |
|---|----------|-----------|----------|---------|----------------|
| 1 | Low | `tests/test_pipeline.py`（`TestHighlighterStack`） | test | 该用例**初版有两个缺陷**，审查中已修复：①`assert "style=" not in html` 对整个渲染输出断言，会被模板其他位置的内联样式误伤；②改用 `<div class="highlight">.*?</div>` 后仍失效——`.highlight` 是**外层**容器（项目自己的 `.code-block-wrapper` 在其内），非贪婪匹配被内层 `</div>` 截断，断言对象只含控件不含代码 | 已改为定位 `<pre>` 并同时断言**标签属性**与**内容体**（`noclasses` 的内联样式出现在 `<pre>` 标签上，只看内容体会漏） |

## By Severity

### Critical

无。

### High

无。

### Medium

无。

### Low

- **`tests/test_pipeline.py`** [test] — 守卫用例初版断言范围/定位有误，已修复（见上表）。
  > 修复后反证成立：`noclasses` 模式产出 `<pre style="line-height: 125%;">` → 用例失败。

## Severity Distribution

- Critical: 0
- High: 0
- Medium: 0
- Low: 1

## Language-Specific Notes

| Rule group | Pattern | Rule file | Source | Files |
|------------|---------|-----------|--------|-------|
| 1 | `**/*.{py,pyi,pyw,ipynb}` | python.md | system | 2 |

- **python.md**：本次为**删除式改动**，按「删除前验证」三步执行——① 全仓无对 `codehilite` 的引用（仅 `md2html.py` 自身）；② 全量测试通过；③ 40 篇真实文章 + 丰富文档输出逐字节比对。无可变默认参数、无异常处理、无资源管理改动。
- **测试代码**：Finding 1 即此维度的问题（断言定位不准），已修。

## Coverage Detail

| File | Status | Note |
|------|--------|------|
| `md2html.py` | reviewed | 移除 `codehilite` 扩展与 `extension_configs`；补注释说明高亮栈 |
| `tests/test_pipeline.py` | reviewed | 新增 `TestHighlighterStack` 2 例；Finding 1 |

### ADR 边界 / 注释约定（Step 2.7 + 2.8）

- `check_comment_conventions.py md2html.py --check-refs`：**通过**（检查 1 个文件）。
- 新增注释为自描述文本（说明高亮栈与配色来源），无 ADR 编号或 `docs/adr` 链接。

## Follow-Up

1. Finding 1 已在审查过程中修复，无需后续动作。
2. **附带发现（未改动）**：`fenced_code` 同样已被 `superfences` 覆盖（实测冗余）。属另一处清理，未纳入本次——如需一并去掉请确认。

## 决策性内容

本次改动**不产生**新决策：它是把既有的「高亮由 `pymdownx.highlight` 完成、配色来自 `assets/highlight.css`」这一事实**落实为代码**（删除与之矛盾的死配置），并把它钉进测试。相关决策已在 ADR-0011（代码块语言标签）、ADR-0028（围栏语言别名映射）中记录，无需新落 ADR。
