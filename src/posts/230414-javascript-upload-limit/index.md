---
title: JavaScript文件上传限制文件类型
date: "2023-04-14T16:28:42.000Z"
description: JavaScript文件上传限制文件类型
tags:
  - javascript
last_updated: "2023-04-14T16:28:42.000Z"
---

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
