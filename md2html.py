import markdown
import re
from pathlib import Path

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
  opacity: 0.45;
  transition: opacity 0.2s;
}
.code-block-wrapper:hover .code-block-controls,
.code-block-wrapper:focus-within .code-block-controls {
  opacity: 1;
}
.fold-btn, .copy-btn, .code-toggle {
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 2px 6px;
  font-size: 16px;
  line-height: 1;
  outline: none;
  box-shadow: none;
  transition: background 0.2s;
}
.fold-btn:hover, .copy-btn:hover, .code-toggle:hover {
  background: var(--bgColor-muted, var(--color-canvas-subtle, #eee));
}
.fold-btn svg { display: block; }
.fold-btn .ic-fold { transition: transform 0.2s ease; }
.code-block-wrapper.folded .fold-btn .ic-fold { transform: rotate(180deg); }
.fold-btn, .code-toggle {
  color: #6e7681;
}
[data-color-mode="dark"] .fold-btn,
[data-color-mode="dark"] .code-toggle {
  color: #8b949e;
}
.code-toggle.off {
  color: #c6cbd1;
}
[data-color-mode="dark"] .code-toggle.off {
  color: #484f58;
}
.highlight code {
  counter-reset: cl;
}
.highlight .cl {
  display: block;
  counter-increment: cl;
  padding-left: 3.2em;
  position: relative;
  line-height: 1.45;
  overflow-wrap: anywhere;
}
.highlight .cl::before {
  content: counter(cl);
  position: absolute;
  left: 0;
  width: 2.4em;
  text-align: right;
  color: #6e7681;
  user-select: none;
}
[data-color-mode="dark"] .highlight .cl::before {
  color: #8b949e;
}
.code-block-wrapper.folded .cl ~ .cl {
  display: none;
}
/* 折叠态仅保留首行: 禁止换行, 长行横向滚动, 保证预览严格为一行 */
.code-block-wrapper.folded {
  overflow-x: auto;
}
.code-block-wrapper.folded pre,
.code-block-wrapper.folded .highlight .cl {
  white-space: nowrap;
  overflow-wrap: normal;
}
.code-block-wrapper.nowrap pre {
  white-space: pre;
}
.code-block-wrapper.nowrap .cl {
  overflow-wrap: normal;
}
.code-block-wrapper.nolines .cl {
  padding-left: 0;
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
  color: #6e7681;
  background: var(--bgColor-muted, var(--color-canvas-subtle, #f6f8fa));
  padding: 0 6px;
  border-radius: 4px;
  user-select: none;
  opacity: .85;
}
[data-color-mode="dark"] .code-lang {
  color: #8b949e;
  background: var(--bgColor-muted, var(--color-canvas-subtle, #161b22));
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
        btn.innerHTML = '<svg width="18" height="18" viewBox="0 0 20 20" style="vertical-align:middle"><path fill="green" d="M7.629 15.314l-4.243-4.243 1.414-1.414 2.829 2.828 6.364-6.364 1.414 1.414z"/></svg>';
        setTimeout(() => {
          btn.innerHTML = '<svg width="18" height="18" viewBox="0 0 20 20" style="vertical-align:middle"><rect x="6" y="2" width="9" height="13" rx="2" fill="#555"/><rect x="3" y="5" width="9" height="13" rx="2" fill="#aaa"/></svg>';
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

    def __init__(self):
        """初始化 markdown 解析器，启用常用扩展，并设置多行文本自动换行"""
        extensions = [
            'fenced_code',       # 代码块
            'codehilite',        # 高亮
            'tables',
            'toc',
            'pymdownx.extra',
            'pymdownx.b64',
            'pymdownx.highlight',
            'pymdownx.emoji',
            'pymdownx.tilde',    # 删除线 ~~
        ]

        extension_configs = {
            "codehilite": {
                "css_class": "highlight",
                "use_pygments": True,
                "pygments_style": "monokai",
                "linenums": False,
                "wrapcode": True,  # 让代码块内容自动换行
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
                '<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">'
                '<path fill="currentColor" d="M12 3 6 9h3v4h2V9h3z"/></svg>'
                '</button>'
                '<button class="code-toggle lines-toggle" title="行号" aria-label="行号">'
                '<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">'
                '<path fill="currentColor" d="M2 3h1v1H2zM4.5 3h9v1h-9zM2 7h1v1H2zM4.5 7h9v1h-9zM2 11h1v1H2zM4.5 11h9v1h-9z"/></svg>'
                '</button>'
                '<button class="fold-btn" title="折叠" aria-label="折叠">'
                '<svg class="ic-fold" width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">'
                '<path fill="currentColor" d="M8 5 3.5 10h9z"/></svg>'
                '</button>'
                '<button class="copy-btn" title="复制" aria-label="复制">'
                '<svg width="18" height="18" viewBox="0 0 20 20" style="vertical-align:middle">'
                '<rect x="6" y="2" width="9" height="13" rx="2" fill="#555"/>'
                '<rect x="3" y="5" width="9" height="13" rx="2" fill="#aaa"/>'
                '</svg>'
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
        return "\n".join(lines)

    def _add_lazy_loading(self, html: str) -> str:
        """为正文图片注入懒加载属性(已有 loading 标记的不重复注入)。"""
        return re.sub(r'<img (?![^>]*loading=)', '<img loading="lazy" decoding="async" ', html)

    def convert(self, md_text: str) -> str:
        """把 markdown 文本渲染成完整 HTML"""
        # 每一行末 增加两个空格 以自动换行
        md_text = '\n'.join(line + '  ' for line in md_text.splitlines())
        body_html = self.md.convert(md_text)
        # 高亮器会丢弃围栏语言, 转换前按出现顺序预扫描, 转换后回填标签
        langs = self._extract_fence_langs(md_text)
        body_html = self._add_controls(body_html, langs)
        body_html = self._add_lazy_loading(body_html)

        full_html = f"""
  <article class="{self.WRAPPER_CSS}">
    {body_html}
  </article>
  {self.EXTRA_JS}
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
