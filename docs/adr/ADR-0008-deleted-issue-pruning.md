# ADR-0008：已删除 issue 从索引与站点剔除

**状态：** 已接受
**创建时间：** 2026-10-08

> **当前状态 / 核心结论：** 删除 issue 不再残留于列表与站点。runOne 捕获 `get_issue` 的 404 视为删除并清理单条索引；新增 `--prune` 全量对账；workflow 增加 `deleted` 事件并让删除自愈、dispatch 走全量重建清理历史残留。下一步合并后跑一次 `workflow_dispatch` 全量重建。

---

## 背景

workflow 仅监听 `issues: [opened, edited]`，删除不触发重建；`blogBase.json` 持久化索引保留已删条目，生成产物 `docs/post/N.html` 也仍在。runOne 直接对不存在的 issue 调 `get_issue` 会抛 404 崩溃。结果：删掉的帖子仍长期出现在列表与站点。

## 决策

1. **删除即清理（单条）**：`Gmeek.py#GMEEK.runOne` 捕获 `github.GithubException`（status 404），改走清理分支——调用 `Gmeek.py#GMEEK.prune_one` 移除该编号的索引条目与 HTML，并重渲染列表/feed/nav/检索页，不再中断构建。
2. **全量对账（一次性）**：新增 `Gmeek.py#GMEEK.prune_stale` 与 `Gmeek.py#main` 的 `--prune` 开关；用 `repo.get_issues(state="all")` 比对索引，删除仓库已不存在（被删）的条目及其 HTML，返回被移除编号列表。
3. **CI 事件与发布语义**：`.github/workflows/Gmeek.yml` 的 issues 类型增加 `deleted`；删除事件委托 runOne（404→清理）并 `rm -f` 已发布 HTML；`workflow_dispatch` 改为全量重建（`runAll`）+ 整体覆盖发布目录，顺带清理残留的已删帖子 HTML。
   - 不做什么：不在 runOne/runLatest 增量路径额外拉取全量 issue 列表（仅在显式 `--prune` 或删除事件触发网络对账）。

## 后果

- **收益：** 删除事件自愈；历史残留可经一次 dispatch 全量重建彻底清除。
- **代价 / 权衡：** 删除事件走完整列表重渲染（廉价，未变文章凭缓存跳过）；`--prune` 与 dispatch 全量重建会多一次 `get_issues` 网络调用。

## 实施位置

- 逻辑：`Gmeek.py#GMEEK.runOne`、`Gmeek.py#GMEEK.prune_one`、`Gmeek.py#GMEEK.prune_stale`、`Gmeek.py#main`
- 构建：`.github/workflows/Gmeek.yml`（issues `deleted` 类型、dispatch 全量覆盖）
- 测试：`tests/test_pipeline.py`（TestDeletedPruning）

## 验证

- `tests/test_pipeline.py` 新增：prune_one 移除条目+HTML+失效导航缓存；runOne 遇 404 不抛异常且清理并重渲染；prune_stale 按实况剔除已删条目。

## 下一步

合并后于 Actions 手动触发一次 `workflow_dispatch`，确认已删帖子从线上列表与 `docs/post/` 消失。
