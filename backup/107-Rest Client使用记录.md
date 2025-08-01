

## 自定义变量
### 环境变量
存储不同环境的变量, 在Visual Studio代码设置文件中直接定义.
```json
"rest-client.environmentVariables": {
    "$shared": {
        "version": "v1",
        "prodToken": "foo",
        "nonProdToken": "bar"
    },
    "local": {
        "version": "v2",
        "host": "localhost",
        "token": "{{$shared nonProdToken}}",
        "secretKey": "devSecret"
    },
    "production": {
        "host": "example.com",
        "token": "{{$shared prodToken}}",
        "secretKey" : "prodSecret"
    }
}
```
### 文件变量
表示整个http文件的值, 在http文件中定义, 只有文件范围

`@hostname = api.example.com`

### 请求变量
在http文件中定义, 定义请求变量的响应值, 作为下个请求的参数, 比如先获取token, 再请求

```rest
@baseUrl = https://example.com/api

# @name login
POST {{baseUrl}}/api/login HTTP/1.1
Content-Type: application/x-www-form-urlencoded

name=foo&password=bar

###

@authToken = {{login.response.headers.X-AuthToken}}

# @name createComment
POST {{baseUrl}}/comments HTTP/1.1
Authorization: {{authToken}}
Content-Type: application/json

{
    "content": "fake content"
}

###

@commentId = {{createComment.response.body.$.id}}

# @name getCreatedComment
GET {{baseUrl}}/comments/{{commentId}} HTTP/1.1
Authorization: {{authToken}}

###

# @name getReplies
GET {{baseUrl}}/comments/{{commentId}}/replies HTTP/1.1
Accept: application/xml

###

# @name getFirstReply
GET {{baseUrl}}/comments/{{commentId}}/replies/{{getReplies.response.body.//reply[1]/@id}}
```

### 提示变量
发送请求时 要求用户输入使用的变量

```rest
# @prompt text 请求时弹框提示输入文本
GET https://127.0.0.1/test

{
    "text": "{{text}}",
}
```

## 内置变量

```log
{{$guid}}
{{$randomInt min max}}
{{$timestamp [offset option]}}

{{$datetime}} 时间戳
{{$datetime -3 h}} 3小时前
{{$datetime 2 d}} 2天后

{{$datetime rfc1123|iso8601 [offset option]}}

{{$datetime rfc1123}}       Wed, 16 Apr 2025 06:23:49 GMT
{{$datetime iso8601}}       2025-04-16T06:24:53.379Z
{{$datetime 'YYYY-MM-DD'}}  2025-04-16

{{$localDatetime rfc1123|iso8601 [offset option]}}
使用本地时区
{{$localDatetime rfc1123}}       Wed, 16 Apr 2025 06:23:49 GMT
{{$localDatetime iso8601}}       2025-04-16T14:25:57+08:00
{{$localDatetime 'YYYY-MM-DD'}}  2025-04-16

{{$processEnv [%]envVarName}}
envVarName: 指定本地机器环境变量
%: 可选, 制定时, 将envVarName视为扩展设置环境变量, 并将其值用于查找.

{{$processEnv PATH}} PATH环境变量


{{$dotenv [%]variableName}}
返回.env文件中设置的环境变量, .env文件与.http文件在统一目录中

.env变量定义格式
VAR1=ABC

{{$aadToken [new] [public|cn|de|us|ppe] [<domain|tenantId>] [aud:<domain|tenantId>]}}

{{$oidcAccessToken  [new]  [<clientId:<clientId>] [<callbackPort:<callbackPort>] [authorizeEndpoint:<authorizeEndpoint}] [tokenEndpoint:<tokenEndpoint}] [scopes:<scopes}] [audience:<audience}]}
```

## 取消代理
因为VSCode配置了代理, 而用rest-client时 基本上不要代理, 又没有关代理的配置
虽然rest-client提供了excludeHostsForProxy配置, 域名较多时 不够方便

可以修改以下文件:
c:\Users\Administrator\.vscode\extensions\humao.rest-client-0.25.1\dist\extension.js

修改获取代理配置, 改名, 让找不到代理配置即可
workspace.getConfiguration("http") -> workspace.getConfiguration("http1")

不过环境变量如果配置了http.proxy, 应该还能用, 未测试.
    
## 相关链接
[vscode-restclient](https://github.com/Huachao/vscode-restclient)
    
    