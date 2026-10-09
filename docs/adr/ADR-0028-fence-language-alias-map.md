# ADR-0028：围栏语言别名映射

**状态：** 已接受
**创建时间：** 2026-10-09

> **当前状态 / 核心结论：** 全量统计 220 篇源 markdown 的围栏语言共 36 种，其中 **11 种 Pygments 不认识**（`conf`/`jinja2`/`log`/`reg`/`jsonp`/`jsonc`/`cmd`/`rc`/`yml`/`tree`/`pip`），涉及 70 个代码块，此前全部降级为纯文本。结论：建立**确定性别名映射**把这 11 种映射到等价词法，标签仍显示原文；**不采用** Pygments 的自动识别（`guess_lang`，实测 45 块只猜对 5 块）。下一步无需后续动作。

---

## 背景

代码块高亮走 Pygments（经 `pymdownx.highlight`，渲染链见 ADR-0011）。Pygments 按**别名表**查词法，查不到就静默降级为纯文本——不报错、不打日志，只是没有配色。

全量统计 220 篇源 markdown 的围栏语言得 36 种，其中 11 种不被识别。同时评估了 Pygments 的自动识别：

- 把**已知语言**的块拿去猜，45 块只猜对 **5 块**（11.1%）：`bash`→`scdoc`、`js`→`xml+django`、`ini`→`scdoc`；
- 启用后受影响的是「无语言 / 名字不认识」的块，其中一多半是**说明文字或输出样例**，会被猜成 `scdoc`/`verilog`/`tsql` 等无关词法。

错误的高亮比不高亮更糟——读者会以为配色有语义。

## 决策

1. **建立确定性别名映射，不启用自动识别**。映射表：

   | 围栏名 | 映射到 | 依据 |
   |---|---|---|
   | `conf` | `ini` | 34 块中 15 块为 ini 风格（fail2ban/键值）、6 块 nginx 指令、13 块其他；`ini` 覆盖最广，且对 nginx 块实测不产生 `err` token |
   | `jinja2` | `html+jinja` | 模板 + Jinja 标签 |
   | `log` | `text` | 终端输出无通用词法，显式钉住「不高亮」 |
   | `reg` | `registry` | Windows 注册表导出 |
   | `jsonp` / `jsonc` | `javascript` | 带 `//` 注释的 JSON；`json` 词法会把注释标成 `err` token（实测 3 个），`javascript` 为 0 |
   | `cmd` | `bash` | 3 块实为 `reg add`/`curl` 命令行；实测 `batch` 给 0 token、`bash` 给 3–13 |
   | `rc` | `ini` | 站内为 Mintty 配置（键值） |
   | `yml` | `yaml` | 同义写法 |
   | `tree` | `text` | 目录树 |
   | `pip` | `bash` | shell 命令 |

2. **在 markdown 层归一化，只换围栏 info string 的首个 token**：`title="…"` 之类的尾部原样保留，未登记的写法一字不动。
3. **标签仍显示原文**：标签由 ADR-0011 的 `_extract_fence_langs` 从同一文本抽取，与映射解耦——写 `conf` 就显示 `conf`，不显示 `ini`。
4. **映射目标的选择是判断**：依据（含抽样数据）写入代码注释，不追求可自动化校验。

不做什么：
- 不启用 Pygments 的自动识别（实测不可靠）。
- 不改 Pygments 的全局别名表（2.20 已移除 `add_lexer`，需触碰内部映射；markdown 层归一化更可控、可单测）。
- 不改标签的显示文本。

## 后果

- **收益**：全站 694 个代码块中，有高亮的块 **502 → 575**（+73）。
- **代价 / 权衡**：转换前多一次 O(行数) 的文本扫描；映射表是**判断性配置**，新增语言名时需人工补录。
- **未解决风险**：`conf` 是异质的（34 块跨 ini / nginx / 其他），选 `ini` 是覆盖最优而非全对；围栏若写在引用块/列表内不被识别——与 ADR-0011 的标签抽取同一限制，两处行为一致。

## 实施位置

- `md2html.py#Markdown2GithubHtml.FENCE_LANG_ALIASES`
- `md2html.py#Markdown2GithubHtml._normalize_fence_langs`
- `md2html.py#Markdown2GithubHtml.convert`
- `tests/test_pipeline.py`（`TestFenceLangAliases`）

## 验证

- 单测 9 例：别名目标在 Pygments 中存在、被映射语言确实获得高亮且无 `err` token、标签保持原文、`log`/`tree` 保持不高亮、已知语言不受影响、未登记语言仍为纯文本、只替换首个 token、正文提及语言名不被误改、未闭合围栏不吞后续行。
- 反证：移除映射条目、或把 `convert` 还原为不调用归一化——对应用例均失败；标签在两版下都保持原文（证明标签与映射解耦）。
- **断言作用边界（如实记录）**：「无 `err` token」只覆盖「目标词法对内容报错」这一类错映射（12 组错映射中抓到 4 组），抓不到「能着色但着错」（如 `conf`→`python` 给 13 token、0 err 仍通过）；映射选择的正确性无法自动化校验。
- `pytest` 全量 246 passed。

## 关联文档

- [ADR-0011](ADR-0011-code-block-language-label.md)：本 ADR 保持其标签机制不变（标签取原文），只改高亮所用的词法。

## 下一步

无需后续动作。
