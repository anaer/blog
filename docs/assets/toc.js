document.addEventListener("DOMContentLoaded", function() {
    console.log("\n %c TOC Plugins https://github.com/anaer/Gmeek \n","padding:5px 0;background:#C333D0;color:#fff");

    let css = `
    .toc {
        position:fixed;
        top:130px;
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
        background-color:var(--color-select-menu-tap-focus-bg);
    }

    .toc-link.active {
        font-weight: bold;
        background-color: #b6e3ff;
    }

    @media (max-width: 1249px)
    {
        .toc{
            position:static;
            top:auto;
            left:auto;
            transform:none;
            padding:10px;
            margin-bottom:20px;
            max-height: 40vh;
            width:60%;
        }
    }`;

    let contentContainer = document.getElementById('content');
    const headings = contentContainer.querySelectorAll('h1, h2, h3, h4, h5, h6');
    if (headings.length === 0) {
        return;
    }

    let tocElement = document.createElement('div');
    tocElement.className = 'toc';
    contentContainer.prepend(tocElement);

    tocElement.insertAdjacentHTML('afterbegin', '<div class="toc-title toc-link">'+document.title+'</div>');
    headings.forEach(heading => {
        if (!heading.id) {
            heading.id = heading.textContent.trim().replace(/\s+/g, '-').toLowerCase();
        }
        const link = document.createElement('a');
        link.href = '#' + heading.id;
        link.textContent = heading.textContent;
        link.className = 'toc-link';
        link.style.paddingLeft = `${(parseInt(heading.tagName.charAt(1)) - 1) * 10}px`;
        tocElement.appendChild(link);
    });
    tocElement.insertAdjacentHTML('beforeend', '<a class="toc-end" onclick="window.scrollTo({top:0,behavior: \'smooth\'});">↑ Top ↑</a>');

    const style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);

    // 高亮显示当前所在位置
    window.addEventListener('scroll', function () {
        let currentHeading = null;

        headings.forEach(heading => {
            const rect = heading.getBoundingClientRect();
            if (rect.top <= 0 && rect.bottom > 0) {
                currentHeading = heading;
            }
        });

        document.querySelectorAll('.toc-link').forEach(link => {
            link.classList.remove('active');
        });

        if (currentHeading) {
            const activeLink = tocElement.querySelector(`a[href="#${currentHeading.id}"]`);
            if (activeLink) {
                activeLink.classList.add('active');
                tocElement.scrollTop = activeLink.offsetTop - tocElement.offsetTop;
            }
        }
    });
});