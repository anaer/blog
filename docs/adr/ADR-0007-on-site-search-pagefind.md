# ADR-0007：站内检索——构建期生成索引 + 静态检索页

**状态：** 已接受
**创建时间：** 2026-09-30

> **当前状态 / 核心结论：** 首页搜索框不再跳转 GitHub Issue 搜索，改为提交到站内检索页 `/search.html`（`?q=`）；检索数据由构建期 Pagefind 扫描生成产物目录得到，只索引文章页正文容器。站点语言经 `<html lang>` 交给索引分词与界面本地化，结果链接按 `homeUrl` 补全子路径。下一步为合并后跑一次构建，确认线上检索可用。

---

## 背景

列表页搜索框原为 `action="{{ blogBase['issuesUrl'] }}"` + `target="_blank"`，提交后在新标签页打开 GitHub Issue 列表的搜索——用户离开了站点，且检索范围是 issue 而非渲染后的文章。站内虽已有客户端筛选（`templates/tag.html` 的标题子串匹配），但它只有标题维度、且入口只在标签页。

静态站点没有服务端，检索只能在「构建期预建索引 + 浏览器端查询」之间取平衡。

## 决策

1. **检索入口本地化**：`templates/plist.html` 的表单改为 GET 提交到 `{{ blogBase['homeUrl'] }}/search.html`，保留 `name="q"`，去掉新标签页跳转。
2. **索引在构建期生成，且必须建在合并后的完整站点上**：CI 在生成产物合并进工作区后执行 `npx -y pagefind@1.5.2 --site docs`，输出 `docs/pagefind/`。**不能建在生成目录上**——增量构建时该目录只含本次重渲染的文章，在其上建索引会丢掉其余全部文章。
3. **索引范围限定文章正文**：`templates/post.html#postBody` 标记 `data-pagefind-body`；列表页、标签页、检索页无该标记，整体不进索引。文章标题经 `<title>` 入索引（已实测可检索）。
4. **子路径部署由 `homeUrl` 补全**：`Gmeek.py#search_settings` 派生两个键——`lang`（`i18n` 为 CN 时 `zh-CN`，否则 `en`）写入 `<html lang>`，`searchBaseUrl`（`homeUrl` 去尾斜杠 + `/`）作为检索界面的 `baseUrl`。索引内记录的是站点根相对路径，站点托管在 `/blog` 这类子路径下时必须补全。
5. **检索界面复用 Pagefind 自带 UI**：`templates/search.html` 加载 `pagefind-ui.js`，用 `triggerSearch` 承接 `?q=` 深链；配色变量按 Primer 的两级回退映射，随站点明暗模式切换。
   - **尺寸只经 `--pagefind-ui-scale` 调整**：Pagefind 的输入框高度（`64*scale`）、放大镜图标（`18*scale` 见方、`top:23*scale`）、清除按钮（`top:3*scale`、`height:58*scale`）是**联动**的，单独覆盖输入框 `height`/`font-size` 会让图标与按钮偏出垂直中心甚至溢出输入框。取 `scale: 0.75`（输入框 48px、字号 `21*0.75≈16px`），三者中心同为 `24px`；清除按钮文字随缩放变小，单独提回 `12px`（不影响其高度与居中）。
   - 不做什么：不自建倒排索引与查询逻辑；不在查询侧做中文分词补偿（实测无效，见「未解决风险」）。

## 后果

- **收益：** 检索完全静态、无服务端与运行时依赖；索引仅在检索页按需加载，普通页面零额外开销；不向仓库新增依赖（Pagefind 由 CI 临时下载并锁定版本）。
- **代价 / 权衡：** 构建链多一个 Node 步骤，其失败会阻断本次发布（检索页资源缺失时整站检索不可用，宁可失败可见）；索引体积随文章数增长。
- **未解决风险：** Pagefind 的 zh 索引是**词级切分**，与浏览器端查询侧分词并不一致，**短中文查询可能漏检**。已量化（29 篇真实文章实测）：完整标题、小节标题、多字词 0% 漏检；**标题内两字词约 1/3 搜不到目标文章**，且哪些两字词能搜、哪些不能不可预测；强制 `--force-language zh` 不改变结果。该档已由 [ADR-0027](ADR-0027-chinese-substring-search-index.md) 的标题/小节子串索引补齐；**正文内**两字词（实测 12.1%）仍未覆盖。

## 实施位置

- 生成：`Gmeek.py#search_settings`、`Gmeek.py#GMEEK.createSearchHtml`、`Gmeek.py#GMEEK.runAll`、`Gmeek.py#GMEEK.runOne`、`Gmeek.py#GMEEK.runLatest`
- 模板：`templates/search.html`、`templates/base.html`（`lang`）、`templates/post.html`（`data-pagefind-body`）、`templates/plist.html`（检索入口）
- 构建：`.github/workflows/Gmeek.yml`（`Build search index`）
- 测试：`tests/test_pipeline.py`

## 验证

- `pytest` 96 passed（含语言与结果前缀派生、检索页接线、索引范围标记、入口不再指向 issue、CI 步骤顺序）。
- 本地端到端：用真实模板渲染 2 篇文章 + 列表页 + 检索页，Pagefind 在 4 个 HTML 中只索引 2 个文章页；结果链接按 `baseUrl` 补全为 `https://example.com/blog/post/N.html`，`meta.title` 取到文章标题。
- 检索页尺寸：`tests/test_pipeline.py#TestSearchBoxSizing` 按 Pagefind 几何公式校验放大镜与清除按钮垂直居中、且不溢出输入框。

## 关联文档

- 检索入口扩展至文章页：[ADR-0012 文章页搜索框](ADR-0012-post-page-search-box.md)
- [ADR-0021](ADR-0021-search-result-meta.md)：在其检索页与索引范围之上扩展结果的展示内容（标签 + issue 入口）。
- [ADR-0026](ADR-0026-pagefind-search-performance.md)：在其形态之上做加载链 / 每查询渲染 / 跨页面 warmup 优化，不动索引范围与 Pagefind 版本。
- [ADR-0027](ADR-0027-chinese-substring-search-index.md)：补齐本 ADR「未解决风险」中记录的短中文查询漏检（标题/小节子串索引）。

## 下一步

合并后跑一次构建（`workflow_dispatch`），确认线上 `/search.html` 可检索、`/pagefind/` 资源可加载。
