# ADR-0013: 全量重建空产物与 CI 发布安全闸门

- **状态**: 已接受
- **日期**: 2026-10-08
- **相关**: ADR-0008（已删除 issue 清理）、`Gmeek.py#runAll`、`Gmeek.py#prune_stale`、`.github/workflows/Gmeek.yml`

## 背景与事故

为实现「清理历史已删除 issue」，上一轮让 `workflow_dispatch` 走 `runAll` 全量重建 + `rm -rf docs` 整体覆盖。手动触发后线上 `post` 目录被整体清空、帖子全部消失。

根因：`runAll` 中存在 PyGithub `PaginatedList` 双次迭代陷阱：

```python
issues=self.repo.get_issues(state="all")
issue_list=list(issues)        # 第一次迭代: 耗尽分页生成器
for issue in issues:           # 第二次迭代: 同一已耗尽对象 → 0 次
    self.addOnePostJson(issue)
```

`list(issues)` 把分页对象读空后，复用的同一对象再次迭代产出 0 个元素，导致 `postListJson` 为空、`cleanFile()` 已清空的 `docs/post/` 无内容回填；随后 CI 的 `rm -rf docs` + `cp -a` 把这份空站点发布了出去。

单元测试用列表型假对象无法暴露该问题（列表可重复迭代），故此前 109 用例全绿却在真实 API 下失败。

## 决策

1. **修正迭代**：`runAll` 改为迭代已物化的 `issue_list`，并对单条 issue 的 `addOnePostJson` 包 `try/except`，单条失败只跳过不中断整轮重建。
2. **CI 安全闸门**：`workflow_dispatch` 分支在 `rm -rf docs` 之前增加两道校验——构建退出码非 0 即中止；`/opt/Gmeek/docs/post/` 为空或不存在即中止（`::error::` 标注）。确保任何失败/空产物都不会覆盖线上。
3. **回归测试**：`tests/test_pipeline.py#TestRunAllIteration` 用一次性生成器模拟 `PaginatedList` 行为，断言 `runAll` 仍能收录全部 issue，固化该陷阱不再复发。

## 验证

- `pytest` 110 passed（新增 `TestRunAllIteration` 1 例）。
- workflow YAML 解析正常，`issues.types` 含 `deleted`，`workflow_dispatch` 校验与中止逻辑就位。

## 恢复步骤（运营侧）

1. 提交本 ADR 与代码修正并推送。
2. 在 Actions 重新手动触发一次 `workflow_dispatch`。
3. 构建会重新渲染全部现存 issue 为帖子（GitHub issue 仍在，内容不丢），`post` 目录恢复。

## 代价与权衡

- 安全闸门使「全量重建失败」时不再误删线上，但需人工重跑一次修复后的构建来恢复。
- 单条 issue 异常被跳过：极端情况下个别帖子缺失而不报错，需在构建日志中关注 `skip issue #` 行。
