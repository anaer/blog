# ADR-0013：全量重建空产物与 CI 发布安全闸门

**状态：** 已接受
**创建时间：** 2026-10-08

> **当前状态 / 核心结论：** 修复「手动触发即清空线上帖子」的两个叠加缺陷（命令行路由整数/字符串不等、`PaginatedList` 被 `list()` 耗尽后空迭代），并在 `workflow_dispatch` 分支加 CI 发布安全闸门——产物异常或空 `post` 目录时中止覆盖。下一步无需后续动作。

---

## 背景与事故

为实现「清理历史已删除 issue」，上一轮让 `workflow_dispatch` 走 `runAll` 全量重建 + `rm -rf docs` 整体覆盖。手动触发后线上 `post` 目录被整体清空、帖子全部消失。

事故实为**两个缺陷叠加**：

### 缺陷 A（直接推手）：命令行路由整数/字符串不等

`Gmeek.py#main` 的 `--issue_number` argparse 缺省为**整数** `0`，路由却与**字符串** `"0"` 比较：

```python
parser.add_argument("--issue_number", default=0)
elif options.issue_number=="0" or options.issue_number=="":   # 0 == "0" 为 False
    blog.runAll()
else:
    blog.runOne(options.issue_number)                          # → runOne(0)
```

重构 workflow 后，`workflow_dispatch` 分支执行 `Gmeek.py TOKEN REPO`（不再显式传 `--issue_number ''`），缺省整数 `0` 因此被误判为单篇，进入 `runOne(0)` → `get_issue(0)` 404 → 打印「issue #0 不存在(可能已删除)」。`runOne` 只重渲染列表页、不产出任何帖子，`docs/post/` 为空；dispatch 分支随后无条件 `rm -rf docs` + `cp -a` 把这份残缺站点发布，导致线上 `post` 目录被删。（原版 Gmeek 始终显式传 `--issue_number ''`，故从未暴露。）

### 缺陷 B（放大器）：`runAll` 的 PaginatedList 双次迭代

```python
issues=self.repo.get_issues(state="all")
issue_list=list(issues)        # 第一次迭代: 耗尽分页生成器
for issue in issues:           # 第二次迭代: 同一已耗尽对象 → 0 次
    self.addOnePostJson(issue)
```

`list(issues)` 把分页对象读空后，复用的同一对象再次迭代产出 0 个元素，导致 `postListJson` 为空、`cleanFile()` 已清空的 `docs/post/` 无内容回填；随后 CI 的 `rm -rf docs` + `cp -a` 把这份空站点发布了出去。

单元测试用列表型假对象无法暴露该问题（列表可重复迭代），故此前 109 用例全绿却在真实 API 下失败。

## 决策

1. **路由归一化**：新增纯函数 `Gmeek.py#resolve_run_mode(issue_number, prune)`，将 `issue_number` 统一 `str().strip()` 后再判定 `""`/`"0"` → `all`，其余 → `one`，`prune` 优先。`main` 改用该函数路由，根治整数/字符串不等。
2. **修正迭代**：`runAll` 改为迭代已物化的 `issue_list`，并对单条 issue 的 `addOnePostJson` 包 `try/except`，单条失败只跳过不中断整轮重建。
3. **CI 安全闸门**：`workflow_dispatch` 分支在 `rm -rf docs` 之前增加两道校验——构建退出码非 0 即中止；`/opt/Gmeek/docs/post/` 为空或不存在即中止（`::error::` 标注）。确保任何失败/空产物都不会覆盖线上。
4. **回归测试**：`TestResolveRunMode` 固化路由（含整数 `0` 与字符串 `"0"`）；`TestRunAllIteration` 用一次性生成器模拟 `PaginatedList` 行为，断言 `runAll` 仍能收录全部 issue。

## 验证

- `pytest` 116 passed（新增 `TestResolveRunMode` 6 例、`TestRunAllIteration` 1 例）。
- workflow YAML 解析正常，`issues.types` 含 `deleted`，`workflow_dispatch` 校验与中止逻辑就位。

## 恢复步骤（运营侧）

1. 提交本 ADR 与代码修正并推送。
2. 在 Actions 重新手动触发一次 `workflow_dispatch`。
3. 构建会重新渲染全部现存 issue 为帖子（GitHub issue 仍在，内容不丢），`post` 目录恢复。

## 后果

- 安全闸门使「全量重建失败」时不再误删线上，但需人工重跑一次修复后的构建来恢复。
- 单条 issue 异常被跳过：极端情况下个别帖子缺失而不报错，需在构建日志中关注 `skip issue #` 行。

## 下一步

无需后续动作。
