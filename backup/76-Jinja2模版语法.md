### Jinja2模版语法

---

#### 一、基础语法结构
1. **变量输出**
   ```jinja2
   {{ variable }}                {# 基础输出 #}
   {{ variable|default("N/A") }} {# 设置默认值 #}
   {{ user.name|title }}         {# 过滤器链式操作 #}
   ```

2. **逻辑控制**
   ```jinja2
   {% if score > 90 %}
     优秀
   {% elif score > 60 %}
     合格
   {% else %}
     不合格
   {% endif %}
   ```

3. **循环结构**
   ```jinja2
   {% for item in items %}
     <li>{{ loop.index }}. {{ item.name }}</li>
   {% else %}
     <p>暂无数据</p>
   {% endfor %}
   ```

---

#### 二、模板继承系统
1. **父模板定义** (`base.html`)
   ```jinja2
   <!DOCTYPE html>
   <html>
   <head>
     {% block head %}
       <title>{% block title %}默认标题{% endblock %}</title>
     {% endblock %}
   </head>
   <body>
     {% block content %}{% endblock %}
   </body>
   </html>
   ```

2. **子模板扩展**
   ```jinja2
   {% extends "base.html" %}

   {% block title %}子页面标题{% endblock %}

   {% block content %}
     <h1>{{ self.title() }}</h1>
     {% include "partials/nav.html" %}
   {% endblock %}
   ```

---

#### 三、高级功能组件
1. **宏（Macros）**
   ```jinja2
   {% macro input(name, value='', type='text') %}
     <input type="{{ type }}" 
            name="{{ name }}" 
            value="{{ value|e }}" 
            class="form-control">
   {% endmacro %}

   {{ input('username') }}               {# 调用宏 #}
   {{ input('email', type='email') }}    {# 带参数覆盖 #}
   ```

2. **过滤器（Filters）**
   ```jinja2
   {{ text|trim|upper }}                  {# 内置过滤器 #}
   {{ list|join(', ') }}                  {# 列表转字符串 #}
   {{ date|datetime(format='%Y-%m-%d') }} {# 自定义过滤器 #}
   ```

3. **测试器（Tests）**
   ```jinja2
   {% if variable is defined %}      {# 检查变量存在性 #}
   {% if number is even %}           {# 数值类型测试 #}
   {% if string is sequence %}       {# 可迭代对象检测 #}
   ```

---

#### 四、安全控制机制
1. **自动转义**
   ```jinja2
   {{ user_input }}                {# 自动HTML转义 #}
   {{ safe_html|safe }}            {# 标记安全内容 #}
   {% autoescape false %}          {# 关闭局部转义 #}
     {{ raw_content }}
   {% endautoescape %}
   ```

2. **沙箱模式限制**
   ```jinja2
   {# 在受限环境中禁止以下操作： #}
   {% forbidden_tag %}             {# 禁用危险标签 #}
   {{ __import__('os') }}          {# 禁止Python函数调用 #}
   ```

---

#### 五、空白控制
```jinja2
{% for item in list -%}   {# 移除行首空白 #}
  {{ item }}
{%- endfor %}             {# 移除行尾空白 #}

{# 输出结果无空行： #}
{% if true %}...{% endif %}
```

---

#### 六、注释语法
```jinja2
{# 单行注释 #}

{#
  多行注释
  模板调试时使用
#}

{{ "注释内容不会出现在输出中" }}
```

---

#### 七、包含与导入
1. **文件包含**
   ```jinja2
   {% include 'header.html' ignore missing %}  {# 忽略缺失文件 #}
   ```

2. **模块化组织**
   ```jinja2
   {% from 'forms.html' import input as field %}  {# 导入单个宏 #}
   {% import 'macros.html' as macros %}           {# 导入整个模块 #}
   ```

---
