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
/* 按钮插在标题内部(见下方 h.insertBefore), 故选择器须跨过标题层级;
   若写成直系子代 .heading-section > .section-toggle 则一条都不会匹配 */
.heading-section > :is(h1,h2,h3,h4,h5,h6) > .section-toggle {
    display: inline-flex;
    /* 图标定尺 14px: 用「0.35em(半字高) - 7px(半盒高)」把盒底定到基线, 使图标中心落在字高中心;
       直接用 middle 会对齐到 x-height 中线, 视觉偏低约 0.1em */
    vertical-align: calc(0.35em - 7px);
    margin-right: 6px;
    border: none;
    background: transparent;
    cursor: pointer;
    padding: 0;
    color: var(--fgColor-muted, var(--color-fg-muted));
    opacity: .6;
    line-height: 1;
    transition: opacity .2s;
}
/* 行内文本控件不设 hover 背景(标题行中会像一枚误入的方块), 反馈只靠透明度 */
.heading-section > :is(h1,h2,h3,h4,h5,h6) > .section-toggle:hover {
    opacity: 1;
}
.heading-section > :is(h1,h2,h3,h4,h5,h6) > .section-toggle .ic-chevron {
    transition: transform .2s ease;
}
.heading-section.collapsed > :is(h1,h2,h3,h4,h5,h6) > .section-toggle .ic-chevron {
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
        // 图标统一取自 base.html 的 renderIcon(单一数据源 icons.py)
        toggle.innerHTML = (typeof renderIcon === 'function') ? renderIcon('chevron', 14, 'ic-chevron') : '';

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
