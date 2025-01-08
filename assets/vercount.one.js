var t, e;
!function() {
    var n, o = [], c = !1;
    function i() {
        c = !0,
        document.removeEventListener("DOMContentLoaded", i),
        o.forEach((t => t.call(document))),
        o = []
    }
    t = {
        fetch: async function(t) {
            try {
                e.hideAll();
                const o = await fetch("https://events.vercount.one/log?jsonpCallback=VisitorCountCallback", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        url: window.location.href
                    })
                })
                  , c = await o.json();
                n(( () => {
                    t(c),
                    localStorage.setItem("visitorCountData", JSON.stringify(c)),
                    e.showAll()
                }
                ))
            } catch (t) {
                console.error("Error fetching visitor count:", t),
                e.hideAll()
            }
        }
    },
    e = {
        counterIds: ["site_pv", "page_pv", "site_uv"],
        updateText: function(t) {
            this.counterIds.forEach((e => {
                const n = document.getElementById("busuanzi_value_" + e);
                n && (n.textContent = t[e] || "0");
                const o = document.getElementById("vercount_value_" + e);
                o && (o.textContent = t[e] || "0")
            }
            ))
        },
        hideAll: function() {
            this.counterIds.forEach((t => {
                const e = document.getElementById("busuanzi_container_" + t);
                e && (e.style.display = "none");
                const n = document.getElementById("vercount_container_" + t);
                n && (n.style.display = "none")
            }
            ))
        },
        showAll: function() {
            this.counterIds.forEach((t => {
                const e = document.getElementById("busuanzi_container_" + t);
                e && (e.style.display = "inline");
                const n = document.getElementById("vercount_container_" + t);
                n && (n.style.display = "inline")
            }
            ))
        }
    },
    (n = function(t) {
        c || "interactive" === document.readyState || "complete" === document.readyState ? t.call(document) : (o.push(t),
        document.addEventListener("DOMContentLoaded", i))
    }
    )(( () => {
        t.fetch(e.updateText.bind(e))
    }
    ))
}();