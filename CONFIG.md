# 配置文件说明

### `config.json` 文件

```javascript
{
    "title":"Meekdai",
    "displayTitle":"eekdai",
    "subTitle":"童话是一种生活态度，仅此而已。",
    "homeUrl":"http://blog.meekdai.com",
    "avatarUrl":"http://meekdai.com/avatar.jpg",
    "faviconUrl":"http://meekdai.com/favicon.ico",
    "singlePage":["link","about"],
    "GMEEK_VERSION":"v2.4"
}
```

以上是必须的字段，修改为自己的信息即可，下面是可以自定义字段的描述，可以选择加入到`config.json`中。

```javascript
"startSite":"02/16/2015",
"filingNum":"浙ICP备20023628号",
"onePageListNum":15,
"commentLabelColor":"#006b75",
"i18n":"CN",
"dayTheme":"light",
"nightTheme":"dark",
```
另有不清楚的也可以参考 https://github.com/Meekdai/meekdai.github.io/blob/main/config.json

`dayTheme` / `nightTheme` 取值为 `light` / `dark`——随附的 Primer 子集只定义这两个主题，填其它值（如 `dark_colorblind`）会落回 `:root` 默认（浅色）。


### `.github/workflows/Gmeek.yml` 文件

以仓库内的 `.github/workflows/Gmeek.yml` 为准（唯一事实来源，此处不复制内容）。与本仓库定制相关的要点：

- **触发**：`workflow_dispatch` 与 `issues: [opened, edited, deleted]`。
- **源码**：构建从 `blog` 分支取源码到 `/opt/Gmeek`；`docs/adr`、`docs/glossary`、`docs/review` 只存在于 `main`，发布时从产物中剔除。
- **发布安全闸门**：`workflow_dispatch` 走全量重建，覆盖线上前校验——构建退出码非 0，或重建未产出任何帖子，即中止发布。
- **检索索引**：在合并后的完整站点上执行 `npx pagefind`，输出 `docs/pagefind/`。
- **AI 摘要**：由 `API_URL` / `API_KEY` / `API_MODEL` 三个 secret 提供。
