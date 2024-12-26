## [暴力猴Violentmonkey](https://violentmonkey.github.io/)

### [元数据块](https://violentmonkey.github.io/api/metadata-block/)

```markdown
// ==UserScript==
// @name 标题
// @name:zh-CN 可以在变量名后增加区域信息:zh-CN 实现多语言国际化
// @namespace 命名空间 通过name和namespace确定唯一, 创建同名脚本时会提示冲突
// @description 描述
// @author 作者
// @version 1.0.2 版本信息 用于检查版本更新
// @match 匹配规则
// @exclude-match 排除规则
// @include 同@match 建议使用@match
// @exclude 同@exclude-match 建议使用@exclude-match
// @grant none 授权GM_* API
// @noframes 添加则表示脚本只在顶级文档中执行, 不在嵌套frame中执行
// @run-at       document-start 脚本执行时间
// @inject-into page 默认 确定脚本注入到哪个上下文中
// @icon 图标链接
// @require https://my.cdn.com/jquery.js 引入三方js
// @resource logo https://my.cdn.com/logo.png 引入三方资源, 脚本中通过GM_getResourceText和GM_getResourceURL访问
// @resource text https://my.cdn.com/some-text.txt
// @downloadURL 下载链接
// @supportURL 支持链接 用于问题反馈等
// @homepageURL 主页链接
// @unwarp 添加则表示脚本按原样注入页面的全局范围
// ==/UserScript==
```

### [GM_* API接口](https://violentmonkey.github.io/api/gm/)

-   [GM\_\*](https://violentmonkey.github.io/api/gm/#gm_)
    -   [GM\_info](https://violentmonkey.github.io/api/gm/#gm_info)
    -   [GM\_getValue](https://violentmonkey.github.io/api/gm/#gm_getvalue)
    -   [GM\_setValue](https://violentmonkey.github.io/api/gm/#gm_setvalue)
    -   [GM\_deleteValue](https://violentmonkey.github.io/api/gm/#gm_deletevalue)
    -   [GM\_listValues](https://violentmonkey.github.io/api/gm/#gm_listvalues)
    -   [GM\_addValueChangeListener](https://violentmonkey.github.io/api/gm/#gm_addvaluechangelistener)
    -   [GM\_removeValueChangeListener](https://violentmonkey.github.io/api/gm/#gm_removevaluechangelistener)
    -   [GM\_getResourceText](https://violentmonkey.github.io/api/gm/#gm_getresourcetext)
    -   [GM\_getResourceURL](https://violentmonkey.github.io/api/gm/#gm_getresourceurl)
    -   [GM\_addElement](https://violentmonkey.github.io/api/gm/#gm_addelement)
    -   [GM\_addStyle](https://violentmonkey.github.io/api/gm/#gm_addstyle)
    -   [GM\_openInTab](https://violentmonkey.github.io/api/gm/#gm_openintab)
    -   [GM\_registerMenuCommand](https://violentmonkey.github.io/api/gm/#gm_registermenucommand)
    -   [GM\_unregisterMenuCommand](https://violentmonkey.github.io/api/gm/#gm_unregistermenucommand)
    -   [GM\_notification](https://violentmonkey.github.io/api/gm/#gm_notification)
    -   [GM\_setClipboard](https://violentmonkey.github.io/api/gm/#gm_setclipboard)
    -   [GM\_xmlhttpRequest](https://violentmonkey.github.io/api/gm/#gm_xmlhttprequest)
    -   [GM\_download](https://violentmonkey.github.io/api/gm/#gm_download)
-   [GM.\*](https://violentmonkey.github.io/api/gm/#gm)

### [DOM观察](https://violentmonkey.github.io/guide/observing-dom/)

### [匹配规则](https://violentmonkey.github.io/api/matching/)

![image](https://violentmonkey.github.io/static/5353fff61b7784074245599dfc3ebf63/a6d36/match.png)
