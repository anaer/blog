import markdown
import re
from pathlib import Path
from icons import render as icon_svg

class Markdown2GithubHtml:
    """
    将 Markdown 文本渲染成类 GitHub 的 HTML 页面，
    给代码块增加折叠与复制按钮。
    用法：
        tool = Markdown2GithubHtml()
        html = tool.convert('# Hello')
        Path('out.html').write_text(html, encoding='utf-8')
    """

    # GitHub 官方样式（自动跟随亮色/暗色）
    CSS_URL = "https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.2.0/github-markdown.min.css"

    # 额外内联 JS：折叠+复制 + 按钮样式
    EXTRA_JS = """
<style>
.code-block-wrapper {
  position: relative;
  display: inline-block;
  width: 100%;
}
.code-block-controls {
  position: absolute;
  top: 6px;
  right: 8px;
  z-index: 2;
  display: flex;
  gap: 2px;
}
/* 内容区图标按钮统一语言: 常态半透明 + 主题 muted 色, hover 转不透明并加主题背景 */
.fold-btn, .copy-btn, .code-toggle {
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 2px 4px;
  font-size: 16px;
  line-height: 1;
  border-radius: 4px;
  color: var(--fgColor-muted, var(--color-fg-muted));
  opacity: .6;
  transition: opacity 0.2s, background 0.2s;
}
.fold-btn:hover, .copy-btn:hover, .code-toggle:hover {
  opacity: 1;
  background: var(--bgColor-muted, var(--color-canvas-subtle));
}
.fold-btn svg { display: block; }
.fold-btn .ic-fold { transition: transform 0.2s ease; }
.code-block-wrapper.folded .fold-btn .ic-fold { transform: rotate(180deg); }
/* 复制成功反馈: 图标切换为 check 并短暂转为绿色 */
.copy-btn.copied {
  color: var(--color-success-fg);
  opacity: 1;
}
.code-toggle.off {
  color: var(--color-primer-fg-disabled);
}
.highlight code {
  counter-reset: cl;
}
.highlight .cl {
  display: block;
  counter-increment: cl;
  padding-left: 2.8em;
  position: relative;
  line-height: 1.45;
  /* 关键: .markdown-body pre>code 设了 white-space:pre, .cl 会继承它而无法换行;
     显式声明 pre-wrap 才能保留缩进并允许自动换行 */
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  word-break: normal;
  /* 空行占位: 空 .cl 标签无 in-flow content, 默认 height:0, 会让空行「消失」
     并与下一行挤在一起. min-height 锁定到一行高度, 保留视觉空行 */
  min-height: 1.45em;
  /* 行号槽位底色: 左侧 2em 染成低饱和度底色, 与代码区做视觉区分;
     linear-gradient 只覆盖 padding 内的行号槽, 不侵入代码区; 收尾处 1px 边框强化列分隔
     槽宽取 2em(与行号数字本身宽度贴合): 更宽会让行号整体偏右、离代码区的空档也变大 */
  background-image:
    linear-gradient(to right,
      var(--cl-gutter, rgba(175, 184, 193, 0.28)) 0,
      var(--cl-gutter, rgba(175, 184, 193, 0.28)) calc(2em - 1px),
      var(--cl-gutter-edge, rgba(175, 184, 193, 0.55)) calc(2em - 1px),
      var(--cl-gutter-edge, rgba(175, 184, 193, 0.55)) 2em,
      transparent 2em);
}
/* 深色主题(WorkBuddy 风): 行号槽位底色用中性白色微染(冷暖皆可), 不再带蓝灰调;
   槽位 rgba(255,255,255,0.045) 在 #1a1c20 的底上呈现"略亮一档"的色块,
   1px 分隔线 rgba(255,255,255,0.10) 同步提一档, 整体克制不抢代码区 */
html[data-color-mode="dark"] .highlight .cl {
  background-image:
    linear-gradient(to right,
      rgba(255, 255, 255, 0.045) 0,
      rgba(255, 255, 255, 0.045) calc(2em - 1px),
      rgba(255, 255, 255, 0.10) calc(2em - 1px),
      rgba(255, 255, 255, 0.10) 2em,
      transparent 2em);
}
.highlight .cl::before {
  content: counter(cl);
  position: absolute;
  left: 0;
  width: 2em;
  text-align: center;
  color: var(--fgColor-muted, var(--color-fg-muted));
  user-select: none;
}
.code-block-wrapper.folded .cl ~ .cl {
  display: none;
}
/* 折叠态仅保留首行: 禁止换行但保留缩进(用 pre 而非 nowrap, 后者会吞掉空格), 长行横向滚动 */
.code-block-wrapper.folded {
  overflow-x: auto;
}
.code-block-wrapper.folded pre,
.code-block-wrapper.folded .highlight .cl {
  white-space: pre;
  overflow-wrap: normal;
}
.code-block-wrapper.nowrap .cl {
  white-space: pre;
  overflow-wrap: normal;
}
.code-block-wrapper.nowrap pre {
  white-space: pre;
}
.code-block-wrapper.nolines .cl {
  padding-left: 0;
  /* 行号关闭时一并撤掉槽位底色, 否则左侧会留一道与代码区不连贯的色块 */
  background-image: none;
}
.code-block-wrapper.nolines .cl::before {
  display: none;
}
/* 代码块语言标签: 左上角展示围栏语法(pygments 会丢弃语言类, 由渲染器回填) */
.code-block-wrapper.has-lang {
  padding-top: 22px;
}
.code-lang {
  position: absolute;
  top: 4px;
  left: 10px;
  z-index: 2;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 12px;
  letter-spacing: .5px;
  color: var(--fgColor-muted, var(--color-fg-muted));
  background: var(--bgColor-muted, var(--color-canvas-subtle));
  padding: 0 6px;
  border-radius: 4px;
  user-select: none;
  opacity: .85;
}
/* 移动端 / 触屏(hover: none): 控件常显并加大点按区域;
   同时为控件预留顶部空间, 避免绝对定位的按钮遮挡代码首行 */
@media (hover: none), (max-width: 767px) {
  .code-block-controls {
    top: 2px;
    right: 2px;
    gap: 0;
  }
  .code-block-wrapper,
  .code-block-wrapper.has-lang {
    padding-top: 30px;
  }
  /* 提高特异性以覆盖 .markdown-body .highlight pre{padding:16px} */
  .code-block-wrapper pre,
  .code-block-wrapper .highlight pre {
    padding-top: 10px;
  }
  .fold-btn, .copy-btn, .code-toggle {
    padding: 5px 8px;
    opacity: 1;   /* 触屏无 hover, 常显 */
  }
  .code-lang {
    top: 7px;
    left: 8px;
  }
}
</style>
<script>
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.code-block-wrapper').forEach(w => {
    // 单行代码块无需折叠
    if (w.querySelectorAll('.cl').length < 2) {
      const fb = w.querySelector('.fold-btn');
      if (fb) fb.style.display = 'none';
    }

    // 自动换行 / 行号开关(默认开启)
    const wrapBtn = w.querySelector('.wrap-toggle');
    const linesBtn = w.querySelector('.lines-toggle');
    wrapBtn.addEventListener('click', () => {
      wrapBtn.classList.toggle('off', w.classList.toggle('nowrap'));
    });
    linesBtn.addEventListener('click', () => {
      linesBtn.classList.toggle('off', w.classList.toggle('nolines'));
    });
  });

  // 复制功能(取 textContent, 折叠态也复制全文)
  document.querySelectorAll('.copy-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const code = btn.parentElement.parentElement.querySelector('pre code').textContent;
      navigator.clipboard.writeText(code).then(() => {
        btn.classList.add('copied');
        btn.innerHTML = '__ICON_CHECK__';
        setTimeout(() => {
          btn.classList.remove('copied');
          btn.innerHTML = '__ICON_COPY__';
        }, 1500);
      });
    });
  });

  // 折叠功能: 折叠时保留首行预览(箭头经 CSS 旋转, 不依赖文本)
  document.addEventListener('click', e => {
    const foldBtn = e.target.closest('.fold-btn');
    if (foldBtn) {
      const wrapper = foldBtn.closest('.code-block-wrapper');
      wrapper.classList.toggle('folded');
    }
  });
});
</script>
"""

    # github-markdown-css 要求的最外层容器
    WRAPPER_CSS = "markdown-body"

    # 站内实际使用、但 Pygments 不认识的围栏语言名 -> 等价词法。
    # 键取自全量源文件的围栏统计(36 种里有 11 种不被识别); 右侧目标均在 Pygments 中验证存在。
    # 映射依据(抽样核对真实代码块后确定):
    #   conf    —— 站内 conf 块以 ini 风格(fail2ban/键值)为主, nginx 指令在 ini 下基本不着色、不误导
    #   jinja2  —— 模板 + Jinja 标签
    #   log     —— 日志/终端输出无通用词法, 显式声明"不高亮"(与现状一致, 但意图明确)
    #   reg     —— Windows 注册表导出
    #   jsonp / jsonc —— 带 // 注释的 JSON; json 词法会把注释标成 err token, javascript 不会
    #   cmd     —— 站内 cmd 块实为命令行(reg/curl 等), 实测 batch 词法给 0 token、bash 能正确着色
    #   rc      —— 站内为 Mintty 配置(键值风格)
    #   yml     —— yaml 的同义写法
    #   tree    —— 目录树
    #   pip     —— shell 命令
    FENCE_LANG_ALIASES = {
        "conf": "ini",
        "jinja2": "html+jinja",
        "log": "text",
        "reg": "registry",
        "jsonp": "javascript",
        "jsonc": "javascript",
        "cmd": "bash",
        "rc": "ini",
        "yml": "yaml",
        "tree": "text",
        "pip": "bash",
    }

    def __init__(self):
        """初始化 markdown 解析器，启用常用扩展，并设置多行文本自动换行"""
        # 两条高亮路径并存, 各管一类代码块, 缺一不可:
        #   pymdownx.highlight(经 superfences) 管**围栏**代码块;
        #   codehilite 管**缩进**代码块(4 空格缩进、无围栏), 靠 css_class 对齐同一套 CSS。
        # 配色全部来自 assets/highlight.css, 与 Pygments 主题无关, 故不设 pygments_style。
        extensions = [
            'codehilite',        # 缩进代码块(围栏块由 superfences 处理)
            'tables',
            'toc',
            'pymdownx.extra',    # 含 superfences
            'pymdownx.b64',
            'pymdownx.highlight',
            'pymdownx.emoji',
            'pymdownx.tilde',    # 删除线 ~~
        ]

        extension_configs = {
            "codehilite": {
                "css_class": "highlight",  # 必设: 默认是 codehilite, 与 highlight.css 不匹配
                "use_pygments": True,
                "linenums": False,         # 行号由 .cl 行包裹 + CSS 计数器提供
                "wrapcode": True,
            }
        }
        self.md = markdown.Markdown(extensions=extensions, extension_configs=extension_configs)

    def _extract_fence_langs(self, md_text):
        """按出现顺序提取围栏代码块的语言(无语言记空串), 供标签对齐。"""
        langs = []
        fence = None
        for line in md_text.split('\n'):
            stripped = line.lstrip()
            m = re.match(r'^(`{3,}|~{3,})', stripped)
            if not m:
                continue
            ticks = m.group(1)[0]
            if fence is None:
                fence = ticks
                info = stripped[len(m.group(1)):].strip()
                langs.append(info.split()[0] if info else '')
            elif m.group(1)[0] == fence:
                fence = None
        return langs

    def _normalize_fence_langs(self, md_text):
        """把 FENCE_LANG_ALIASES 中的围栏语言名换成等价词法, 供高亮使用。

        只替换 info string 的首个 token, 其余(如 title="...")原样保留;
        未登记的写法一字不动。标签仍用原始语言名(由 _extract_fence_langs 从同一文本抽取),
        故本函数只影响高亮, 不影响左上角显示。
        """
        out = []
        fence = None
        for line in md_text.split('\n'):
            stripped = line.lstrip()
            m = re.match(r'^(`{3,}|~{3,})(.*)$', stripped)
            if m:
                ticks = m.group(1)
                if fence is None:
                    fence = ticks[0]
                    parts = m.group(2).strip().split(None, 1)
                    mapped = self.FENCE_LANG_ALIASES.get(parts[0].lower()) if parts else None
                    if mapped:
                        indent = line[:len(line) - len(stripped)]
                        tail = (' ' + parts[1]) if len(parts) > 1 else ''
                        out.append(f'{indent}{ticks}{mapped}{tail}')
                        continue
                elif ticks[0] == fence:
                    fence = None
            out.append(line)
        return '\n'.join(out)

    def _add_controls(self, html: str, langs=None) -> str:
        """
        为每个 <pre><code>...</code></pre> 插入控制元素与(可选)语言标签。
        langs 为围栏语言的有序列表, 按 <pre> 出现顺序对齐; 缺失或不匹配时记空串。
        """
        if langs is None:
            langs = []
        cursor = {"i": 0}

        def _repl(m):
            pre_tag = m.group(0)
            code_open = re.search(r"<code[^>]*>", pre_tag)
            code_close = pre_tag.rfind("</code>")
            if code_open and code_close != -1:
                pre_tag = (pre_tag[:code_open.end()]
                           + self._wrap_code_lines(pre_tag[code_open.end():code_close])
                           + pre_tag[code_close:])
            lang = ''
            if cursor["i"] < len(langs):
                lang = langs[cursor["i"]] or ''
            cursor["i"] += 1
            label = f'<span class="code-lang" aria-hidden="true">{lang}</span>' if lang else ''
            wrapper_cls = 'code-block-wrapper has-lang' if lang else 'code-block-wrapper'
            controls = (
                '<div class="code-block-controls">'
                '<button class="code-toggle wrap-toggle" title="自动换行" aria-label="自动换行">'
                f'{icon_svg("wrap", cls="octicon")}'
                '</button>'
                '<button class="code-toggle lines-toggle" title="行号" aria-label="行号">'
                f'{icon_svg("lines", cls="octicon")}'
                '</button>'
                '<button class="fold-btn" title="折叠" aria-label="折叠">'
                f'{icon_svg("fold", cls="octicon ic-fold")}'
                '</button>'
                '<button class="copy-btn" title="复制" aria-label="复制">'
                f'{icon_svg("copy", cls="octicon")}'
                '</button>'
                '</div>'
            )
            return f'<div class="{wrapper_cls}">{label}{controls}\n{pre_tag}</div>'

        # 匹配 <pre> 标签，允许 <pre> 内 <code> 前存在 <span> 等标签
        # 例如 <pre><span ...></span><code>...</code></pre>
        return re.sub(
            r'<pre[^>]*>(?:<[^>]*>)*<code[^>]*>.*?</code>(?:<[^>]*>)*</pre>',
            _repl, html, flags=re.DOTALL
        )

    def _wrap_code_lines(self, inner: str) -> str:
        """把 <code> 内每个逻辑行包成 <span class="cl">, 供 CSS 计数器显示行号。"""
        tokens = re.split(r"(<[^>]+>)", inner)
        lines, current, stack = [], [], []

        def close_line():
            closers = "".join("</" + re.match(r"<(\w+)", t).group(1) + ">" for t in stack)
            return '<span class="cl">' + "".join(current) + closers + "</span>"

        for tok in tokens:
            if not tok:
                continue
            if tok.startswith("</"):
                if stack:
                    stack.pop()
                current.append(tok)
            elif tok.startswith("<"):
                stack.append(tok)
                current.append(tok)
            else:
                parts = tok.split("\n")
                for i, part in enumerate(parts):
                    if i > 0:
                        lines.append(close_line())
                        current = list(stack)
                    current.append(part)
        lines.append(close_line())
        if len(lines) > 1 and not re.sub(r"<[^>]+>", "", lines[-1]).strip():
            lines.pop()
        # 用空串连接: .cl 为 display:block, 各自成行; 若用 "\n" 连接, 在 pre(white-space:pre)
        # 下会额外渲染出空行, 导致行间距翻倍
        return "".join(lines)

    def _add_lazy_loading(self, html: str) -> str:
        """为正文图片注入懒加载属性(已有 loading 标记的不重复注入)。"""
        return re.sub(r'<img (?![^>]*loading=)', '<img loading="lazy" decoding="async" ', html)

    @staticmethod
    def _add_hard_breaks(md_text: str) -> str:
        """给围栏代码块之外的每行末尾追加两个空格, 使 Markdown 的单换行渲染为 <br>。

        代码块内保持原样: 否则每行会被塞入两个尾随空格, 污染代码内容
        (复制时带上、并影响自动换行的断点)。
        """
        out = []
        fence = None
        for line in md_text.splitlines():
            m = re.match(r'^\s*(`{3,}|~{3,})', line)
            if m:
                ticks = m.group(1)[0]
                if fence is None:
                    fence = ticks
                elif ticks == fence:
                    fence = None
                out.append(line)
                continue
            out.append(line + '  ' if fence is None else line)
        return '\n'.join(out)

    def convert(self, md_text: str) -> str:
        """把 markdown 文本渲染成完整 HTML"""
        # 围栏外每行末补两个空格以自动换行(硬换行); 代码块内不加, 避免污染代码
        md_text = self._add_hard_breaks(md_text)
        # 高亮器会丢弃围栏语言, 转换前按出现顺序预扫描, 转换后回填标签。
        # 标签取原始语言名; 高亮另走归一化后的等价词法(见 FENCE_LANG_ALIASES)
        langs = self._extract_fence_langs(md_text)
        body_html = self.md.convert(self._normalize_fence_langs(md_text))
        body_html = self._add_controls(body_html, langs)
        body_html = self._add_lazy_loading(body_html)

        # 复制/成功图标同样取自集中式注册表, 与按钮、模板保持同一风格
        extra_js = (self.EXTRA_JS
                    .replace("__ICON_CHECK__", icon_svg("check", cls="octicon"))
                    .replace("__ICON_COPY__", icon_svg("copy", cls="octicon")))

        full_html = f"""
  <article class="{self.WRAPPER_CSS}">
    {body_html}
  </article>
  {extra_js}
"""
        return full_html

# =====================
# 简易 CLI，可直接 `python md2html.py file.md out.html`
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python md2html.py <input.md> <output.html>")
        sys.exit(1)

    try:
        tool = Markdown2GithubHtml()
        md_path = Path(sys.argv[1])
        if not md_path.exists():
            print(f"Error: Input file '{sys.argv[1]}' not found")
            sys.exit(1)
        md_text = md_path.read_text(encoding='utf-8')
        output_path = Path(sys.argv[2])
        output_path.write_text(tool.convert(md_text), encoding='utf-8')
        print(f"Successfully converted '{sys.argv[1]}' to '{sys.argv[2]}'")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
