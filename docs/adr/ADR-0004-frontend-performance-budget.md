# ADR-0004：前端性能与资源交付优化

**状态：** 提议中
**创建时间：** 2026-09-30

> **当前状态 / 核心结论：** 性能审计（`docs/review/2026-09-30-performance-frontend.md`）定位瓶颈为页面重量与第三方关键路径；定为「Primer 子集化 + tag 数据瘦身 + 第三方收敛 + post 样式拆分」按 P0–P2 实施（图片懒加载捎带），下一步进入 SPARC。

---

## 背景

线上实测（2026-09-30）：列表/文章页 wire ≈100KB，其中 `primer.css` 以 80.6KB（gzip）独占约 80%；标签页 ≈154KB（内联全量数据 195.6KB raw）；受限网络下浏览器实测 DCL 15.4s，`defer` 外链 vercount 结束于 13.7s 直接推迟 DCL；head 中 post-only 样式全站加载；头像来自跨域慢源（实测单次 11.5s）。

## 决策

1. **Primer 子集化（P0）**：以生成页与模板为内容源 PurgeCSS 裁剪出 `assets/primer-subset.css`（实测 gzip 75.2→27.1KB，-64%），`templates/base.html` 改引子集；`scripts/build_primer_subset.sh` 固化再生成流程（含「关键类保留」校验）；原 `primer.css` 留档兜底。
2. **tag 页数据瘦身（P1）**：内联 JSON 仅投影 `labels/postUrl/postTitle/dateLabelColor/createdDate` 五字段（`Gmeek.py#tag_data` 纯函数 + 单测）；`templates/tag.html` 改引 `tagListJson`；客户端筛选逻辑不变。
3. **第三方收敛（P2）**：vercount 改为 DOMContentLoaded 后动态注入（不占用首屏关键路径与带宽；其脚本自身已处理 DOM 就绪检查）；头像自托管至 `assets/`（`config.json#avatarUrl` 改本地路径）。
4. **post-only 样式拆分（P2）**：`highlight.css` 与 `github-markdown-css` 从 base 移入 `templates/post.html`（列表/标签页不再加载）。
5. **图片懒加载（P3 捎带）**：`md2html.py` 对正文 `<img>` 注入 `loading="lazy" decoding="async"`（已有标记则不重复注入）。
   - 不做什么：不改静态托管/CDN（`max-age=600` 为平台约束，保留）；oneko 闲置加载与 HTML minify 延后（收益小、非热路径）。

## 后果

- **收益：** 列表/文章页 wire ≈100KB→~45KB；标签页 ≈154KB→~70KB；DCL 不再被第三方阻塞。
- **代价 / 权衡：** 子集 CSS 需在模板类名变化时重跑生成脚本（脚本内含校验）；头像迁移对历史页面无影响。
- **未解决风险：** 子集裁剪后需一次人工视觉抽查（亮/暗模式、窄屏）确认无漏类。

## 实施位置

- 资源与模板：`templates/base.html`（子集引用、vercount 注入）、`templates/post.html`（post-only 样式）、`templates/tag.html`（`tagListJson`）、`assets/primer-subset.css`、`assets/avatar.png`、`config.json`
- 生成器：`Gmeek.py#tag_data`、`Gmeek.py#GMEEK.createPlistHtml`、`md2html.py#Markdown2GithubHtml.convert`
- 工具：`scripts/build_primer_subset.sh`

## 验证

- 基线：`docs/review/2026-09-30-performance-frontend.md`（wire 实测与浏览器水位）。
- 待实施后：同环境复测列表页 wire ≤50KB、标签页 ≤70KB；`pytest` 全绿；子集校验脚本 0 漏类。

## 下一步

进入 SPARC 实施（P0–P2 + 图片懒加载）；完成后按同一网络环境复测并回填对比。
