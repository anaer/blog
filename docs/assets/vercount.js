let visitorCountModule, eventHandler;

(function () {
    let onReadyCallback, callbacks = [], isDOMReady = false;

    // DOM 加载完成后执行所有回调
    function handleDOMReady() {
        isDOMReady = true;
        document.removeEventListener("DOMContentLoaded", handleDOMReady);
        callbacks.forEach(callback => callback.call(document));
        callbacks = [];
    }

    // 生成浏览器指纹的哈希值
    const generateBrowserFingerprint = () => {
        const screenInfo = `${window.screen.width}x${window.screen.height}x${window.screen.colorDepth}`;
        const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone || "";
        const languages = navigator.languages ?
        navigator.languages.join(",") : navigator.language || "";

        // 通过WebGL获取显卡信息
        const gl = document.createElement("canvas").getContext("webgl");
        const gpuInfo = gl ? gl.getParameter(gl.RENDERER) : "";

        const rawString = [
        screenInfo,
        timeZone,
        languages,
        navigator.userAgent,
        gpuInfo,
        new Date().getTimezoneOffset()
        ].join("|");

        // 生成哈希值
        let hash = 0;
        for (let i = 0; i < rawString.length; i++) {
        hash = (hash << 5) - hash + rawString.charCodeAt(i);
        hash &= hash; // 转换为32位整数
        }
        return Math.abs(hash).toString(36);
    };

    const browserToken = generateBrowserFingerprint();

    // 访客计数模块
    visitorCountModule = {
        fetch: async function (callback) {
            try {
                const response = await fetch("https://events.vercount.one/api/v2/log", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-Browser-Token": browserToken
                    },
                    body: JSON.stringify({
                        url: window.location.href,
                        token: browserToken
                    }),
                });
                const data = await response.json();

                onReadyCallback(() => {
                    callback(data);
                    localStorage.setItem("visitorCountData", JSON.stringify(data));
                });
            } catch (error) {
                console.error("Error fetching visitor count:", error);
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