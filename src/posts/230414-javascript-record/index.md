---
title: JavaScript记录
date: "2023-04-14T16:23:01.000Z"
description: JavaScript记录
tags:
  - javascript
last_updated: "2023-04-25T16:40:22.000Z"
---

## 解构赋值语法

`const {path: filePath, originalFilename} = params.files.file` 的含义

这是 JavaScript 中的解构赋值语法，假设 `params` 对象中有一个名为 `files` 的属性，该属性的值是一个对象，包含一个名为 `file` 的属性，其值也是一个对象。
那么，这段代码可以将 `params.files.file` 对象中的 `path` 属性和 `originalFilename` 属性分别赋值给 `filePath` 和 `originalFilename` 两个变量。

具体来说，假设 `params.files.file` 内容如下：

```javascript
{
  path: '/uploads/file-123456.jpg',
  originalFilename: 'test.jpg'
}
```

执行以后：

```javascript
const {path: filePath, originalFilename} = params.files.file;
console.log(filePath); // '/uploads/file-123456.jpg'
console.log(originalFilename); // 'test.jpg'
```

这种解构赋值语法可以简化代码，使得可以快速访问和使用对象属性。

## 上传文件类型限制


如果希望限制上传文件只能是图片和视频类型，可以在判断文件类型的逻辑中，判断上传文件的 MIME 类型是否以 `image/` 或 `video/` 开头。

举个例子:

```javascript
const fs = require('fs');
const express = require('express');
const app = express();

app.post('/upload', function (req, res, next) {
  const {path: filepath, type:filetype} = req.files.file;

  if (!/^image\//.test(filetype) && !/^video\//.test(filetype)) {
    // 不是允许的文件类型，删除临时文件
    fs.unlink(filepath, function (err) {
      if (err) console.log(err);
      console.log('临时文件删除成功！');
    });
    res.status(400).send('只支持上传图片和视频文件');
  } else {
    res.status(200).send('文件上传成功！');
  }
});
```
