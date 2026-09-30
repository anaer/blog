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
.fold-btn, .copy-btn {
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 2px 6px;
  font-size: 16px;
  outline: none;
  box-shadow: none;
  transition: background 0.2s;
}
.fold-btn:hover, .copy-btn:hover {
  background: var(--bgColor-muted, var(--color-canvas-subtle, #eee));
}
.fold-btn {
  color: #6e7681;
}
[data-color-mode="dark"] .fold-btn {
  color: #8b949e;
}
.highlight code {
  counter-reset: cl;
}
.highlight .cl {
  display: block;
  counter-increment: cl;
  padding-left: 3.2em;
  position: relative;
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
</style>
<script>
document.addEventListener('DOMContentLoaded', () => {
  // 单行代码块无需折叠
  document.querySelectorAll('.code-block-wrapper').forEach(w => {
    if (w.querySelectorAll('.cl').length < 2) {
      const fb = w.querySelector('.fold-btn');
      if (fb) fb.style.display = 'none';
    }
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

  // 折叠功能: 折叠时保留首行预览
  document.addEventListener('click', e => {
    if (e.target.classList.contains('fold-btn')) {
      const wrapper = e.target.closest('.code-block-wrapper');
      wrapper.classList.toggle('folded');
      e.target.textContent = wrapper.classList.contains('folded') ? '▼' : '▲';
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

    def _add_controls(self, html: str) -> str:
        """
        为每个 <pre><code>...</code></pre> 插入控制元素：
          <button class='fold-btn'>▲</button>
          <button class='copy-btn'>复制</button>
        """
        def _repl(m):
            pre_tag = m.group(0)
            code_open = re.search(r"<code[^>]*>", pre_tag)
            code_close = pre_tag.rfind("</code>")
            if code_open and code_close != -1:
                pre_tag = (pre_tag[:code_open.end()]
                           + self._wrap_code_lines(pre_tag[code_open.end():code_close])
                           + pre_tag[code_close:])
            controls = (
                '<div class="code-block-controls">'
                '<button class="fold-btn">▲</button>'
                '<button class="copy-btn">'
                '<svg width="18" height="18" viewBox="0 0 20 20" style="vertical-align:middle">'
                '<rect x="6" y="2" width="9" height="13" rx="2" fill="#555"/>'
                '<rect x="3" y="5" width="9" height="13" rx="2" fill="#aaa"/>'
                '</svg>'
                '</button>'
                '</div>'
            )
            return f'<div class="code-block-wrapper">{controls}\n{pre_tag}</div>'

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
        body_html = self._add_controls(body_html)
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
