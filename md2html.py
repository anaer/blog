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
  background: #eee;
}
</style>
<script>
document.addEventListener('DOMContentLoaded', () => {
  // 复制功能
  document.querySelectorAll('.copy-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const code = btn.parentElement.parentElement.querySelector('pre code').innerText;
      navigator.clipboard.writeText(code).then(() => {
        btn.innerHTML = '<svg width="18" height="18" viewBox="0 0 20 20" style="vertical-align:middle"><path fill="green" d="M7.629 15.314l-4.243-4.243 1.414-1.414 2.829 2.828 6.364-6.364 1.414 1.414z"/></svg>';
        setTimeout(() => {
          btn.innerHTML = '<svg width="18" height="18" viewBox="0 0 20 20" style="vertical-align:middle"><rect x="6" y="2" width="9" height="13" rx="2" fill="#555"/><rect x="3" y="5" width="9" height="13" rx="2" fill="#aaa"/></svg>';
        }, 1500);
      });
    });
  });

  // 折叠功能
  document.addEventListener('click', e => {
    if (e.target.classList.contains('fold-btn')) {
      const pre = e.target.parentElement.parentElement.querySelector('pre');
      const collapsed = pre.style.display === 'none';
      pre.style.display = collapsed ? 'block' : 'none';
      e.target.textContent = collapsed ? '▲' : '▼';
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
            r'<pre[^>]*>(?:<span[^>]*>.*?</span>\s*)*<code[^>]*>.*?</code></pre>',
            _repl, html, flags=re.DOTALL
        )

    def convert(self, md_text: str) -> str:
        """把 markdown 文本渲染成完整 HTML"""
        # 每一行末 增加两个空格 以自动换行
        md_text = '\n'.join(line + '  ' for line in md_text.splitlines())
        body_html = self.md.convert(md_text)
        body_html = self._add_controls(body_html)

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
    tool = Markdown2GithubHtml()
    md_path = Path(sys.argv[1])
    md_text = md_path.read_text(encoding='utf-8')
    Path(sys.argv[2]).write_text(tool.convert(md_text), encoding='utf-8')
