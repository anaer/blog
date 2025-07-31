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

    # 额外内联 JS：折叠+复制
    EXTRA_JS = """
<script>
document.addEventListener('DOMContentLoaded', () => {
  // 复制功能
  document.querySelectorAll('.copy-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const code = btn.nextElementSibling.querySelector('code').innerText;
      navigator.clipboard.writeText(code).then(() => {
        btn.textContent = '已复制';
        setTimeout(() => btn.textContent = '复制', 1500);
      });
    });
  });

  // 折叠功能
  document.addEventListener('click', e => {
    if (e.target.classList.contains('fold-btn')) {
      const pre = e.target.parentElement.querySelector('pre');
      const collapsed = pre.style.display === 'none';
      pre.style.display = collapsed ? 'block' : 'none';
      e.target.textContent = collapsed ? '收起' : '展开';
    }
  });
});
</script>
"""

    # github-markdown-css 要求的最外层容器
    WRAPPER_CSS = "markdown-body"

    def __init__(self):
        """初始化 markdown 解析器，启用常用扩展"""
        extensions = [
            'fenced_code',       # 代码块
            'codehilite',        # 高亮
            'tables',
            'toc',
        ]
        self.md = markdown.Markdown(extensions=extensions)

    def _add_controls(self, html: str) -> str:
        """
        为每个 <pre><code>...</code></pre> 插入控制元素：
          <button class='fold-btn'>收起</button>
          <button class='copy-btn'>复制</button>
        """
        def _repl(m):
            pre_tag = m.group(0)
            # 代码块第一行前插入按钮
            controls = ('<button class="fold-btn">收起</button>'
                        '<button class="copy-btn">复制</button>')
            return '<div>' + controls + '\n' + pre_tag + '</div>'

        return re.sub(r'<pre[^>]*><code[^>]*>.*?</code></pre>',
                      _repl, html, flags=re.DOTALL)

    def convert(self, md_text: str) -> str:
        """把 markdown 文本渲染成完整 HTML"""
        body_html = self.md.convert(md_text)
        body_html = self._add_controls(body_html)

        full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>Markdown Preview</title>
  <link rel="stylesheet" href="{self.CSS_URL}">
  <style>
    body {{ box-sizing: border-box; padding: 2em; max-width: 1012px; margin: 0 auto; }}
    .fold-btn, .copy-btn {{
      background: #eee; border: 1px solid #bbb; border-radius: 3px;
      padding: 4px 8px; margin-right: 6px; cursor: pointer; font-size: 0.75em;
    }}
  </style>
</head>
<body>
  <article class="{self.WRAPPER_CSS}">
    {body_html}
  </article>
  {self.EXTRA_JS}
</body>
</html>"""
        return full_html

# =====================
# 简易 CLI，可直接 `python md2html.py file.md > out.html`
if __name__ == "__main__":
    import sys
    tool = Markdown2GithubHtml()
    md_path = Path(sys.argv[1])
    md_text = md_path.read_text(encoding='utf-8')
    Path(sys.argv[2]).write_text(tool.convert(md_text), encoding='utf-8')
