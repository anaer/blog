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
        border: 1px solid #e1e4e8;
        border-radius: 6px;
        padding: 10px;
        overflow-y: auto;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        max-height: 70vh;
    }
    .toc-title{
        font-weight: bold;
        text-align: center;
        border-bottom: 1px solid #ddd;
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
        border-bottom: 1px solid #e1e4e8;
    }
    .toc a:last-child {
        border-bottom: none;
    }
    .toc a:hover {
        background-color: var(--color-select-menu-tap-focus-bg);
    }

    .toc-link.active {
        font-weight: bold;
        background-color: #b6e3ff;
    }

    /* 子节点默认折叠, 滚动到所在小节时由脚本展开 */
    .toc-children.collapsed {
        display: none;
    }
`;

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
            expanded: false
        };
    });
    const itemByHeading = new Map();
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

    // 渲染: 每个节点 = 链接 + 子节点容器(默认折叠)
    items.forEach(function(item) {
        const wrapper = document.createElement('div');
        wrapper.className = 'toc-item';

        const link = document.createElement('a');
        link.href = '#' + item.heading.id;
        link.textContent = item.heading.textContent;
        link.className = 'toc-link';
        link.style.paddingLeft = `${(item.level - 1) * 10}px`;
        wrapper.appendChild(link);

        const childrenEl = document.createElement('div');
        childrenEl.className = 'toc-children collapsed';
        wrapper.appendChild(childrenEl);

        item.link = link;
        item.childrenEl = childrenEl;

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
                it.childrenEl.classList.toggle('collapsed', !shouldExpand);
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
});
