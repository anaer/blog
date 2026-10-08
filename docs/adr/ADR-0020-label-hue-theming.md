# ADR-0020：标签配色改为按名称派生色相并随主题自适应

**状态：** 已接受
**创建时间：** 2026-10-08

> **当前状态 / 核心结论：** 标签与日期标签的底色不再取 GitHub label 的色值，改为由**名称确定性派生色相**（`Gmeek.py#deterministic_hue`）；底色与字色在 CSS 里由 `--label-hue` 按主题推导——浅色浅底深字、深色深底浅字，同一色相明度反转。色相来源可由配置项 `labelColorMode` 在「名称派生（默认）」与「GitHub 标签色」之间切换，两种模式观感一致。评论数徽标维持配置色（`.Label--solid`）。下一步无需后续动作。

---

## 背景

标签底色原为 `'#' + label.color`，直接取 GitHub 上该 label 的色值；字色在模板里硬编码 `#fff`。由此有两个问题：

1. **颜色不可控**：同一标签在不同仓库颜色不同，改色只能去 GitHub 后台逐个改；新增标签还得先想好颜色。
2. **不随主题**：`color:#fff` 是内联硬编码，深色模式下饱和底色偏刺眼——所谓「适配深浅」实际只是两种模式共用同一块饱和色。

已有的 `deterministic_color(seed)` 为日期标签派生 `hsl` 色，但它输出**完整颜色**（含饱和度与明度），单一取值同样无法随主题变化。

## 决策

1. **色相由名称确定性派生，来源可由配置切换**：新增 `Gmeek.py#deterministic_hue`（`md5(名称)` 高两位 `% 360`）；`labelHueDict` 由仓库标签名构建，不再读 `label.color`。同一标签永远同色，新增标签零配置。
   - **配置项 `labelColorMode`**：`derived`（默认）按名称派生；`github` 取 GitHub 标签色的**色相**（`Gmeek.py#hex_to_hue`，色值缺失或非法时回退名称派生）。两者**只换色相来源、不换观感**——共用同一套主题自适应渲染，因此都兼容明暗；填其它值等同 `derived`。
2. **底色与字色按主题从色相推导**：模板只输出 `style="--label-hue:N"`，`base.html` 的共享 `.Label` 规则据此计算——
   - 浅色：`hsl(h, 70%, 92%)` 底 + `hsl(h, 80%, 26%)` 字
   - 深色：`hsl(h, 45%, 22%)` 底 + `hsl(h, 85%, 80%)` 字

   同一色相在两种主题下**明度反转**，天然兼容深浅；字色不再硬编码。
3. **日期标签同源**：`dateLabelHue = deterministic_hue(post["number"])`，与标签共用同一套 `.Label` 规则（`tag_data` 的投影字段随之由 `dateLabelColor` 改名为 `dateLabelHue`）。
4. **评论数徽标维持配置色**：它是用户可配置的强调色（配置项 `commentLabelColor`，默认值在 `Gmeek.py#GMEEK.__init__`），保留十六进制取值 + 白字，加 `.Label--solid` 类从色相规则中豁免。
5. **未登记标签的兜底**：模板用 `labelHueDict.get(label, 210)`，标签页 JS 在缺值时不下发变量，两侧都退回 CSS 默认色相 `210`。

   - 不做什么：不改标签的尺寸 / 间距 / 排布；不为标签提供手工指定颜色的入口（如需再议）。

## 后果

- **收益：** 配色完全由站点控制且确定可复现；新增标签零配置；明暗两版同一色相自动协调；`tag.html` 内联的 `labelHueDict` 由「名称 → 十六进制」变为「名称 → 整数」，体积更小。
- **代价 / 权衡：** 标签颜色不再与 GitHub 上的一致（属预期，也是本次目的）；`.Counter` 计数徽标的字色由硬编码白字改为 `inherit`，以适配新的浅底标签。
- **未解决风险：** 色相由 `md5` 派生，不同标签理论上可能落到同一色相（概率约 `1/360`）；标签数量很大时可考虑拉开色相间距。**2026-10-08 修订**(持续累积)：

  **(1) `AttributeError`**：`GMEEK.__init__` 把 `labelHueDict = {…}` 放在 `defaultConfig()` 之后，而 `defaultConfig` 已先读 `self.labelHueDict`，真实实例化会崩。修正：`__init__` 先以空 dict 占位再调 `defaultConfig`，真实色相在之后重算覆盖；新增 `test_init_initialises_labelHueDict_before_defaultConfig` 用 `inspect` 审计行序。

  **(2) 模板拿到空 dict**：第 (1) 步加了占位后，`defaultConfig` 把空 dict 写进了 `blogBase["labelHueDict"]`。`__init__` 末尾重算仅覆盖 `self.labelHueDict` 不够——`plist.html` / `post.html` / `tag.html` 模板读的是 `blogBase["labelHueDict"]`，仍会拿到空 dict，标签全回退默认色相 210。修正：在重算之后加一行 `self.blogBase["labelHueDict"] = self.labelHueDict`；新增 `test_init_resyncs_blogBase_labelHueDict_after_recompute` 钉死重算 / 回写 / 行序三条 invariant。

  **(3) tag_data 投影 KeyError**(2026-10-08)：`tag_data()` 在 `createPlistHtml` 末尾被调用，遍历 `postListJson` 全量；老状态文件(`blogBase.json`)里在本特性加入前已存的历史帖子缺 `dateLabelHue`(以及潜在的未来新增字段)，按硬索引 `post[k]` 直接 KeyError 让整页构建失败。修正：投影改为 `post.get(k, defaults[k])`，缺色相兜底 210(与模板默认一致)、缺 `postUrl/postTitle/createdDate` 兜底空串、`labels` 兜底空列表；新增 `TestTagData` 三条用例钉死兜底值与键集合、生产路径端到端复现确认。

  **(4) 共同教训**(合并 (1)(2)(3))：四条都属于同一类问题——「**持久化状态文件 schema 演进时，新增字段对历史条目的兼容性**」。`blogBase.json`(`slim_state` 输出含 `postListJson`/`singeListJson`)由历史 build 累积，旧条目可能缺本次新增字段。处理模式：
  - **派生字段**(能从 baseline 字段确定性重算, 如 `dateLabelHue ← number`、`createdDate ← createdAt`)：**入口迁移**——在 `defaultConfig` 末尾调用 `migrate_state(blogBase)`, 就地把 `field_migrations` 字典里登记的派生字段补全; 一次构建后由 `slim_state` 落盘, 下游消费者按统一路径消费真值, 不依赖散落 `.get()` 兜底。新增一个派生字段只需在该字典加一行。
  - **非派生可选字段**(如 `description` 可由用户在 `postConfig` 设置, 也可能为空)：消费侧局部防御——`if key in post else default`, 或 `is_html_stale` 这类已有 `.get(k, ...)` 模式。
  - **初始化侧**：进入需要读新字段的方法前，先默认填充(`__init__` 占位 dict)。
  - **写入侧**：写回的字段必须把重算或新值同步推到模板实际读取的位置(`self.blogBase["labelHueDict"] = self.labelHueDict`)。
  - **测试侧**：老状态文件用 fixture 或断言回写出真实结构；避免再用「`SimpleNamespace(labelHueDict={})`」这类占位绕过真实路径。

## 实施位置

- 派生：`Gmeek.py#deterministic_hue`、`Gmeek.py#hex_to_hue`、`Gmeek.py#label_hue`、`Gmeek.py#GMEEK.__init__`（`labelHueDict` 按 `labelColorMode` 构建）、`Gmeek.py#GMEEK.addOnePostJson`（`dateLabelHue`）
- 样式：`templates/base.html`（共享 `.Label` / `.Label--solid`）
- 消费：`templates/plist.html`、`templates/post.html`、`templates/tag.html`（含 JS 改用 `setProperty("--label-hue", …)`）

## 验证

- `pytest` 171 passed（`TestDeterministicHue` 3 例、`TestLabelColorMode` 7 例——含十六进制转色相的已知值与非法输入、两模式取值、非法色值回退、模式归一化、配置默认值，以及 `TestLabelHueTheme` 4 例）。
- 渲染核对：`post.html` 无 GitHub 式内联底色；`plist.html` 评论数徽标为 `.Label--solid`；`tag.html` 三处改用 `setProperty`，内联脚本 `node --check` 通过。

## 下一步

无需后续动作。
