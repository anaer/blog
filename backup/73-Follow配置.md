
## 自动化

### Webhook

POST 请求, 会将feed条目信息作为Json参数进行请求, 所以如果要较好处理的话, 可能需要自定义一个webhook接口进行处理

```jsonp
{'entry': {'id': 'xxx', 'publishedAt': '2025-02-06T06:31:29.669Z', 'insertedAt': '2025-02-06T06:42:55.467Z', 'feedId': '85248513348230144', 'title': "xxx", 'description': 'xxx', 'content': 'xxx', 'author': None, 'url': 'xxx', 'guid': 'xxx', 'media': [{'url': 'xxx', 'type': 'photo', 'width': 492, 'height': 656}]}, 'feed': {'title': 'xxx', 'description': 'xxx', 'siteUrl': 'https://xxx', 'image': 'https://xxx', 'checkedAt': '2025-02-06T06:42:55.466Z', 'ttl': 30, 'url': 'https://xxxx', 'lastModifiedHeader': 'Thu, 06 Feb 2025 06:42:54 GMT', 'etagHeader': '"ee35-WBbJJibnAIpo+80xxx/iPxbcxxx"', 'errorMessage': None, 'errorAt': None}, 'view': 5}
```

如果直接配置bark接口地址, 因为参数命名凑巧一致的情况下, 能推送成功一条空标题的消息, 内容为条目url链接
后期要看Follow是否会对一些推送接口进行适配.

## Follow Feed分享页自动订阅

因为目前主要在Web端使用, 在分享页订阅时 老是要跳转下载客户端. 所以实现该脚本: 
1. 从链接获取feed id 
2. 查询feed信息接口 判断是否订阅 
3. 调用feed订阅接口 进行订阅, 设定临时分类 

有需要再进行优化

```js
// ==UserScript==
// @name         Follow分享页 自动订阅
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  从当前页面 URL 中提取最后一段数字 ID
// @author       anaer
// @match        https://app.follow.is/share/feeds/*
// @grant        GM_addStyle
// @grant        GM_xmlhttpRequest
// @grant        unsafeWindow
// ==/UserScript==

(function() {
    'use strict';

  const xget = (url, type = 'json') => new Promise((success, fail) => {
	GM_xmlhttpRequest({
		method: 'GET',
		timeout: 3000,
    credentials: 'include', // 携带浏览器 Cookies
		url: url,
		responseType: type,
		onload: success,
		onerror: fail,
		ontimeout: fail
	});
});

  const xpost = (url, data={}) => new Promise((success, fail) => {
	GM_xmlhttpRequest({
		method: 'POST',
		timeout: 3000,
    credentials: 'include', // 携带浏览器 Cookies
    headers: {
        'Content-Type': 'application/json', // 设置请求头
    },
		url: url,
    data: data,
		responseType: 'json',
		onload: success,
		onerror: fail,
		ontimeout: fail
	});
});

    // 获取当前页面的 URL
    const currentUrl = window.location.href;

    // 使用正则表达式提取最后一段数字 ID
    const match = currentUrl.match(/\/(\d+)\/?$/);

    var id;
    if (match && match[1]) {
        id = match[1];
        console.log('提取的数字 ID:', id);
    } else {
        console.log('未找到数字 ID');
    }

    let url = 'https://api.follow.is/feeds?id='+id
			xget(url).then(r => {
				const ra = r.response;
				console.log(url, ra);

        if (ra.data.subscription) {
          console.log('已订阅');
        }else{
          console.log('未订阅');
          let feed = unsafeWindow.__HYDRATE__['feeds.$get,query:id='+id]['feed']

          var data = JSON.stringify({
              feedId: feed.id,
              url: feed.url,
              view: 0,
              category: "待定"
            });
          xpost('https://api.follow.is/subscriptions', data).then(r => {
            const ra = r.response;
            console.log('订阅成功', data, ra)
          })
          .catch (e => {
            console.log('订阅失败');
          });
        }

			})
			.catch (e => {
				console.log(url, '获取feed信息异常');
			});

})();
```