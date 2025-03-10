// 全局变量声明
let apiClient, counterManager;

(() => {
  // 模块内部变量
  let scheduleTask, // 定时任务处理器
      pendingTasks = [], // 等待执行的任务队列
      isDOMReady = false; // DOM是否加载完成的标志

  // DOM加载完成处理函数
  function handleDOMReady() {
    isDOMReady = true;
    document.removeEventListener("DOMContentLoaded", handleDOMReady);
    // 执行所有等待的任务
    pendingTasks.forEach(task => task.call(document));
    pendingTasks = [];
  }

  // API地址生成器
  const getAPIEndpoint = (version = 2) =>
    `https://events.vercount.one/api/v${version}/log`;

  // API客户端配置
  apiClient = {
    fetch: async function(callback) {
      const v2API = getAPIEndpoint(2);
      const v1API = getAPIEndpoint(1);

      try {
        counterManager.hideAll();

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
        let currentURL = window.location.href;

        // URL协议验证
        if (!currentURL.startsWith("http")) {
          console.warn("检测到不合规的URL协议，仅支持HTTP和HTTPS");
          currentURL = "https://local.file/invalid-protocol";
        }

        try {
          // 首先尝试v2 API
          const response = await fetch(v2API, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-Browser-Token": browserToken
            },
            body: JSON.stringify({
              url: currentURL,
              token: browserToken
            })
          });

          if (!response.ok) {
            throw new Error(`API响应异常，状态码：${response.status}`);
          }

          // 处理API响应
          const processResponse = (data) => {
            if (!data) return { site_uv: 0, site_pv: 0, page_pv: 0 };

            if (data.status === "success" && data.data) {
              return data.data;
            }

            if (data.status === "error") {
              console.warn("API错误：", data.message, data);
              return data.data || { site_uv: 0, site_pv: 0, page_pv: 0 };
            }

            return data;
          };

          const result = processResponse(await response.json());

          // 更新界面并保存数据到本地存储
          scheduleTask(() => {
            callback(result);
            localStorage.setItem("visitorCountData", JSON.stringify(result));
            counterManager.showAll();
          });

        } catch (v2Error) {
          console.warn("v2 API请求失败，降级使用v1 API：", v2Error);

          try {
            // 尝试带token的v1 API
            const v1Response = await fetch(v1API, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "X-Browser-Token": browserToken
              },
              body: JSON.stringify({
                url: currentURL,
                token: browserToken
              })
            });

            const v1Result = await v1Response.json();

            scheduleTask(() => {
              callback(v1Result);
              localStorage.setItem("visitorCountData", JSON.stringify(v1Result));
              counterManager.showAll();
            });

          } catch (v1Error) {
            console.warn("带token的v1 API请求失败，尝试无token请求：", v1Error);

            // 尝试不带token的v1 API（兼容CORS问题）
            const fallbackResponse = await fetch(v1API, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                url: currentURL,
                token: browserToken
              })
            });

            const fallbackResult = await fallbackResponse.json();

            scheduleTask(() => {
              callback(fallbackResult);
              localStorage.setItem("visitorCountData", JSON.stringify(fallbackResult));
              counterManager.showAll();
            });
          }
        }
      } catch (error) {
        console.error("获取访问量数据失败：", error);

        // 尝试使用本地缓存
        const cachedData = localStorage.getItem("visitorCountData");
        if (cachedData) {
          try {
            const parsedData = JSON.parse(cachedData);
            scheduleTask(() => {
              callback(parsedData);
              counterManager.showAll();
            });
            console.log("使用缓存的访问量数据");
          } catch (parseError) {
            console.error("缓存数据解析失败：", parseError);
            counterManager.hideAll();
          }
        } else {
          counterManager.hideAll();
        }
      }
    }
  };

  // 计数器管理对象
  counterManager = {
    counterIDs: ["site_pv", "page_pv", "site_uv"], // 支持的统计类型

    // 更新页面显示
    updateCounters(data) {
      this.counterIDs.forEach(id => {
        const elements = [
          document.getElementById(`busuanzi_value_${id}`),
          document.getElementById(`vercount_value_${id}`)
        ];

        elements.forEach(element => {
          if (element) {
            element.textContent = data[id] || "0";
          }
        });
      });
    },

    // 隐藏所有计数器
    hideAll() {
      this.counterIDs.forEach(id => {
        ["busuanzi", "vercount"].forEach(prefix => {
          const container = document.getElementById(`${prefix}_container_${id}`);
          if (container) {
            container.style.display = "none";
          }
        });
      });
    },

    // 显示所有计数器
    showAll() {
      this.counterIDs.forEach(id => {
        ["busuanzi", "vercount"].forEach(prefix => {
          const container = document.getElementById(`${prefix}_container_${id}`);
          if (container) {
            container.style.display = "inline";
          }
        });
      });
    }
  };

  // 任务调度器（DOM状态感知）
  scheduleTask = function(taskHandler) {
    if (isDOMReady ||
        document.readyState === "interactive" ||
        document.readyState === "complete"
    ) {
      taskHandler.call(document);
    } else {
      pendingTasks.push(taskHandler);
      document.addEventListener("DOMContentLoaded", handleDOMReady);
    }
  };

  // 初始化：当文档加载完毕时获取统计数据
  scheduleTask(() => {
    apiClient.fetch(counterManager.updateCounters.bind(counterManager));
  });
})();
