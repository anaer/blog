// 正文标题折叠展开: 将每个标题及其后续内容包裹为可折叠 section, 默认展开。
document.addEventListener("DOMContentLoaded", function () {
    const body = document.getElementById('postBody');
    if (!body) {
        return;
    }
    const headings = Array.from(body.querySelectorAll('h1, h2, h3, h4, h5, h6'));
    if (headings.length === 0) {
        return;
    }

    const style = document.createElement('style');
    style.textContent = `
.heading-section { position: relative; }
.heading-section > .section-toggle {
    display: inline-flex;
    vertical-align: middle;
    margin-right: 6px;
    border: none;
    background: transparent;
    cursor: pointer;
    color: inherit;
    opacity: .55;
    padding: 0;
    line-height: 1;
    transition: opacity .2s;
}
.heading-section > .section-toggle:hover { opacity: 1; }
.heading-section > .section-toggle .ic-chevron {
    transition: transform .2s ease;
}
.heading-section.collapsed > .section-toggle .ic-chevron {
    transform: rotate(-90deg);
}
/* 折叠态仅保留标题, 隐藏其余直接子内容(含嵌套 section) */
.heading-section.collapsed > *:not(h1):not(h2):not(h3):not(h4):not(h5):not(h6) {
    display: none;
}
`;
    document.head.appendChild(style);

    const HEADING_RE = /^H[1-6]$/;

    headings.forEach(function (h) {
        const level = parseInt(h.tagName.charAt(1), 10);
        const section = document.createElement('div');
        section.className = 'heading-section';

        const toggle = document.createElement('button');
        toggle.className = 'section-toggle';
        toggle.setAttribute('aria-label', '折叠/展开');
        toggle.innerHTML = '<svg class="ic-chevron" width="14" height="14" viewBox="0 0 16 16" aria-hidden="true"><path fill="currentColor" d="M4 5l4 4 4-4z"/></svg>';

        h.parentNode.insertBefore(section, h);
        section.appendChild(h);
        h.insertBefore(toggle, h.firstChild);

        // 将后续同级或更高级别兄弟节点移入本 section, 直到遇到同级或更高级标题
        let node = section.nextSibling;
        while (node) {
            if (node.nodeType === 1 && HEADING_RE.test(node.tagName)) {
                const l = parseInt(node.tagName.charAt(1), 10);
                if (l <= level) {
                    break;
                }
            }
            const next = node.nextSibling;
            section.appendChild(node);
            node = next;
        }
    });

    // 事件委托: 点击 chevron 切换折叠态(不干扰标题内的链接)
    body.addEventListener('click', function (e) {
        const toggle = e.target.closest('.section-toggle');
        if (toggle) {
            e.preventDefault();
            toggle.closest('.heading-section').classList.toggle('collapsed');
        }
    });
});
