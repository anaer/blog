在使用 @ConfigurationProperties 绑定 Map 时，Spring Boot 的 松散绑定 (Relaxed Binding) 机制会默认移除 Key 中的特殊字符（如斜杠 /、中划线 - 等）以进行规范化处理。

解决方案：使用方括号 [] 包裹 Key
要保留 Key 中的斜杠或其他特殊字符，你必须在配置文件（YAML 或 Properties）中使用 方括号语法。
1. YAML 配置示例

```yaml
my:
  config:
    map:
      "[/api/v1/user]": "value1"
      "[/auth/login]": "value2"
```

* 关键点：必须使用双引号包裹整个 Key，且 Key 内部使用 []。

2. Properties 配置示例

```ini
my.config.map.[/api/v1/user]=value1
my.config.map.[/auth/login]=value2
```

3. Java 代码接收

```java
@Component
@ConfigurationProperties(prefix = "my.config")
public class MyProperties {
    private Map<String, String> map;
    // getter and setter
}
```

为什么斜杠会丢失？
Spring Boot 在处理 Map 的 Key 时，如果 Key 没有被 [] 包裹，它会尝试应用松散绑定规则。在此规则下： [1, 2] 

* / 会被视作路径分隔符或非法字符被剔除。
* my-key 会被转为 myKey。
* 使用 [] 可以显式告诉 Spring “这是一个字面量 Key”，从而跳过松散绑定逻辑，原样保留所有字符。
