### Fastjson 特性开关

1.2.83

---

#### **一、序列化特性 (SerializerFeature)**

com.alibaba.fastjson.serializer.SerializerFeature

| 特性名称                          | 默认状态 | 功能描述                                                                 |
|-----------------------------------|----------|--------------------------------------------------------------------------|
| **QuoteFieldNames**               | 启用     | 字段名用双引号包裹                                                       |
| **UseSingleQuotes**               | 禁用     | 使用单引号代替双引号                                                     |
| **WriteMapNullValue**             | 禁用     | 序列化时输出值为 `null` 的字段                                            |
| **WriteEnumUsingToString**        | 禁用     | 序列化枚举值时调用 `toString()` 方法                                       |
| **WriteEnumUsingName**        | 启用     | 序列化枚举值时调用 `name()` 方法                                       |
| **UseISO8601DateFormat**        | 禁用     | 使用ISO8601日期格式                                       |
| **WriteNullListAsEmpty**          | 禁用     | 1.1 将 `null` 的集合字段输出为 `[]`                                           |
| **WriteNullStringAsEmpty**        | 禁用     | 1.1 将 `null` 的字符串字段输出为 `""`                                         |
| **WriteNullNumberAsZero**         | 禁用     | 1.1 将 `null` 的数值字段输出为 `0`                                            |
| **WriteNullBooleanAsFalse**       | 禁用     | 1.1 将 `null` 的布尔字段输出为 `false`                                        |
| **SkipTransientField**            | 启用     | 1.1 忽略被 `transient` 修饰的字段                                             |
| **SortField**                     | 启用     | 1.1 排序字段                                             |
| ~~WriteTabAsSpecial~~                     | 禁用     | 1.1.1 把\t做转义输出                                            |
| **PrettyFormat**                  | 禁用     | 1.1.2 格式化输出（缩进和换行）                                                  |
| **WriteClassName**                | 禁用     | 1.1.2 输出 `@type` 字段（支持多态反序列化）                                     |
| **DisableCircularReferenceDetect**| 禁用     | 1.1.6 禁用循环引用检测（提升性能，但可能栈溢出）                                |
| **WriteSlashAsSpecial**             | 禁用     | 1.1.9 对斜杠'/'进行转义                             |
| **BrowserCompatible**             | 禁用     | 1.1.10 对 Unicode 特殊字符进行转义（兼容浏览器场景）                             |
| **WriteDateUseDateFormat**        | 禁用     | 1.1.14 使用全局日期格式（需配置 `JSON.DEFFAULT_DATE_FORMAT`）                    |
| **NotWriteRootClassName**         | 禁用     | 1.1.15 不输出根类名                                                             |
| ~~DisableCheckSpecialChar~~         | 禁用     | 1.1.19 如果有特殊字符如双引号,将会在转成json时带有反斜杠转义符                                                            |
| **BeanToArray**                   | 禁用     | 1.1.35 将 Java 对象序列化为 JSON 数组（按字段定义顺序）                          |
| **WriteNonStringKeyAsString**   | 禁用     | 1.1.37 将非字符串类型字段序列化为字符串形式                                         |
| **NotWriteDefaultValue**   | 禁用     | 1.1.42 不设默认值                                        |
| **BrowserSecure**   | 禁用     | 1.2.6 浏览器安全,将<>()字符做转义输出                                        |
| **IgnoreNonFieldGetter**   | 禁用     | 1.2.7 忽略为空的属性                                         |
| **WriteNonStringValueAsString**   | 禁用     | 1.2.9 将非字符串类型值序列化为字符串形式                                         |
| **IgnoreErrorGetter**   | 禁用     | 1.2.11 忽略那些抛错的getter方法                                        |
| **WriteBigDecimalAsPlain**        | 禁用     | 1.2.16 将 `BigDecimal` 序列化为普通数值（不科学计数法）                          |
| **MapSortField**   | 禁用     | 1.2.27 对Map中的键值对进行排序                                        |

---

#### **二、反序列化特性 (Feature)**

com.alibaba.fastjson.parser.Feature

| 特性名称                          | 默认状态 | 功能描述                                                                 |
|-----------------------------------|----------|--------------------------------------------------------------------------|
| **AutoCloseSource**               | 启用     | 自动关闭输入流                                                          |
| **AllowComment**                  | 禁用     | 允许 JSON 中包含 `//` 或 `/* */` 注释                                     |
| **AllowUnQuotedFieldNames**       | 启用     | 允许字段名不加双引号                                                     |
| **AllowSingleQuotes**             | 启用     | 允许字段值使用单引号                                                     |
| **InternFieldNames**              | 启用     | 缓存字段名（提升性能）                                                   |
| **AllowISO8601DateFormat**                 | 禁用     | 识别和处理 ISO 8601 标准的时间格式                              |
| **AllowArbitraryCommas**                 | 启用     | 允许在JSON字符串中存在任意逗号，即使它们不在键值对之间                              |
| **UseBigDecimal**                 | 启用     | 将浮点数解析为 `BigDecimal`（避免精度丢失）                               |
| **IgnoreNotMatch**                | 启用     | 1.1.3 忽略无法匹配的字段（不抛异常）                                            |
| **SortFeidFastMatch**                 | 启用     | 1.1.3 排序字段优先匹配                              |
| **DisableASM**                 | 禁用     | 1.1.3 禁用ASM                              |
| **DisableCircularReferenceDetect**                 | 禁用     | 1.1.7 是否检测循环引用                              |
| **InitStringFieldAsEmpty**                 | 禁用     | 1.1.10 对于没有值得字符串属性设置为空串                              |
| **SupportArrayToBean**            | 禁用     | 1.1.35 允许将 JSON 数组反序列化为 JavaBean                                       |
| **OrderedField**                  | 禁用     | 1.2.3 按字段定义顺序解析 JSON                                                   |
| **DisableSpecialKeyDetect**                 | 禁用     | 1.2.5 关闭特殊字符的转义                              |
| **UseObjectArray**                 | 禁用     |  1.2.9                               |
| **SupportNonPublicField**                 | 禁用     | 1.2.22, 1.1.54.android                               |
| **IgnoreAutoType**                 | 禁用     | 1.2.29                              |
| **DisableFieldSmartMatch**        | 禁用     | 1.2.30 禁用字段名智能匹配（如驼峰转下划线）                                      |
| **SupportAutoType**               | 禁用     | 1.2.41, backport to 1.1.66.android 允许通过 `@type` 自动反序列化多态类型（高危，需白名单控制）                |
| **NonStringKeyAsString**                 | 禁用     | 1.2.42                              |
| **CustomMapDeserializer**                 | 禁用     | 1.2.45                              |
| **ErrorOnEnumNotMatch**                 | 禁用     | 1.2.55                              |
| **SafeMode**                 | 禁用     | 1.2.68                              |
| **TrimStringFieldValue**                 | 禁用     | 1.2.72                              |
| **UseNativeJavaObject**                 | 禁用     | 1.2.77 use HashMap instead of JSONObject, ArrayList instead of JSONArray                            | 

---

#### **三、全局安全配置 (ParserConfig)**

com.alibaba.fastjson.parser.ParserConfig

| 配置项                          | 默认值  | 功能描述                                                                 |
|---------------------------------|---------|--------------------------------------------------------------------------|
| **AutoTypeSupport**             | `false` | 是否启用 `@type` 自动类型推断（强烈建议保持关闭）                         |
| **SafeMode**                    | `false` | 严格模式（仅允许反序列化内置基础类型，需手动配置白名单）                  |
| **AsmEnable**                   | `true`  | 启用 ASM 字节码技术加速反序列化                                           |
| **DefaultClassLoader**          | `null`  | 指定类加载器用于加载反序列化类                                            |
| **CheckAutoType**               | `true`  | 反序列化时检查类名是否在白名单中                                           |
| **AutoTypeCheckHandler**        | `null`  | 自定义 `@type` 校验处理器                                                  |
| **DenyClassNames**              | 内置    | 默认拒绝反序列化的危险类列表（如 `java.lang.ProcessBuilder`）            |

---

#### **四、其他全局配置**

com.alibaba.fastjson.JSON

| 配置项                          | 默认值  | 功能描述                                                                 |
|---------------------------------|---------|--------------------------------------------------------------------------|
| **JSON.DEFAULT_DATE_FORMAT**    | `null`  | 全局日期格式（如 `"yyyy-MM-dd HH:mm:ss"`）                               |
| **JSON.DEFAULT_GENERATE_FEATURE**| 动态   | 全局默认启用的序列化特性掩码                                             |
| **JSON.DEFAULT_PARSER_FEATURE** | 动态    | 全局默认启用的反序列化特性掩码                                           |

---
