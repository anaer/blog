# ADR-0009：TOC 子节点折叠展开的 +/− 标识

**状态：** 已接受
**创建时间：** 2026-10-08
**最近更新：** 2026-10-08（+/− 切换按钮由左侧改为右侧）

> **当前状态 / 核心结论：** 含子节点的目录项增加 SVG +/− 切换按钮，反映并可手动控制折叠态；切换按钮**右对齐**（`right: 2px`），左侧不再预留槽位，缩进只由 `(level-1) * 10` 决定。折叠机制由 `.toc-children.collapsed` 改为 `.toc-item.open` 驱动。与滚动自动跟随（applyState）共存。下一步浏览器验证切换与高亮不冲突。

---

## 背景

`assets/toc.js` 子节点默认折叠、滚动到所在小节才展开，但目录上没有任何可见的折叠/展开指示，用户无从知晓可点击展开。

## 决策

1. **可见指示 + 手动控制**：渲染时为有子节点的 `.toc-item` 插入 `button.toc-toggle`（内嵌 +/− 两个 SVG）；点击独立切换该节点 `.open`，展开/收起其子目录，不触发标题跳转。
   - **右对齐放置**：`+/−` 按钮 `position: absolute; right: 2px`，固定在每行最右内侧；链接文字的右内边距预留 `TOGGLE_SLOT`（22px）防止长标题与按钮重叠。
   - **左侧不再预留槽位**：之前版本把 `+/−` 放在每行最左，给所有目录项无条件预留 16px 的左侧占位让同级对齐。改为右对齐后左侧只承担缩进（`(level - 1) * 10`），文字更紧凑、视觉重心也回到标题本身。
   - **槽位对齐不变**：槽位（无论左右）仍对**所有**目录项（含叶子节点）无条件预留，**仍不能用 `children.length` 分支**——否则同级里有/无子节点的项会差一个槽位、无法对齐。当前是右内边距方向上保留这一约束。
2. **折叠态改用 `open` 类**：`.toc-children.collapsed` 方案改为 `.toc-item:not(.open) > .toc-children { display:none }`；图标随 `.open` 切换 +/−（`assets/toc.js` 的 CSS 块 + `applyState`）。
3. **保持滚动自动跟随语义**：`assets/toc.js#applyState` 仍只展开「当前标题 + 祖先」分支，手动展开的非活动分支在滚动时回缩——自动跟随行为不变，+/− 同时支持临时 peek。

## 后果

- **收益：** 目录提供明确的折叠提示与手动展开能力；按钮右对齐后视觉重心回到标题本身，缩进更紧凑；零新增依赖。
- **代价 / 权衡：** 手动展开的兄弟分支会随滚动自动回缩（标准 TOC 行为，非缺陷）。右对齐时若目录面板极窄（< 80px）按钮可能与长标题相互挤压——但 panel 宽度由 `.toc { width: 200px }` 固定，足够。

## 实施位置

- `assets/toc.js`（toggle 按钮、`.open` 驱动、点击委托、`itemByWrapper` 映射）

## 验证

- `tests/test_pipeline.py` 静态断言：toc.js 含 `toc-toggle`、`itemByWrapper`、`.toc-item:not(.open) > .toc-children`、`classList.toggle('open'`，以及 `+/−` 槽位**右侧**无条件预留（`paddingRight` 含 `TOGGLE_SLOT` 且不得依赖 `children.length`），左侧无 `TOGGLE_SLOT`，`.toc-toggle` 以 `right: 2px` 定位。
- 视觉预览 `toc_preview.html`：对照展示「左对齐（旧版，对齐失败）」与「右对齐（新版）」，可手动展开/折叠确认无重叠。

## 关联文档

- [ADR-0019](ADR-0019-icon-button-unification.md)：统一 `.toc-toggle` 的交互与配色（常态半透明、hover 转不透明 + 主题背景）。

## 下一步

浏览器确认 +/− 切换与滚动高亮共存、嵌套子目录折叠正确。
