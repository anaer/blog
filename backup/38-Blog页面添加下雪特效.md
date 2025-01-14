## snowfall

下载js文件到目录assets/snowfall@1.7下

在base.html添加
```html
    <script src="{{ blogBase['homeUrl'] }}/assets/snowfall@1.7/snowfall.js"></script>
```

在<script>块添加
```js
snowFall.snow(document.body, {round : true, shadow : true, minSize: 5, maxSize:8});
```

其他效果见相关链接

## 相关链接

[JQuery-Snowfall](https://github.com/loktar00/JQuery-Snowfall)