# ADR-0016：主题切换失效——`modeSwitch` 按属性名读取

**状态：** 已接受
**创建时间：** 2026-10-08

> **当前状态 / 核心结论：** 主题切换按名读取 `data-color-mode`——不可按下标取属性：`<html>` 首个属性是 `lang`，下标法会只走 `changeLight()` 而无法切到深色。下一步无需后续动作。

---

## 背景

点击主题切换按钮后无法切到深色，表现为「切换主题失效」。

根因是 `modeSwitch()` 用**属性下标**判断当前明暗：

```js
if(document.getElementsByTagName("html")[0].attributes[0].value=="light"){ changeDark(); }
else{ changeLight(); }
```

而 `<html>` 的首个属性是 `lang`，不是 `data-color-mode`：

```html
<html lang="zh-CN" data-color-mode="light" data-dark-theme="dark" data-light-theme="light">
```

于是 `attributes[0].value` 恒为 `"zh-CN"`（或 `"en"`），与 `"light"` 比较永远为假 → 永远走 `else` → 只调用 `changeLight()`。

上游 Gmeek 的 `<html>` 原本没有 `lang`，`attributes[0]` 恰好就是 `data-color-mode`，所以能用；ADR-0007 为检索分词把 `lang` 加在最前面后，这个位置假设就失效了。

用最小 DOM 桩在 Node 中回放真实脚本可复现：

| 实现 | 起始 | 连点 3 次后的模式序列 |
|------|------|----------------------|
| 旧（`attributes[0]`） | light | `light → light → light → light`（卡住） |
| 新（按名读取） | light | `light → dark → light → dark`（正常） |

## 决策

1. **按属性名读取**，不再依赖属性顺序：

   ```js
   var root=document.getElementsByTagName("html")[0];
   if(root.getAttribute("data-color-mode")=="light"){ changeDark(); localStorage.setItem("meek_theme","dark"); }
   else{ changeLight(); localStorage.setItem("meek_theme","light"); }
   ```

   `getAttribute` 对属性顺序与数量都免疫，`lang` 之类的新增属性不会再影响判断。

2. **渲染版本递增**：`base.html` 会内联进每个页面（含缓存的文章 HTML），故 `RENDER_VERSION` 由 6 提升至 **7**，触发全站帖子重转。

   - 不做什么：不改动 `changeDark`/`changeLight` 的其余逻辑；不改动 `<html>` 的属性顺序（按名读取后顺序已无关紧要，调整顺序反而会再次制造隐式耦合）。

## 后果

- **收益**：主题切换恢复正常，深/浅色可来回切换且 `localStorage` 记录正确；判断逻辑不再与 `<html>` 的属性顺序耦合。
- **代价 / 权衡**：无实质代价；仅一次全站重转。
- **未解决风险**：同类「按下标取属性/子节点」的写法仍可能出现在别处——本仓库已全量检索 `attributes[`，仅此一处。

## 实施位置

- 模板：`templates/base.html#modeSwitch`
- 版本：`Gmeek.py#RENDER_VERSION`
- 测试：`tests/test_pipeline.py`（新增 `TestThemeSwitch`）

## 验证

- `pytest` 142 passed（新增 3 例：`modeSwitch` 必须按名读取、不得按下标取属性、`changeDark`/`changeLight` 均被分支引用）。
- Node + 最小 DOM 桩回放真实脚本：新模式序列 `light → dark → light → dark`，旧模式序列恒为 `light`。
- 全量检索确认仓库内 `attributes[` 仅剩此一处（已修复）。

## 下一步

无需后续动作。
