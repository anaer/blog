// 运行时按全站导航数据(nav.json)计算并填充上一页/下一页,
// 使链接始终与最新文章顺序一致, 不依赖该页自身何时被构建。
// nav.json 拉取失败时保留服务端渲染的静态兜底链接。
document.addEventListener("DOMContentLoaded", function () {
    var nav = document.querySelector(".paginate-container[data-nav-url]");
    if (!nav) {
        return;
    }
    var navUrl = nav.getAttribute("data-nav-url");
    var current = (nav.getAttribute("data-post-number") || "").trim();
    var container = nav.querySelector(".pagination");
    if (!navUrl || !current || !container) {
        return;
    }

    function setLink(className, rel, label, item, isPrev) {
        var a = container.querySelector("." + className);
        if (!item) {
            if (a) {
                a.remove();
            }
            return;
        }
        if (!a) {
            a = document.createElement("a");
            a.className = className;
            a.setAttribute("rel", rel);
            a.setAttribute("aria-label", label);
            if (isPrev) {
                container.insertBefore(a, container.firstChild);
            } else {
                container.appendChild(a);
            }
        }
        a.href = item.url;
        a.textContent = item.title;
    }

    fetch(navUrl)
        .then(function (res) {
            return res.ok ? res.json() : null;
        })
        .then(function (list) {
            if (!Array.isArray(list)) {
                return;
            }
            var index = -1;
            for (var i = 0; i < list.length; i++) {
                if (String(list[i].number) === current) {
                    index = i;
                    break;
                }
            }
            if (index < 0) {
                return;
            }
            setLink("previous_page", "previous", "Previous Page", index > 0 ? list[index - 1] : null, true);
            setLink("next_page", "next", "Next Page", index < list.length - 1 ? list[index + 1] : null, false);
        })
        .catch(function () {
            // 静默失败: 保留静态兜底
        });
});
