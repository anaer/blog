# Review Report: 批次 B — 站点展示一致性（工作区改动）

**Mode**: review
**Reviewer**: Qoder agent / 2026-09-30
**Scope**: 工作区改动 5 个文件（`Gmeek.py`、`templates/plist.html`、`templates/post.html`、`templates/tag.html`、`tests/test_pipeline.py`）
**Rule config**: `sha256:2bed64cb922060527607cecd5c9b2eb5debd3c2d0727841f1e3294a6ed8604bb`（来源：system）
**Coverage**: 5 reviewed / 5 total / 0 excluded

## Summary

批次 B（对应 ADR-0002）：导航统一为「上一篇=更早 / 下一篇=更晚、首末隐藏、去随机」（纯时间序，含已关闭文章、忽略置顶，单页不参与）；时间统一 UTC+8（epoch 采集改 `calendar.timegm`，列表日期与文章页时间一致）；`#号` 引用替换跳过围栏与行内代码；日期色标改确定性派生（md5）；单页 `postUrl` 与 RSS 链接修复；摘要转义 / 高亮判定 / tag 页 hash 编码。实现删除了 3 个旧符号，ADR-0002 实施位置锚点已按「代码为准」同步更新（复核 0 硬失败）。

审查未发现 critical / high / medium 问题；1 项 Low（导航查找复杂度，规模下可忽略）。

## Issues

| # | Severity | File:Line | Category | Finding | Recommendation |
|---|----------|-----------|----------|---------|----------------|
| 1 | Low | `Gmeek.py`（`nav_neighbors`） | performance | 每帖渲染对导航序列做一次 `list.index()`（O(n)），全量渲染整体 O(n²)；当前 ~200 篇规模下实测量级可忽略 | 不阻塞；批次 C 重构时可改为预生成 `{编号: 相邻项}` 索引映射 |

## By Severity

### Critical

（无）

### High

（无）

### Medium

（无）

### Low

- **`Gmeek.py`（`nav_neighbors`）** [performance] — 每次渲染一篇文章做一次线性查找；`nav_keys` 已做构建期缓存，剩余成本仅查找本身
  > 批次 C 重构时顺带优化，本批不需要动作。

## Severity Distribution

- Critical: 0
- High: 0
- Medium: 0
- Low: 1

## Language-Specific Notes

| Rule group | Pattern | Rule file | Source | Files |
|------------|---------|-----------|--------|-------|
| 1 | `**/*.{py,pyi,pyw,ipynb}` | python.md | system | 2 |
| 2 | `default` | default.md | system | 3 |

Python / 模板专项结论：

- **正确性**：`replace_issue_refs` 对围栏（``` / ~~~）与行内代码（反引号分段）均跳过，负向用例覆盖「代码块内 `#N` 不替换」；`nav_neighbors` 端点与缺失编号有守卫；`createPostHtml` 显式清除残留 prev/next 键（负向用例覆盖）
- **测试质量**：新增 22 例（总 43），均钉死期望值；含 6 组负向控制（置顶/关闭不干扰导航、代码块不替换、残留键清除、跨日日期不得取 UTC、预算/缓存控制沿用）；模板冒烟覆盖转义与 urlencode 编码结果
- **一致性**：删除符号（`get_prev_post`/`get_next_post`/`get_background_color`）全仓无残留调用；`random` 依赖已移除；`time`/`re` 等保留导入均有实际使用
- **注释约定**：`check_comment_conventions.py --check-refs` 通过；ADR 编号/链接泄漏扫描 0 命中（Step 2.7）

## Coverage Detail

| File | Status | Note |
|------|--------|------|
| `Gmeek.py` | reviewed | 新增 6 个纯函数 + 删除 3 个旧方法；导航/时间/引用/色标/单页 URL 全量审 |
| `templates/plist.html` | reviewed | 单页入口 homeUrl 前缀；标签链接 urlencode |
| `templates/post.html` | reviewed | 摘要转义；标签链接 urlencode |
| `templates/tag.html` | reviewed | hash encode/decode（含搜索框） |
| `tests/test_pipeline.py` | reviewed | 43 例，含模板冒烟与 `createPostHtml` 接线测试 |

## Follow-Up

- 批次 C 计划已由 ADR-0003 覆盖；无阻塞项
- 观察项（沿用批次 A 登记）：摘要 / HTML 缓存键未含渲染器版本，批次 C 重构 md2html 时评估缓存失效策略
- 一次性可见变化（预期内、非缺陷）：全站上下篇方向翻转、晚间文章列表日期 +1 天、色标换新后固定
