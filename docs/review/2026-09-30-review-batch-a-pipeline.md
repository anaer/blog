# Review Report: 批次 A — 生成管线正确性（工作区未提交改动）

**Mode**: review
**Reviewer**: Qoder agent / 2026-09-30
**Scope**: 工作区改动 5 个文件（`Gmeek.py`、`Summary.py`、`tests/test_pipeline.py`、`requirements-dev.txt`、`.gitignore`）
**Rule config**: `sha256:2bed64cb922060527607cecd5c9b2eb5debd3c2d0727841f1e3294a6ed8604bb`（来源：system）
**Coverage**: 5 reviewed / 5 total / 0 excluded

## Summary

批次 A 正确性修复（对应 ADR-0001）：全量重建索引（清除已删除/改判条目，未变更文章携带摘要与构建缓存）、收录过滤补 PR 判断、置顶判定改为按最新 pin/unpin 事件（修复线上 issue #6 的取消置顶不生效复现）、摘要失败可重试（≤10/构建）、状态文件瘦身（只落两个索引集合）、可测试化（`__main__` 守卫 + 21 例单测）。

审查未发现 critical / high / medium 问题；发现并清理 1 处 Low（死赋值）。

## Issues

| # | Severity | File:Line | Category | Finding | Recommendation |
|---|----------|-----------|----------|---------|----------------|
| 1 | Low | `Gmeek.py`（`addOnePostJson`） | maintainability | `post["top"]=0` 在所有分支均被覆盖（原实现依赖它作默认值，改为 `resolve_top` 后成为死赋值） | 已删除该行，随批清理并通过 21 例单测回归 |

## By Severity

### Critical

（无）

### High

（无）

### Medium

（无）

### Low

- **`Gmeek.py`（`addOnePostJson`）** [maintainability] — `post["top"]=0` 死赋值，删除后行为不变
  > 已随批清理；`pytest` 21 passed 回归通过。

## Severity Distribution

- Critical: 0
- High: 0
- Medium: 0
- Low: 1（已清理）

## Language-Specific Notes

| Rule group | Pattern | Rule file | Source | Files |
|------------|---------|-----------|--------|-------|
| 1 | `**/*.{py,pyi,pyw,ipynb}` | python.md | system | 3 |
| 2 | `default` | default.md | system | 2 |

Python 专项结论：

- **边界与异常**：`resolve_top` 对空事件列表有守卫；`carry_cache` 对 None / 缺键防御完整；`resolve_regen_mode` 覆盖预算耗尽与未配置两种短路
- **测试质量**：21 例均钉死期望值，含 4 组负向控制（#6 场景 pinned→unpinned 判 0、事件乱序不变、PR 排除、预算耗尽不再重试）；无真实网络请求
- **注释约定**：`check_comment_conventions.py --check-refs` 通过；ADR 编号/链接泄漏扫描 0 命中（Step 2.7）
- **已知取舍**（非缺陷）：置顶判定由「首事件短路」改为「全事件扫描」，事件多页的 issue 会多 1–2 次 API 调用；API 成本优化已登记为 ADR-0001 延后项
- **安全快检**：无新增外部输入拼接、无敏感信息落日志（正式结论见 security 报告）

## Coverage Detail

| File | Status | Note |
|------|--------|------|
| `Gmeek.py` | reviewed | 索引重建 / 收录过滤 / 置顶判定 / 缓存与重试门控 / 落盘 / main 入口 全量审 |
| `Summary.py` | reviewed | 返回语义（未配置 None / 失败空串）与配置探测函数 |
| `tests/test_pipeline.py` | reviewed | 21 例，含负向控制与 get_cached 覆盖 |
| `requirements-dev.txt` | reviewed | `-r requirements.txt` + pytest，无版本漂移风险（锁版本归批次 C） |
| `.gitignore` | reviewed | 新增 `.pytest_cache` |

## Follow-Up

- 批次 B/C 的剩余计划已由 ADR-0002 / ADR-0003 覆盖，无阻塞项
- 观察项（非本批缺陷）：摘要 / HTML 缓存键未含渲染器版本；批次 C 重构 md2html 时需评估缓存失效策略，避免历史文章沿用旧渲染结果
