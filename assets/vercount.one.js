var visitorCountModule, eventHandler;

(function () {
    var onReadyCallback, callbacks = [], isDOMReady = false;

    // DOM 加载完成后执行所有回调
    function handleDOMReady() {
        isDOMReady = true;
        document.removeEventListener("DOMContentLoaded", handleDOMReady);
        callbacks.forEach(callback => callback.call(document));
        callbacks = [];
    }

    // 访客计数模块
    visitorCountModule = {
        fetch: async function (callback) {
            try {
                // eventHandler.hideAll();
                const response = await fetch("https://events.vercount.one/log?jsonpCallback=VisitorCountCallback", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        url: window.location.href,
                    }),
                });
                const data = await response.json();

                onReadyCallback(() => {
                    callback(data);
                    localStorage.setItem("visitorCountData", JSON.stringify(data));
                    eventHandler.showAll();
                });
            } catch (error) {
                console.error("Error fetching visitor count:", error);
                // eventHandler.hideAll();
            }
        },
    };

    // 事件处理模块
    eventHandler = {
        counterIds: ["site_pv", "page_pv", "site_uv"],

        // 更新计数器文本
        updateText: function (data, skipPage = false) {
            this.counterIds.forEach(id => {
                // 如果 skipPage 为 true，跳过 page_pv
                if (skipPage && id === "page_pv") return;

                const vercountElement = document.getElementById("vercount_value_" + id);
                if (vercountElement) {
                    vercountElement.textContent = data[id] || "0";
                }
            });
        },

        // 隐藏所有计数器
        hideAll: function () {
            this.counterIds.forEach(id => {
                const vercountContainer = document.getElementById("vercount_container_" + id);
                if (vercountContainer) {
                    vercountContainer.style.display = "none";
                }
            });
        },

        // 显示所有计数器
        showAll: function () {
            this.counterIds.forEach(id => {
                const vercountContainer = document.getElementById("vercount_container_" + id);
                if (vercountContainer) {
                    vercountContainer.style.display = "inline";
                }
            });
        },

        // 从 localStorage 初始化数据（只更新 site 相关数据）
        initializeFromLocalStorage: function () {
            const cachedData = localStorage.getItem("visitorCountData");
            if (cachedData) {
                try {
                    const data = JSON.parse(cachedData);
                    this.updateText(data, true); // 跳过 page_pv
                    this.showAll();
                } catch (error) {
                    console.error("Error parsing cached data:", error);
                }
            }
        },
    };

    // DOM 加载完成后执行回调
    onReadyCallback = function (callback) {
        if (isDOMReady || document.readyState === "interactive" || document.readyState === "complete") {
            callback.call(document);
        } else {
            callbacks.push(callback);
            document.addEventListener("DOMContentLoaded", handleDOMReady);
        }
    };

    // 初始化：从 localStorage 加载数据并获取最新数据
    onReadyCallback(() => {
        // 从 localStorage 初始化数据（只更新 site 相关数据）
        eventHandler.initializeFromLocalStorage();

        // 获取最新数据并更新页面（更新所有数据）
        visitorCountModule.fetch(eventHandler.updateText.bind(eventHandler));
    });
})();