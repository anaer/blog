## 服务端排序

```js
$(grid_selector).jqGrid({
    loadonce: false, // 是否一次性加载数据到客户端，启用本地排序
    sortname: 'name',
    sortorder: 'desc',
    colNames: [ 'id', 'name'],
    colModel: [
    {
        index: 'id',
        name: 'id'
    },
    {
        index: 'name',
        name: 'name',
        width: 50,
        sortable: true
    },
    onSortCol: function(index, columnIndex, sortOrder) {
        search();
        return 'stop'; // 阻止客户端排序操作
    },
})

function search() {
  var param = {};
  param.sortName = $(grid_selector).getGridParam("sortname");
  param.sortOrder = $(grid_selector).getGridParam("sortorder");
  ...
}
```