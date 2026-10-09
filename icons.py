# -*- coding: utf-8 -*-
"""站点图标单一数据源。

统一风格: 线性描边(简洁现代, Lucide/Feather 风)——
  24x24 画布, fill=none, stroke=currentColor, stroke-width=1.5, 圆角端点。
三方复用同一份定义:
  - Gmeek.py 注入模板(IconList)并由 base.html 暴露为前端全局 IconList / renderIcon;
  - md2html.py 渲染代码块控件(见 render);
  - assets/toc.js、assets/sections.js 经前端 renderIcon 复用。

ICONS 的值是图标内部标记(可含 path/circle/rect/line 等), 由 render / 宏 / renderIcon 统一包裹 <svg>。
新增图标只需在此登记一次, 避免路径散落多处导致风格漂移。
"""

# 统一画布与描边参数
VIEWBOX = "0 0 24 24"
STROKE_WIDTH = "1.5"

# name -> 内部标记(线性描边, 24x24)
ICONS = {
    # --- 导航 / 结构 ---
    "post": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M9 13h6"/><path d="M9 17h6"/>',
    "link": '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
    "about": '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/>',
    "moon": '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "rss": '<path d="M4 11a9 9 0 0 1 9 9"/><path d="M4 4a16 16 0 0 1 16 16"/><circle cx="5" cy="19" r="1" fill="currentColor" stroke="none"/>',
    "upload": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m17 8-5-5-5 5"/><path d="M12 3v12"/>',
    "github": '<path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>',
    "home": '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/>',
    "subway": '<rect x="4" y="3" width="16" height="16" rx="2"/><path d="M4 11h16"/><path d="M12 3v8"/><path d="m8 19-2 3"/><path d="m16 19 2 3"/><path d="M8 15h.01"/><path d="M16 15h.01"/>',

    # --- 交互控件 ---
    "plus": '<path d="M12 5v14"/><path d="M5 12h14"/>',
    "minus": '<path d="M5 12h14"/>',
    "chevron": '<path d="m6 9 6 6 6-6"/>',
    "copy": '<rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "wrap": '<path d="M3 6h18"/><path d="M3 12h15a3 3 0 1 1 0 6h-4"/><path d="m16 16-2 2 2 2"/><path d="M3 18h5"/>',
    "lines": '<path d="M8 6h13"/><path d="M8 12h13"/><path d="M8 18h13"/><path d="M3 6h.01"/><path d="M3 12h.01"/><path d="M3 18h.01"/>',
    "fold": '<path d="m18 15-6-6-6 6"/>',
    "eye": '<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>',
    "pen": '<path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>',
}


def viewbox(name=None):
    """返回图标画布。保留 name 参数仅为兼容旧调用; 现全部统一为 24x24。"""
    return VIEWBOX


def render(name, size=16, cls="octicon", svg_id=None):
    """渲染统一风格的 <svg> 字符串(Python 侧使用, 如 md2html.py 的代码块控件)。

    - cls: svg 上的 class; 传空串则不加 class 属性。
    - svg_id: 需要 JS 定位(如主题切换)时给 <svg> 加 id。
    """
    inner = ICONS.get(name, "")
    attrs = f' class="{cls}"' if cls else ""
    if svg_id:
        attrs += f' id="{svg_id}"'
    return (
        f'<svg{attrs} width="{size}" height="{size}" viewBox="{VIEWBOX}" '
        f'fill="none" stroke="currentColor" stroke-width="{STROKE_WIDTH}" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{inner}</svg>'
    )
