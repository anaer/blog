# Review Report: 手机版分页修复与按屏宽增减页码

**ID**: `REV-0001`
**Date**: 2026-10-14
**Mode**: review
**Reviewer**: WorkBuddy AI（design-manager「落地后必审」触发）
**Scope**: `Gmeek.py`、`templates/plist.html`、`tests/test_pipeline.py`、`CHANGELOG.md`（工作区 diff，4 文件 / +87 −13）
**Rule config**: `sha256:0a49b907877f63c54f9cb45bfa0e505f6f20319ea1dcd137db6fae4ddc7144a5`（来源：system）
**Coverage**: 4 reviewed / 4 total / 0 excluded

## Summary

业务背景：列表页为纯页码导航（无「上一页/下一页」）。`primer-subset.css` 的
`.pagination > * { display:none }` 隐藏阶梯（`<544px` 仅留首末项、`544–767px` 加第 2/倒 2 项、
`≥768px` 才全显）是为逐页翻页型分页设计的，导致纯页码导航在 767px 以下被压成只剩首末两页。
本次放开该阶梯，改为服务端按「环数」标注可折叠项、窄屏由 CSS 折叠外圈，并把窗口由 ±2 提至 ±3。
同时释放窄屏下 `.SideNav{min-width:360px}` 造成的横向溢出。

总体评价：改动范围可控、逻辑自洽，边界处理完整。**未发现 critical / high / medium 问题**；
2 项 `low`（测试 fixture 契约滞后、默认值字面重复）均为非阻塞。

## Issues

| # | Severity | File:Line | Category | Finding | Recommendation |
|---|----------|-----------|----------|---------|----------------|
| 1 | Low | `tests/test_pipeline.py:411,507,950,1782,1942,2124,2155` | test | `pageNav` 契约已由「int / `"gap"` 扁平列表」改为「`{kind,value,ring,fold}` 字典列表」，这 7 处 fixture 仍传扁平形状。当前因 `totalPages: 1` 跳过整个分页块而无症状，属潜伏陷阱：一旦这些 fixture 的 `totalPages` 被调大，模板 `item['kind']` 会直接抛错 | 单页 fixture 统一改为 `"pageNav": []`（单页本就不渲染分页，空列表语义更准）；泄漏用例改为 `[{"kind": "page", "value": 1, "ring": 0, "fold": False}]` |
| 2 | Low | `Gmeek.py:146,168` | maintainability | `window=3` 默认值在 `build_page_nav` 与 `build_page_items` 各写一次。当前 `build_page_items` 会把自身 window 透传给 `build_page_nav`，无行为漂移；但两处字面各自演进时会静默不一致 | 抽模块级常量（如 `PAGE_NAV_WINDOW = 3`）供两者共用 |

## By Severity

### Critical

无。

### High

无。

### Medium

无。

### Low

- **`tests/test_pipeline.py:411,507,950,1782,1942,2124,2155`** [test] — 7 处 fixture 仍用旧的扁平 `pageNav` 形状。
  > 建议：单页 fixture 用 `[]`，泄漏用例用字典项；与 `TestPageNumberPagination._render` 的 `build_page_items` 口径统一。

- **`Gmeek.py:146,168`** [maintainability] — `window=3` 默认值重复两处。
  > 建议：提为模块级常量，两函数共用。

## Severity Distribution

- Critical: 0
- High: 0
- Medium: 0
- Low: 2

## Language-Specific Notes

| Rule group | Pattern | Rule file | Source | Files |
|------------|---------|-----------|--------|-------|
| 1 | `**/*.{py,pyi,pyw,ipynb}` | `python.md` | system | 2（`Gmeek.py`、`tests/test_pipeline.py`） |
| 2 | `default` | `default.md` | system | 2（`templates/plist.html`、`CHANGELOG.md`） |

Python 规则组专项结论：

- **边界与异常处理**：`build_page_items` 的 `items[left[0] - 1]` / `items[right[-1] + 1]` 两处下标已逐一推演——
  `left` 排除首页（`1 < value`）故 `left[0] ≥ 1`；`right` 排除末页（`value < total`）且 nav 末元素恒为 `total`，
  故 `right[-1] ≤ len-2`。`total <= 0` 与 `total == 1` 时两侧均为空，短路跳过。**无越界风险**。
- **可变默认参数 / 共享状态**：`build_page_items` 每次调用新建 dict，无跨调用共享。
- **测试代码**：新增 9 例均为确定性断言（`build_page_nav` 钉死完整序列、`build_page_items` 钉死
  `{value: ring}` 映射），无空值兜底式弱断言；`test_contiguous_with_first_page_is_not_folded`
  专门覆盖「折叠会留下跳号断档」这一反例场景。

跨语言工匠规范（`fullstack-craft.md`，Step 2.10）：

- 行数预算：`Gmeek.py` 773 行、`templates/plist.html` 134 行，均低于自研单文件 1200 行门槛；新增函数 18 行。
- 动效属性：本次未新增 `transition` / `@keyframes`。
- 功能图标：分页省略号用 U+2026，非 Emoji 码位。
- 8 态闭环：页码链接的常态 / hover / focus / active 由 primer 既有规则覆盖，`:current` 为不可交互态
  （`<span>`，`aria-current="page"`），本次补齐其视觉态。窄屏折叠项以 `display:none` 退出 tab 序，
  不会留下不可见却可聚焦的控件。

## Coverage Detail

| File | Status | Note |
|------|--------|------|
| `Gmeek.py` | reviewed | `build_page_nav` 窗口默认值 2→3；新增 `build_page_items`；`createPlistHtml` 切换调用 |
| `templates/plist.html` | reviewed | 放开 primer 隐藏阶梯、`.gap` 悬停态、窄屏 `data-ring` 折叠、`.SideNav` 溢出修复、分页块改遍历字典 |
| `tests/test_pipeline.py` | reviewed | 导入与 fixture 适配、4 处窗口期望更新、新增 9 例 |
| `CHANGELOG.md` | reviewed | 新增一条；`check_changelog.py` H1–H4 通过（exit 0） |

### 检查器运行结果

| 检查器 | 范围 | 结果 |
|--------|------|------|
| `resolve_rules.py` | 4 文件 | 2 规则组，`reviewable_files=4`，`excluded_files=[]` |
| `check_comment_conventions.py --check-refs` | 3 文件 | 4 处 C1/C2 命中，**全部位于既有行**（`tests/test_pipeline.py:196/1048/1407/1408`），不在本次 diff 区间（16、2207、2252–2303）内，属既有问题，不计入本次发现项 |
| `check_changelog.py` | `CHANGELOG.md` | 通过（H1/H2/H3/H4），exit 0 |

### 回归验证

- `pytest` **257 passed**（较上轮 +7）。
- `python -m py_compile Gmeek.py` 通过。
- 端到端渲染矩阵（12 组 `total/current`）核对桌面与窄屏可见集，确认折叠后**无「跳号却无省略号」断档**：

  | total/current | 桌面 | 窄屏（<768px） |
  |---|---|---|
  | 5/3 | 1 2 3 4 5 | 1 2 3 4 5 |
  | 12/1 | 1 2 3 4 … 12 | 1 2 … 12 |
  | 12/6 | 1 2 3 4 5 6 7 8 9 … 12 | 1 2 3 4 5 6 7 … 12 |
  | 20/10 | 1 … 7 8 9 10 11 12 13 … 20 | 1 … 9 10 11 … 20 |
  | 30/15 | 1 … 12 13 14 15 16 17 18 … 30 | 1 … 14 15 16 … 30 |

- 样式覆盖的源序依赖已核验：`primer-subset.css` 由 `base.html` 的 `<link>` 在 `<head>` 加载，
  `plist.html` 的 `{% block style %}` 渲染于 `</head>` 之后，同特异性下后者胜出——
  `.pagination>*{display:inline-block;}` 确能覆盖 primer 的 `display:none` 阶梯。

## 未覆盖项

- 未在真实移动浏览器做像素级截图核验（本地浏览器自动化环境首次启动超时）；
  窄屏结论来自 CSS 级联静态推演 + 服务端渲染可见集模拟，非截图实证。
- 未验证 `oneko.js` 等脚本在折叠后的分页区域的行为（本次未触及脚本）。

## Follow-Up

- 2 项 `low` 均为非阻塞，可择机清理；**无需为此复跑审查**（无 critical/high/medium）。
- 用户指令为「修复问题」而非「提交」，故本次未执行 `git add` / `git commit`。

## 决策性内容

评审确认了以下设计约定，建议评估是否沉淀：

- **窄屏分页折叠必须从外向内连续进行**——仅当该侧整段与首页/末页之间隔着省略号时才可折叠，
  否则会出现「跳号却无省略号」的断档。这是一条跨入口一致的设计约束（`build_page_items` 的 `fold` 判定）。
- **有意覆盖 `primer-subset.css` 的分页隐藏阶梯**——该阶梯服务于逐页翻页型分页，与本站纯页码导航语义不符，
  故在 `plist.html` 显式放开。属「为什么这样写是有意的设计」。
- **宽屏 ±3 环、窄屏折叠至 ±1 环**的两档策略（服务端按上限渲染，窄屏由 CSS 收窄）。

是否要通过 `design-manager`（adr 模式）沉淀进 `docs/adr/`？[是 / 仅对话讨论不落盘 / 跳过]
