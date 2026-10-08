document.addEventListener("DOMContentLoaded", function() {
    console.log("\n %c TOC Plugins https://github.com/anaer/Gmeek \n", "padding:5px 0;background:#C333D0;color:#fff");

    let css = `
    @media (max-width: 1249px)
    {
        .toc{
            position:static;
            top:auto;
            left:auto;
            transform:none;
            padding:10px;
            margin-bottom:20px;
            width:100%;
        }
    }

    .toc {
        position:fixed;
        top:120px;
        left:50%;
        transform: translateX(50%) translateX(320px);
        width:200px;
        border: 1px solid var(--color-border-default);
        border-radius: 6px;
        padding: 10px;
        overflow-y: auto;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        max-height: 70vh;
    }
    .toc-title{
        font-weight: bold;
        text-align: center;
        border-bottom: 1px solid var(--color-border-muted);
        padding-bottom: 8px;
    }
    .toc-end{
        font-weight: bold;
        text-align: center;
        visibility: visible;
    }
    .toc a {
        display: block;
        color: var(--color-diff-blob-addition-num-text);
        text-decoration: none;
        padding: 5px 0;
        font-size: 14px;
        line-height: 1.5;
        border-bottom: 1px solid var(--color-border-muted);
    }
    .toc a:last-child {
        border-bottom: none;
    }
    .toc a:hover {
        background-color: var(--color-select-menu-tap-focus-bg);
    }

    /* 高亮背景须随主题, 否则深色下与浅色文字同色, 当前项不可见 */
    .toc-link.active {
        font-weight: bold;
        background-color: var(--color-accent-subtle);
    }

    /* 子节点默认折叠, 滚动到所在小节时由脚本展开 */
    .toc-item {
        position: relative;
    }
    .toc-item:not(.open) > .toc-children {
        display: none;
    }
    .toc-toggle {
        position: absolute;
        /* right-align: 切换按钮贴在每行右内侧, 与右侧面板内边距 2px 齐;
           左侧不再预留槽位, 链接文字可直接从缩进位起 */
        right: 2px;
        top: 4px;
        display: inline-flex;
        padding: 2px 4px;
        border: none;
        background: transparent;
        cursor: pointer;
        border-radius: 4px;
        color: var(--fgColor-muted, var(--color-fg-muted));
        opacity: .6;
        line-height: 1;
        transition: opacity .2s, background .2s;
    }
    .toc-toggle:hover {
        opacity: 1;
        background: var(--bgColor-muted, var(--color-canvas-subtle));
    }
    .toc-toggle .ic-minus { display: none; }
    .toc-item.open .toc-toggle .ic-plus { display: none; }
    .toc-item.open .toc-toggle .ic-minus { display: inline-block; }
`;

    // 切换按钮占位(右对齐): 按钮 12px 图标 + 左右 4px 内边距 + 4px 缓冲, 共 22px
    // 左侧不再预留槽位, 缩进只由 (level - 1) * 10 决定
    const TOGGLE_SLOT = 22;

    let contentContainer = document.getElementById('content');
    if (!contentContainer) {
        return;
    }
    const headings = contentContainer.querySelectorAll('h1, h2, h3, h4, h5, h6');
    if (headings.length === 0) {
        return;
    }

    let tocElement = document.createElement('div');
    tocElement.className = 'toc';
    contentContainer.prepend(tocElement);

    tocElement.insertAdjacentHTML('afterbegin', '<div class="toc-title">目录</div>');

    // 构建层级树: 每个标题挂到最近的上级标题下(按级别判定)
    const items = Array.from(headings).map(function(heading) {
        return {
            heading: heading,
            level: parseInt(heading.tagName.charAt(1)),
            parent: null,
            children: [],
            link: null,
            childrenEl: null,
            wrapper: null,
            expanded: false
        };
    });
    const itemByHeading = new Map();
    const itemByWrapper = new Map();
    const stack = [];
    items.forEach(function(item) {
        if (!item.heading.id) {
            item.heading.id = item.heading.textContent.trim().replace(/\s+/g, '-').toLowerCase();
        }
        while (stack.length && stack[stack.length - 1].level >= item.level) {
            stack.pop();
        }
        item.parent = stack.length ? stack[stack.length - 1] : null;
        if (item.parent) {
            item.parent.children.push(item);
        }
        stack.push(item);
        itemByHeading.set(item.heading, item);
    });

    // 渲染: 每个节点 = 切换按钮(有子节点时) + 链接 + 子节点容器(默认折叠)
    items.forEach(function(item) {
        const wrapper = document.createElement('div');
        wrapper.className = 'toc-item';

        if (item.children.length > 0) {
            wrapper.classList.add('has-children');
            const toggle = document.createElement('button');
            toggle.className = 'toc-toggle';
            toggle.setAttribute('aria-label', '折叠/展开');
            // 图标统一取自 base.html 的 renderIcon(单一数据源 icons.py)
            if (typeof renderIcon === 'function') {
                toggle.innerHTML = renderIcon('plus', 12, 'ic-plus') + renderIcon('minus', 12, 'ic-minus');
            }
            wrapper.appendChild(toggle);
        }

        const link = document.createElement('a');
        link.href = '#' + item.heading.id;
        link.textContent = item.heading.textContent;
        link.className = 'toc-link';
        // 缩进 = 每级 10px, 左侧无切换按钮占位(按钮已挪到右侧);
        // 右侧预留 TOGGLE_SLOT 防止长标题与按钮重叠
        const padBase = (item.level - 1) * 10;
        link.style.paddingLeft = `${padBase}px`;
        link.style.paddingRight = `${TOGGLE_SLOT}px`;
        wrapper.appendChild(link);

        const childrenEl = document.createElement('div');
        childrenEl.className = 'toc-children';
        wrapper.appendChild(childrenEl);

        item.link = link;
        item.childrenEl = childrenEl;
        item.wrapper = wrapper;
        itemByWrapper.set(wrapper, item);

        if (item.parent) {
            item.parent.childrenEl.appendChild(wrapper);
        } else {
            tocElement.appendChild(wrapper);
        }
    });

    tocElement.insertAdjacentHTML('beforeend', '<a class="toc-end" onclick="window.scrollTo({top:0,behavior: \'smooth\'})">↑ Top ↑</a>');

    const style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);

    // 视口顶部基准线: 标题顶边越过该线即视为当前小节
    const OFFSET = 100;

    function currentHeading() {
        // 已滚动到底部时高亮最后一个标题(末尾小节可能始终越不过基准线)
        if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2) {
            return headings[headings.length - 1];
        }
        let current = null;
        for (let i = 0; i < headings.length; i++) {
            if (headings[i].getBoundingClientRect().top - OFFSET <= 0) {
                current = headings[i];
            } else {
                break;
            }
        }
        return current;
    }

    // 仅在目录容器内部滚动以保持高亮项可见, 不触碰页面滚动
    function scrollTocToLink(link) {
        if (tocElement.scrollHeight <= tocElement.clientHeight) {
            return;
        }
        const top = link.offsetTop;
        const bottom = top + link.offsetHeight;
        if (top < tocElement.scrollTop) {
            tocElement.scrollTop = top;
        } else if (bottom > tocElement.scrollTop + tocElement.clientHeight) {
            tocElement.scrollTop = bottom - tocElement.clientHeight;
        }
    }

    let activeItem = null;

    // 应用状态: 展开「当前项 + 其所有祖先」分支, 其余折叠; 同步高亮
    function applyState(item) {
        const activeChanged = item !== activeItem;

        const expanded = new Set();
        let node = item;
        while (node) {
            expanded.add(node);
            node = node.parent;
        }

        let expandedChanged = false;
        items.forEach(function(it) {
            const shouldExpand = expanded.has(it) && it.children.length > 0;
            if (shouldExpand !== it.expanded) {
                it.expanded = shouldExpand;
                it.wrapper.classList.toggle('open', shouldExpand);
                expandedChanged = true;
            }
        });

        if (activeChanged) {
            if (activeItem) {
                activeItem.link.classList.remove('active');
            }
            activeItem = item;
            if (activeItem) {
                activeItem.link.classList.add('active');
            }
        }

        if (activeItem && (activeChanged || expandedChanged)) {
            scrollTocToLink(activeItem.link);
        }
    }

    function updateActive() {
        const heading = currentHeading();
        applyState(heading ? itemByHeading.get(heading) : null);
    }

    let ticking = false;
    function onScroll() {
        if (ticking) {
            return;
        }
        ticking = true;
        window.requestAnimationFrame(function() {
            updateActive();
            ticking = false;
        });
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll, { passive: true });
    updateActive();

    // 点击: 平滑滚动到标题, 并立即高亮/展开对应分支
    tocElement.querySelectorAll('a.toc-link').forEach(function(link) {
        link.addEventListener('click', function(event) {
            const href = link.getAttribute('href') || '';
            if (href.charAt(0) !== '#') {
                return;
            }
            event.preventDefault();
            const targetId = href.substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                history.pushState(null, null, '#' + targetId);
                const item = itemByHeading.get(targetElement);
                if (item) {
                    applyState(item);
                }
            }
        });
    });

    // 点击 +/− 切换: 手动展开/折叠该节点的子目录(独立于滚动自动跟随)
    tocElement.querySelectorAll('button.toc-toggle').forEach(function(btn) {
        btn.addEventListener('click', function(event) {
            event.stopPropagation();
            const wrapper = btn.closest('.toc-item');
            const item = itemByWrapper.get(wrapper);
            if (item) {
                item.wrapper.classList.toggle('open');
            }
        });
    });
});
