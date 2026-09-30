# Security Audit Report: 批次 A — 生成管线正确性

**Mode**: security
**Reviewer**: Qoder agent / 2026-09-30
**Version**: 工作区未提交改动（main@b4dacb5 + 批次 A）
**Rule config**: `sha256:2bed64cb922060527607cecd5c9b2eb5debd3c2d0727841f1e3294a6ed8604bb`（来源：system）
**Coverage**: 5 reviewed / 5 total / 0 excluded

## Summary

- **Scope**：批次 A 改动的 5 个文件（`Gmeek.py`、`Summary.py`、`tests/test_pipeline.py`、`requirements-dev.txt`、`.gitignore`）及其运行上下文——GitHub Actions 事件驱动的静态博客生成器（读本仓库 Issues → 渲染 HTML → 写 `docs/` 并提交到 blog 分支；AI 摘要调用外部 LLM API）。排除：工作流文件、模板、`md2html.py`（非本批改动）。
- **Top Issues**：无 critical / high / medium。登记 2 项 Low（均为既有或计划内事项，本批未引入新风险）。
- **Overall Risk**：Low
- **Language Rule Groups**：`**/*.{py,pyi,pyw,ipynb}` -> `python.md` (system)；`default` -> `default.md` (system)

## Threat Model

| Component | Trust Boundary | Assets | Top Threats (STRIDE) |
|-----------|---------------|--------|----------------------|
| Actions 工作流（`Gmeek.py`） | GitHub API ↔ 生成器（issue 仅限仓库主撰写） | `GITHUB_TOKEN`（repo 写权限） | T（不可信内容进入站点）、I（密钥泄露）、D（API 配额耗尽） |
| `Summary.py`（LLM 调用） | 生成器 ↔ 外部 LLM API | `API_KEY` | I（密钥外泄）、D（重试放大） |
| 发布产物（`docs/` → Pages） | 生成器 ↔ 公开 Internet | 站点内容完整性 | T（意外内容）、I（展示个人信息） |

**本批的安全侧变化（均为收紧方向）**：

1. 收录过滤新增 PR 排除——此前仓库主自己提交的 PR 会被当作文章收录并公开；现收紧（`Gmeek.py#GMEEK.addOnePostJson` → `should_include_issue`）。
2. 摘要重试新增 ≤10/构建上限——限制异常场景下对外部 API 的调用放大（DoS 面收敛，`Gmeek.py#resolve_regen_mode`）。
3. 状态落盘瘦身——`blogBase.json` 不再持久化展示态字段，落盘数据面减小（`Gmeek.py#slim_state`）。

## Input Validation Audit

### Entry Inventory

| 入口 | 类型 | 风险点 |
|------|------|--------|
| CLI（`Gmeek.py#main`） | 外部（argv） | `github_token` 经命令行传入（既有设计，见 Finding 2）；`issue_number` 经 `int()` 解析后才使用 |
| Issue 内容（body / title / labels / events） | 外部（GitHub API，owner 限定） | 文件名由 `normalize_title` 过滤非法字符（既有控制）；正文渲染为 HTML 属产品功能 |
| 环境变量（`API_URL` / `API_KEY` / `API_MODEL`） | 外部（环境） | 密钥不落盘、不打印；`summary_configured` 无「非空默认值架空守卫」问题（对照 secrets-hygiene fail-open 检查） |
| `blogBase.json`（恢复状态） | 文件（生成器自产） | 瘦身后仍向后兼容读取；缓存携带仅在 `updatedAt` 匹配时生效（不吸收过期数据） |

### Enforcement Location

- 收录边界：`should_include_issue`（owner + 非 PR，统一入口）
- 缓存边界：`carry_cache`（仅认 `updatedAt` 一致的旧条目）
- 重试边界：`resolve_regen_mode` + 每构建预算（`MAX_DESC_RETRY`）

### Test Cases（tests/test_pipeline.py，21 例）

1. owner 普通 issue → 收录；PR / 非 owner / 幽灵用户 → 拒绝（负向控制）
2. `pinned→unpinned` 序列 → 判 0（线上 #6 场景负向控制）；事件乱序结果不变
3. 预算耗尽 / API 未配置 → 不重试；变更帖子 → 不携带旧缓存（负向控制）

### Findings

| # | Severity | Category | Confidence | Location | Risk | Reproduction | Recommendation | Verification |
|---|----------|----------|------------|----------|------|-------------|---------------|-------------|
| 1 | Low | security | High | `Summary.py#generate_summary` 失败分支 | 上游错误响应体（`response.text`）打印进 Actions 日志；不含本地密钥，但会回显上游细节 | 令 API 返回非 200，观察工作流日志 | 既有行为（非本批引入）；建议后续截断/仅保留状态码与错误码，归入批次 C 清理 | 触发一次失败请求看日志 |
| 2 | Low | security | Medium | `Gmeek.py#main`（argv 传 token） | `GITHUB_TOKEN` 经命令行参数传入：Actions 环境内仅同 runner 进程可见，风险低；本地运行会留 shell 历史 | `ps` / shell history | 既有设计（上游沿用）；可选硬化：改从环境变量读取（需同步改 workflow），非本批范围 | 硬化后 `ps` 不再可见 |
| 3 | Low | documentation | High | `templates/post.html`（非本批改动，计划内） | AI 摘要未转义直接渲染（Jinja 环境未启用 autoescape）；LLM 输出含 HTML 标签时会被渲染。单作者 + 自建 LLM 场景风险低 | 构造含 HTML 的摘要文本 | 已登记修复：批次 B（ADR-0002 决策 5「AI 摘要按纯文本转义输出」） | 批次 B 验收时断言转义生效 |

## Remediation Plan

### Quick Wins (hours)

- Finding 1：`Summary.py` 失败日志只保留状态码（改为 `response.status_code` + 截断后文本），随批次 C 摘要模块清理一并处理

### Medium Fixes (days)

- 无

### Structural Guardrails (weeks)

- 密钥管理文档化：`GITHUB_TOKEN` 由 Actions 自动签发/轮换；`API_KEY` 走 GitHub Secrets 注入——轮换流程写入重写后的 CONFIG 文档（批次 C）
- 站点内容渲染的转义策略（描述字段）随批次 B 落地后，建议在批次 C 为模板渲染层固化「默认转义 + 显式豁免」约定

## Dependency CVEs

| Package | Version | CVE | Severity | Reachable | Remediation |
|---------|---------|-----|----------|-----------|-------------|
| pytest（本批新增） | 未锁定（dev-only，不进入运行/部署链） | 未发现相关高危 CVE | — | No（仅本地/CI 开发环节） | 依赖锁定统一归批次 C |

## Coverage Detail

| File | Status | Note |
|------|--------|------|
| `Gmeek.py` | reviewed | 密钥处理（无打印/无落盘）、收录边界、缓存边界、重试边界、文件写入路径（沿用既有 normalize_title 控制） |
| `Summary.py` | reviewed | 密钥来自环境变量、无落盘；失败分支日志为既有行为（Finding 1） |
| `tests/test_pipeline.py` | reviewed | 无真实网络请求、无凭据引用 |
| `requirements-dev.txt` | reviewed | 仅引入 pytest（dev） |
| `.gitignore` | reviewed | 新增 `.pytest_cache`（防止缓存目录被提交） |

## Validation

- [x] 密钥模式扫描（ghp_/sk-/AKIA/私钥等）：0 命中
- [x] 密钥打印语句扫描：0 命中
- [x] 负向控制用例覆盖安全相关边界（PR 排除、预算收敛）
- [ ] Finding 3 的转义验收：待批次 B
