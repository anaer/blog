---
title: JavaScript的解构赋值语法
date: "2023-04-14T16:23:01.000Z"
description: JavaScript的解构赋值语法
tags:
  - javascript
last_updated: "2023-04-14T16:23:01.000Z"
---

## `const {path: filePath, originalFilename} = params.files.file` 的含义

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