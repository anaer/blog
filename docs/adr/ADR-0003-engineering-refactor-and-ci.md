# ADR-0003：工程化基线——模块化重构、测试与 CI 硬化

**状态：** 提议中
**创建时间：** 2026-09-30

> **当前状态 / 核心结论：** 已定下工程化三目标——可测试（分层重构 + main() 入口 + 单测）、可复现（锁依赖 + Python 3.12）、可守护（CI 检查 job + workflow 硬化 + 文档重写）；作为批次 A/B 修复后的独立批次执行，下一步进入 design 模式规划。

---

## 背景

仓库为「main 存代码与配置、blog 存生成产物」的双分支结构，Actions 每次直接克隆 main 的代码运行——main 一旦不可运行，博客构建即中断，但 main 目前没有任何 CI 校验。现状：`Gmeek.py` 模块级即执行（argparse 与运行在 import 期）不可测试，无任何单测与 lint；依赖未锁版本、CI 钉已 EOL 的 Python 3.8；workflow 权限为 write-all、无并发控制（连续事件触发的两次运行竞态，后 push 者失败被静默吞掉）、个别三方 action 未固定到不可变版本；README/CONFIG 仍是上游 Gmeek 的安装说明，与真实架构漂移。

## 决策

1. **模块化重构**：按职责分层（配置 / 抓取 / 生成 / 渲染 / RSS / 状态），`Gmeek.py` 保留为编排入口，抽出 `main()` 与 `__main__` 守卫；重构以既有行为为基线，不夹带行为变更（批次 A/B 已定的变更除外）。
2. **测试与检查**：对纯函数（标题规范化、导航相邻计算、时间换算、文章尾配置解析、缓存携带规则）建 pytest 用例；CI 增加检查 job（编译 + 单测），在 main 分支 push 时运行。
3. **版本与依赖**：使用 uv 管理——`pyproject.toml` 声明（含版本下限）为唯一来源、`uv.lock` 锁定全部传递依赖；CI 以 `uv sync --frozen` 安装、`uv run --frozen` 运行；Python 3.12（`requires-python >=3.12` + `.python-version`）；依赖升级后先本地跑通单测与全量构建再合入。
4. **workflow 硬化**：补齐 issues 事件类型（labeled/unlabeled/closed/reopened/deleted/pinned/unpinned）并处理删除触发的清理；加 concurrency（同组串行、不互相取消）；push 产物前先 rebase 重试；三方 action 固定到不可变版本；权限收紧到最小集。
5. **文档与仓库卫生**：README/CONFIG 重写为本仓库真实架构（分支职责、事件流、secrets、本地开发方式）；`.gitignore` 忽略生成产物（`docs/` 下生成内容、`backup/`、`blogBase.json`，按目录白名单保留 `docs/adr/`、`docs/glossary/` 与 `docs/review/`）；生成器的清理逻辑（`Gmeek.py#GMEEK.cleanFile`）同步改为只清理生成产物、保留这三个目录；清理死代码（`markdown2html`、`runLatest`、摘要模块演示代码）并收拢摘要 prompt 与输入截断。
   - 不做什么：不换静态托管方案、不改模板体系、不引入数据库或服务端。

## 后果

- **收益：** main 任何提交先过编译与单测；构建产物确定可复现；文档与真实架构一致；连续事件不互相覆盖。
- **代价 / 权衡：** 完整重构会产生一次性的大 diff，需以行为基线测试作护栏；Python 3.12 下的时间 API 废弃项随批次 A 的时间改造一并处理。
- **未解决风险：** `delete-workflow-runs` 等三方 action 固定版本后的行为需观察一个发布周期。

## 实施位置

- 入口与编排：`Gmeek.py`（模块级执行 → `main()` 入口）
- 渲染与摘要：`md2html.py#Markdown2GithubHtml`、`Summary.py#generate_summary`
- workflow 与文档：`.github/workflows/Gmeek.yml`、`README.md`、`CONFIG.md`、`.gitignore`
- 依赖与版本：`pyproject.toml`、`uv.lock`、`.python-version`（uv 管理，替代 requirements*.txt）

## 验证

- 待实施后：main push 触发检查 job 且全绿；模拟连续两次 issue 事件验证 concurrency 无覆盖；Python 3.12 下本地跑通全量构建。

## 下一步

进入 design 模式，规划重构分层与实施顺序（批次 C，在 A/B 之后）。
