# Performance Analysis Report: 博客页面模块（前端加载/响应速度）

**Mode**: performance
**Reviewer**: Qoder agent / 2026-09-30
**Benchmark**: 无历史基线——本次实测即基线（2026-09-30；线上为 2026-09-29 生成的部署版，含国内直连 GitHub Pages 网络条件标注）
**Rule config**: `sha256:2bed64cb922060527607cecd5c9b2eb5debd3c2d0727841f1e3294a6ed8604bb`（来源：system）
**Coverage**: 6 reviewed / 6 total / 0 excluded

## Summary

- **Bottleneck Type**: network（页面重量与第三方关键路径）；次级为 processing（tag 页客户端构建 199 个节点）
- **Current Performance**（线上实测，wire=gzip/br 后字节）：
  - 列表页 ≈ **100KB**（HTML 6KB + CSS 87.8KB + JS 6.5KB + 第三方 1.3KB）
  - 文章页 ≈ **100KB**（+starry-night/toc）
  - 标签页 ≈ **154KB**（HTML 单项 **60KB**，其中内联数据 195.6KB→解压后）
  - 其中 **primer.css 独占每页 80.6KB（约 80%）**；浏览器实测（受限网络）：TTFB 1.7s、primer.css 下载 10.2s、DCL 15.4s
- **Target**: 列表页 wire ≤ 50KB（primer 子集化）；标签页 ≤ 70KB（数据瘦身）；第三方不再位于 DCL 关键路径
- **Language Rule Groups**: `**/*.html` -> default.md (system)；`**/*.py` -> python.md (system)

> 环境说明：实测网络为国内直连 Pages（约 8–40KB/s，TTFB 1.7s），绝对耗时偏悲观；**重量占比与第三方依赖两项结论与网络无关**。部署版资源清单与 main 工作区模板一致（batch A/B 未改变资源集合）。

## Bottleneck Analysis

| # | Area | Type | Metric (Current) | Metric (Target) | Root Cause | Impact |
|---|------|------|------------------|-----------------|------------|--------|
| 1 | `assets/Primer@21.1.1/primer.css` | network | 1.32MB raw / **80.6KB gzip，每页加载** | ≤27KB（子集化，实测可达） | 全量未裁剪的 Primer 构建，站点仅用极小子集 | 每页 80% 重量；渲染阻塞；慢网下首屏 +10s 量级 |
| 2 | `templates/tag.html` 内联 jsonData | network + processing | **195.6KB raw** / 页面共 213.8KB（wire 60KB） | ~30KB raw（仅投影所需字段） | 模板把整个 `postListJson`（含 AI 摘要/样式/markdown 路径等）原样内联 | 全站最重页面；客户端解析+构建 199 个 DOM 节点 |
| 3 | `events.vercount.one/js`（defer 外链） | network | DCL 前必须执行；受限网络实测结束于 ~13.7s，DCL 15.4s 随之推迟 | async / load 后注入 | `defer` 语义：所有 defer 脚本先于 DOMContentLoaded | 第三方慢/不可达直接拖慢页面就绪 |
| 4 | `templates/base.html` 的 post-only 样式 | network | highlight.css + github-markdown.min.css = **7.2KB/页**（全部页面） | 0（仅文章页） | 两个样式只服务文章正文，却放在 base | 列表/标签页无谓加载 |
| 5 | 头像（cloud.githubusercontent.com） | network | 跨域，实测单次 11.5s（受限网络） | 自托管（assets/） | 外域资源：DNS+TLS+慢回源 | 每页头部展示位等待；favicon 已自托管可参照 |
| 6 | `assets/oneko.js` + `oneko.gif` | network | 5.2KB/页 | 0（idle 加载或配置开关） | 装饰性脚本无条件加载 | 小；可选项 |
| 7 | 文章正文图片 | network | 无 `loading="lazy"` | lazy + async 解码 | `md2html` 转换未注入 | 多图长帖首屏并发拉取全部图片 |

## Optimization Strategies

| Area | Strategy | Expected Gain | Effort | Priority |
|------|----------|---------------|--------|----------|
| network | **Primer 子集化**：PurgeCSS 对生成页裁剪出 `assets/primer-subset.css`（已实测：1.32MB→380KB raw、75.2→**27.1KB gzip，-64%**），模板改引子集文件；建立"模板改类名→重跑裁剪"的脚本化流程 + 视觉抽查 | 每页 **-53KB wire**（全站最大单项） | Medium | **P0** |
| network + processing | **tag 页数据瘦身**：内联 JSON 只保留 `labels/postUrl/postTitle/dateLabelColor/createdDate` 五个字段（Gmeek.py 加纯函数 + 单测；tag.html 无需改）；附带消除 AI 摘要在 tag 页源码中的重复出现 | 内联 195.6KB→~30KB raw；tag 页 wire 60KB→~15KB | Low | **P1** |
| network | **第三方收敛**：vercount 由 `defer` 改 `async` 或 load 后注入（或恢复自托管版降低跨域握手）；头像下载到 `assets/` 并改 `config.json#avatarUrl`；可选 `preconnect` utteranc.es / events.vercount.one | DCL 不再被第三方阻塞；省一次跨域握手（实测 11.5s 环境） | Low | **P2** |
| network | **post-only 样式拆分**：highlight.css、github-markdown.min.css 移入 post.html 的 head 块（starry-night 已是条件加载） | 列表/标签页 -7.2KB | Low | **P2** |
| network | **图片 lazy**：`md2html.py` 对正文 `<img>` 注入 `loading="lazy" decoding="async"` | 多图帖首屏 | Low | P3 |
| network | oneko 改 `load` 后/idle 加载（或配置开关） | -5.2KB/页 | Low | P3 |
| network | HTML 压缩（Jinja trim_blocks / 后处理 minify） | 列表页 6KB、文章页 8KB 已小，收益有限 | — | P3（可不做） |

**不做什么**：不改 GitHub Pages 托管（`max-age=600` 为平台固定，无自定义响应头能力）；不引入 CDN/服务端（与 ADR-0003「不换静态托管方案」一致）。

## Code-Level Findings

> 来自 python.md「性能」章节与 default.md 检查清单；均已确认热路径与数据规模（198 篇文章、每页必载）。

| # | Severity | File:Line | Finding | Root Cause | Recommendation |
|---|----------|-----------|---------|------------|----------------|
| 1 | Medium | `Gmeek.py#GMEEK.createPlistHtml` → `templates/tag.html` | 全量 `postListJson`（含长文本 description）内联进 HTML，页面 60KB wire、199 节点客户端构建 | 模板直接内联整个集合，未按页面所需投影字段 | 只投影 5 个字段（P1），实现后用 tag 页 wire 实测复核 |
| 2 | Medium | `assets/Primer@21.1.1/primer.css`（引用处 `templates/base.html`） | 每页加载 80.6KB gzip 的全量 Primer，实际使用类目几十个 | 无构建裁剪步骤 | 子集化（P0），产物版本化 + 保留原文件兜底 |
| 3 | Low | `md2html.py#Markdown2GithubHtml.convert` | 正文 `<img>` 无 lazy/异步解码 | 转换管线无图片后处理 | 正则后处理注入 `loading="lazy" decoding="async"`（含单测） |
| 4 | Low | `templates/base.html`（head） | post-only 样式全站加载 | 样式归属未按页面拆分 | 移入 post.html head（P2） |

## Gate Check

- Latency regression vs baseline: 基线建立（本次实测）；**项目未设自动性能门禁**，建议实现批次完成后在同一网络环境复测对比（目标：列表页 wire ≤50KB、DCL 明显下降）
- Throughput regression vs baseline: N/A（静态站，无服务端吞吐）
- Memory regression vs baseline: N/A

## Coverage Detail

| File | Status | Note |
|------|--------|------|
| `templates/base.html` | reviewed | head 资源清单、脚本位置、主题内联脚本 |
| `templates/plist.html` | reviewed | 列表渲染、单页入口、标签链接 |
| `templates/post.html` | reviewed | 条件样式、评论懒加载、toc.js |
| `templates/tag.html` | reviewed | 内联数据规模、客户端构建与搜索 |
| `Gmeek.py` | reviewed | createPlistHtml 数据投影、createPostHtml 资源开关 |
| `md2html.py` | reviewed | 图片/代码块后处理缺口 |
| `assets/` | 资源清单核对 | 逐文件体积与线上 wire 实测（未逐字节审内容） |

## Follow-Up

- 建议按 P0→P2 作为独立批次实施（可挂在批次 C 前后）；实施后同环境复测并回填本报告基线对比
- 部署注意：子集化/拆分属资源路径变更，Pages `max-age=600` 决定生效有 ≤10 分钟延迟
- 若采纳，实施范围与取舍（如 oneko 是否保留、评论是否取消自动加载）建议先落 ADR 再动手
