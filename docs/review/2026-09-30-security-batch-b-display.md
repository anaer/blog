# Security Audit Report: 批次 B — 站点展示一致性

**Mode**: security
**Reviewer**: Qoder agent / 2026-09-30
**Version**: 工作区未提交改动（main@75f7137 + 批次 B）
**Rule config**: `sha256:2bed64cb922060527607cecd5c9b2eb5debd3c2d0727841f1e3294a6ed8604bb`（来源：system）
**Coverage**: 5 reviewed / 5 total / 0 excluded

## Summary

- **Scope**：批次 B 改动的 5 个文件（`Gmeek.py`、`templates/plist.html`、`templates/post.html`、`templates/tag.html`、`tests/test_pipeline.py`）及其运行上下文（博客生成器与模板渲染层）。本批不新增不可信输入入口。
- **Top Issues**：无 critical / high / medium；2 项 Low（1 项为刻意使用说明，1 项为既有实现）。
- **Overall Risk**：Low
- **正面收紧**：① 摘要 `|e` 转义——落地批次 A 安全报告 Finding 3（AI 摘要未转义渲染）的修复；② 标签链接 `|urlencode` 与 tag 页 hash `encodeURIComponent` —— 收窄 URL / hash 注入面。

## Threat Model

同批次 A（无新增组件与信任边界）；本批变化集中于渲染/展示层：

| Component | Trust Boundary | Assets | Top Threats (STRIDE) |
|-----------|---------------|--------|----------------------|
| 模板渲染（`templates/*.html`） | 生成器 ↔ 公开 Internet | 站点内容完整性 | T（内容注入）、I |
| 导航/时间/色标（`Gmeek.py` 纯函数） | —（本地纯计算，无外部输入） | — | 无新增 |

## Findings

| # | Severity | Category | Confidence | Location | Risk | Recommendation |
|---|----------|----------|------------|----------|------|----------------|
| 1 | Low | security | High | `Gmeek.py#deterministic_color` | md5 用于非安全用途（日期色标派生）：无凭证 / 完整性依赖，仅作确定性取样；部分静态扫描器（Bandit B324 类）会标记 | 记录为刻意使用、非缺陷；批次 C（Python 3.12）可加 `usedforsecurity=False` 消音 |
| 2 | Low | security | Medium | `templates/tag.html`（`showList` 中 onclick 拼接，既有实现） | 标签名拼入 onclick 字符串（本批未改该行）；标签仅仓库主可控（外部用户无法为本仓库创建标签），实际风险可忽略 | 无需本批动作；批次 C 可顺带改为 `addEventListener` |

## Input Validation Audit

本批不新增不可信输入入口；既有入口（issue 内容 / 环境变量 / 状态文件）的安全结论沿用批次 A 报告。模板侧渲染路径本批为**收紧**（转义 + 编码）。

## Remediation Plan

### Quick Wins (hours)

- 无必须项（2 项 Low 均为登记或刻意说明）

### Medium Fixes (days)

- 无

### Structural Guardrails (weeks)

- 批次 C：模板渲染层固化「默认转义 + 显式豁免」约定（与批次 A 报告的建议合并执行）

## Dependency CVEs

| Package | Version | CVE | Severity | Reachable | Remediation |
|---------|---------|-----|----------|-----------|-------------|
| （本批未新增依赖） | — | — | — | — | 依赖锁定归批次 C |

## Coverage Detail

| File | Status | Note |
|------|--------|------|
| `Gmeek.py` | reviewed | 纯函数（导航/时间/引用/色标）+ 删除符号无残留调用；无新密钥面 |
| `templates/plist.html` | reviewed | 链接前缀与 urlencode 收紧 |
| `templates/post.html` | reviewed | 摘要转义（修复批次 A Finding 3） |
| `templates/tag.html` | reviewed | hash 编解码收紧；onclick 拼接为既有实现（Finding 2） |
| `tests/test_pipeline.py` | reviewed | 冒烟用例断言转义与编码结果；无真实网络请求 |

## Validation

- [x] 密钥模式扫描：0 命中；密钥打印语句：0 命中
- [x] 摘要转义冒烟测试通过（`&lt;img` 断言）
- [x] 编码冒烟测试通过（`tag.html#C%2B%2B` 断言）
- [x] 批次 A 安全报告 Finding 3（摘要未转义）修复已落地
