// 运行时按全站标签数据(nav.json)计算并渲染「关联文章」:
// 关联度 = 与当前文章共享的标签数; 同分沿用 nav.json 的列表序(置顶优先、更新时间降序)。
// nav.json 每次构建全量重写, 因此新增或改标签都不必回刷旧文章页。
var RELATED_LIMIT = 5;

document.addEventListener("DOMContentLoaded", function () {
    var box = document.querySelector(".related-posts[data-nav-url]");
    if (!box) {
        return;
    }

    function hide() {
        box.remove();
    }

    var navUrl = box.getAttribute("data-nav-url");
    var current = (box.getAttribute("data-post-number") || "").trim();
    var labels = readLabels(box.getAttribute("data-labels"));
    if (!navUrl || !current || !labels.length) {
        hide();
        return;
    }

    fetch(navUrl)
        .then(function (res) {
            return res.ok ? res.json() : null;
        })
        .then(function (list) {
            if (!Array.isArray(list)) {
                hide();
                return;
            }
            var hits = [];
            for (var i = 0; i < list.length; i++) {
                var item = list[i];
                if (String(item.number) === current || !Array.isArray(item.labels)) {
                    continue;
                }
                var score = sharedCount(labels, item.labels);
                if (score > 0) {
                    hits.push({item: item, score: score});
                }
            }
            // Array.prototype.sort 稳定: 同分条目保持 nav.json 的列表序
            hits.sort(function (a, b) {
                return b.score - a.score;
            });
            if (!hits.length) {
                hide();
                return;
            }
            render(box, hits.slice(0, RELATED_LIMIT));
        })
        .catch(hide);
});

function readLabels(raw) {
    if (!raw) {
        return [];
    }
    try {
        var parsed = JSON.parse(raw);
        return Array.isArray(parsed) ? parsed : [];
    } catch (e) {
        return [];
    }
}

function sharedCount(a, b) {
    var score = 0;
    for (var i = 0; i < a.length; i++) {
        if (b.indexOf(a[i]) !== -1) {
            score++;
        }
    }
    return score;
}

function render(box, hits) {
    var heading = document.createElement("div");
    heading.className = "related-heading";
    heading.textContent = box.getAttribute("data-heading");
    box.appendChild(heading);

    for (var i = 0; i < hits.length; i++) {
        var item = hits[i].item;
        var link = document.createElement("a");
        link.className = "SideNav-item d-flex flex-items-center";
        link.href = item.url;

        var icon = document.createElement("span");
        // 图标走单一数据源(base.html 的 renderIcon, 由 icons.py 注入)
        icon.innerHTML = typeof renderIcon === "function"
            ? renderIcon("post", 16, "SideNav-icon octicon") : "";
        link.appendChild(icon);

        var title = document.createElement("span");
        title.className = "related-item-title";
        title.textContent = item.title;
        link.appendChild(title);

        box.appendChild(link);
    }
}
