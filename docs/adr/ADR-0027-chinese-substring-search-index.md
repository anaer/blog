# ADR-0027：中文短词检索——标题/小节子串索引（轻量双轨）

**状态：** 已接受
**创建时间：** 2026-10-09

> **当前状态 / 核心结论：** 实测确认 Pagefind 对中文「2 字短词」失效（标题内两字词约 1/3 搜不到目标文章），而完整标题 / 小节标题 / 多字词 0% 漏检。结论：只对「标题 + 小节标题」建一条**连续子串**索引（~11KB），检索页把命中结果插在 Pagefind 结果之上并列展示；不做正文轨（成本高一个数量级、收益边际）。下一步为合并后跑一次构建确认线上生效。

---

## 背景

ADR-0007 记录了「Pagefind 的 zh 索引是词级切分，短中文查询可能漏检」这一未解决风险。本次用线上 29 篇真实文章（博客共 163 页，样本 18%）本地重建 Pagefind 1.5.2 索引实测，把该风险量化：

| 查询形态 | 漏检率 | 样本量 |
|---|---|---|
| 完整标题 | 0% | 29 |
| 小节标题 `h2`/`h3` | 0% | 65 |
| 正文高频两字词 → 目标文章 | 12.1% | 107 |
| **标题内两字词 → 目标文章** | **31.5%** | 89 |

漏检的是**真实词**（`入参` / `出参` / `说明` / `常用` / `修改` / `相关` / `导航` / `虚拟`），而 `配置` / `搜索` / `请求头` 正常——**哪些两字词能搜、哪些不能不可预测**，用户无法形成稳定预期。

参考上游社区做法（Pagefind + 自建子串索引双轨）：Pagefind 负责广搜，子串索引负责中文连续短语精确匹配。

## 决策

1. **只建「标题 + 小节标题」子串索引，不建正文轨**：实测缺口集中在标题内短词；正文多字词组 Pagefind 已能命中。只收 `<title>` 与 `h1–h6` 文本，索引体积从「含正文前 800 字」的 ~177KB 降到 **~11KB**（gzip ~4KB），工程量与收益之比最优。
2. **构建期生成，跑在合并后的完整站点上**：新增 `scripts/build_search_index.py`（**仅标准库**，CI 用 `python3` 直跑，不依赖 uv 环境），扫描站点 HTML 中带 `data-pagefind-body` 的页面，抽取标题与小节标题，写 `<site>/search-index/index.json`。CI 中与 pagefind 同位置（`docs`）、顺序在其之前。**不能**在增量构建产物上生成（同 ADR-0007 对 pagefind 的约束）。
3. **运行时按「连续子串」匹配**：检索页懒加载该 JSON（首次查询时 `fetch`），对 `标题 + 小节标题` 做 `indexOf`（大小写不敏感），词长 < 2 不触发；命中数封顶展示。
4. **结果插在 Pagefind 结果之上，用独立容器**：把 `templates/search.html#exactMatches` 注入 `.pagefind-ui__drawer` 内、`.pagefind-ui__results-area` 之前（headless Chrome 实测该位置在 Pagefind 重渲染后**存活**）；`MutationObserver` 兜底重插（按 id 判存在，不循环）。**不隐藏、不过滤 Pagefind 结果**——两轨并列展示。
   - 上游踩过的两个坑：过滤逻辑把 Pagefind 结果藏光；注入节点被重绘清掉。故用独立容器 + 只插入不删除。
5. **挂接点用 PagefindUI 的 `processTerm`**：Pagefind 每次查询前都会调用该回调，无需额外监听输入事件；在回调里触发子串检索与渲染。

不做什么：
- 不做正文轨（成本高一个数量级，边际收益低）。
- 不引入 Web Worker / 分片（~11KB 单文件，主线程 `indexOf` 开销可忽略）。
- 不魔改 Pagefind（需长期跟进上游 + 编译环境依赖，上游实测因环境问题放弃）。
- 不改 Pagefind 的既有配置与结果装饰逻辑（ADR-0021 / ADR-0026）。

## 后果

- **收益**：中文 2 字短词（`入参` / `导航` / `折叠`…）能命中标题/小节标题所在文章；索引仅 ~11KB，构建耗时与体积增量可忽略。
- **代价 / 权衡**：多一个构建步骤与一个索引产物，且**该步骤失败会阻断整个发布**（与 pagefind 步骤同策略：宁可失败可见，也不让精确匹配静默失效）；`processTerm` 挂接依赖该配置项继续存在（属 PagefindUI 公开配置，非内部实现）；`templates/search.html#exactMatches` 的注入依赖 `.pagefind-ui__drawer` / `.pagefind-ui__results-area` 类名（Pagefind 公开类名空间，升级需回归）。
- **未解决风险**：**正文内**的两字词仍可能漏检（本次不做正文轨）——实测 12.1%，且以跨词碎片为主。若后续该档影响明显，再评估加正文轨。

## 实施位置

- 生成器：`scripts/build_search_index.py`
- 构建：`.github/workflows/Gmeek.yml`（pagefind 之前新增一步）
- 检索页：`templates/search.html`（懒加载 + `processTerm` 挂接 + 独立容器 + 注入 + 样式）
- 测试：`tests/test_pipeline.py`

## 验证

- 生成器单测：抽取 `<title>` 与 `h1–h6`；跳过无 `data-pagefind-body` 的页面；无小节标题时 `h` 为空串；输出 JSON 结构与 URL 形态。
- 检索页单测：容器存在且独立于 Pagefind 的渲染根；`processTerm` 挂接；懒加载 URL 经 `homeUrl` 派生；注入目标为 `.pagefind-ui__drawer`。
- 端到端：本地渲染站点 + `build_search_index.py` + 真实索引，headless Chrome 验证「搜索两字词 → 精确匹配块出现在 Pagefind 结果之上且共存」。
- 反证：还原为无子串轨形态 → 目标用例失败。

## 关联文档

- [ADR-0007](ADR-0007-on-site-search-pagefind.md)：本 ADR 补齐其「未解决风险」中记录的短中文查询漏检。
- [ADR-0026](ADR-0026-pagefind-search-performance.md)：本 ADR 与其共用检索页，并在其 `processTerm` / 装饰器挂接面上扩展。

## 下一步

合并后跑一次构建（`workflow_dispatch`），确认线上 `/search-index/index.json` 可加载、两字词能命中标题文章。
