# Staged/Workspace Review: oneko 列表页收敛 + 列表项 issue 入口

**日期**: 2026-10-09
**范围**: 工作区 diff（5 文件，排除预存在的 icon fill 修复）
**规则配置**: sha256:2bed64cb922060527607cecd5c9b2eb5debd3c2d0727841f1e3294a6ed8604bb

---

## 审查范围

| 文件 | 状态 | 改动摘要 |
|------|------|----------|
| `templates/base.html` | modified | 移除 oneko 全站加载 |
| `templates/plist.html` | modified | 新增 `.list-issue-link` CSS、issue 入口、oneko script 块 |
| `tests/test_pipeline.py` | modified | 新增 `TestOnekoListPageOnly`（3 项）、`TestListItemIssueEntry`（4 项） |
| `docs/adr/ADR-0023-oneko-list-page-only.md` | untracked | oneko 仅列表页 ADR |
| `docs/adr/ADR-0024-list-item-issue-entry.md` | untracked | 列表项 issue 入口 ADR |

**排除**: `CHANGELOG.md`、`docs/adr/ADR-0014-icon-registry-single-source.md`、`templates/base.html` 中的 CSS fill 修复、`tests/test_pipeline.py` 中的 `TestIconFillOverride`——均为预存在的 icon fill 修复改动，与本次任务无关。

---

## 评审结论

### Critical
无

### High
无

### Medium
无

### Low
无

---

## 逐文件审查记录

### templates/base.html
- oneko `<script>` 移除干净，无残留
- 预存在的 CSS fill 修复改动已排除（非本次范围）

### templates/plist.html
- `.list-issue-link` CSS：使用 `--fgColor-muted` 主题变量，窄屏适配，hover 提亮——符合 ADR-0024 视觉决策
- issue 入口：`<object>` 包裹规避嵌套 `<a>`，与文件内既有模式一致；`rel="noopener"` 安全属性齐全
- oneko script 块：位置正确（`{% block script %}` 在 body 结束后，`document.body` 仍可访问）

### tests/test_pipeline.py
- `TestOnekoListPageOnly`：正向（plist 有 oneko）+ 负向（base/post/tag/search 无 oneko）覆盖完整
- `TestListItemIssueEntry`：正向（链接存在、href 正确、`<object>` 包裹）+ 负向（post/search 无该入口）覆盖完整
- 断言无恒真漏洞，负向控制钉死关键行为

### docs/adr/ADR-0023 / ADR-0024
- 状态、TL;DR、决策、实施位置均符合 ADR 写作契约
- 链接校验通过（24 篇 ADR、0 单向、0 坏链）

---

## 覆盖率

- 深审: 5 / 5 文件
- 批量校验: 0
- 排除: 2 文件（预存在的 icon fill 修复）

## 结论

✅ **Commit** — 暂存区内容可安全提交

- 无 Critical/High/Medium 问题
- 代码与测试均通过（201 passed）
- ADR 文档与代码事实一致
