Elasticsearch 常用的 `QueryBuilder` 类及其查询语法

### 常用的 `QueryBuilder` 类及其使用方法

1. **`match` 查询**
   - **说明**：用于全文本搜索，支持分词和模糊匹配。
   - **示例**：
     ```java
     MatchQueryBuilder matchQuery = QueryBuilders.matchQuery("字段名", "查询词");
     ```

2. **`term` 查询**
   - **说明**：用于精确匹配某个字段的值, 单一关键词搜索，不进行分词
   - **示例**：
     ```java
     TermQueryBuilder termQuery = QueryBuilders.termQuery("字段名", "精确值");
     ```

3. **`bool` 查询**
   - **说明**：用于组合多个查询条件，支持 AND/OR/NOT 等逻辑。
   - **示例**：
     ```java
     BoolQueryBuilder boolQuery = QueryBuilders.boolQuery()
         .must(QueryBuilders.matchQuery("字段名1", "查询词1"))
         .should(QueryBuilders.matchQuery("字段名2", "查询词2"))
         .mustNot(QueryBuilders.matchQuery("字段名3", "查询词3"));
     ```

4. **`nested` 查询**
   - **说明**：用于搜索嵌套文档。
   - **示例**：
     ```java
     NestedQueryBuilder nestedQuery = QueryBuilders.nestedQuery("nested_field",
         QueryBuilders.matchQuery("nested_field.nested_doc.sub_field", "nested_value"));
     ```

5. **`range` 查询**
   - **说明**：用于范围查询。查找在指定范围内的文档，例如时间范围查询
   - **示例**：
     ```java
     RangeQueryBuilder rangeQuery = QueryBuilders.rangeQuery("字段名")
         .gte("开始值")
         .lte("结束值");
     ```

6. **`match_phrase` 查询**
   - **说明**：用于短语查询，匹配整个短语。
   - **示例**：
     ```java
     MatchPhraseQueryBuilder matchPhraseQuery = QueryBuilders.matchPhraseQuery("字段名", "短语查询词");
     ```

7. **`exists` 查询**
   - **说明**：用于检查字段是否存在。
   - **示例**：
     ```java
     ExistsQueryBuilder existsQuery = QueryBuilders.existsQuery("字段名");
     ```

8. **`exists` 查询的嵌套文档**
   - **说明**：用于检查嵌套字段是否存在。
   - **示例**：
     ```java
     NestedQueryBuilder nestedExistsQuery = QueryBuilders.nestedQuery("nested_field",
         QueryBuilders.existsQuery("nested_field.nested_doc.sub_field"));
     ```

9. **`terms` 查询**
   - **说明**：用于多值查询。
   - **示例**：
     ```java
     TermsQueryBuilder termsQuery = QueryBuilders.termsQuery("字段名", "值1", "值2", "值3");
     ```

10. **`fuzzy` 查询**
    - **说明**：用于模糊查询，允许一定程度的错误。
    - **示例**：
      ```java
      FuzzyQueryBuilder fuzzyQuery = QueryBuilders.fuzzyQuery("字段名", "模糊查询词");
      ```

11. **`prefix` 查询**
    - **说明**：用于前缀匹配。查询字段值以指定前缀开头的文档
    - **示例**：
      ```java
      PrefixQueryBuilder prefixQuery = QueryBuilders.prefixQuery("字段名", "前缀");
      ```

12. **`wildcard` 查询**
    - **说明**：用于通配符匹配，支持 `*` 和 `?` 通配符。
    - **示例**：
      ```java
      WildcardQueryBuilder wildcardQuery = QueryBuilders.wildcardQuery("字段名", "查询词*");
      ```
