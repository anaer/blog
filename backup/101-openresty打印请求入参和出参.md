可以将配置放到http, server, location下, 用于不同范围
需修改白名单whitelist, 只打印关心的接口, 防止日志太多

```
    # 初始化变量
    set $req_headers "";
    set $req_body "";
    set $resp_headers "";
    set $resp_body "";

    access_by_lua_block {
        -- 捕获请求头
        local headers = ngx.req.get_headers()
        local headers_str = ""
        for k, v in pairs(headers) do
            headers_str = headers_str .. "  " .. k .. ": " .. v .. "\n"
        end
        ngx.var.req_headers = headers_str

        -- 捕获请求体
        ngx.req.read_body()
        local body = ngx.req.get_body_data()
        if not body then
            local file = ngx.req.get_body_file()
            if file then
                local f = io.open(file, "rb")
                body = f:read("*all")
                f:close()
            end
        end
        ngx.var.req_body = body or "-"
    }

    body_filter_by_lua_block {
        local chunk = ngx.arg[1]
        if chunk then
            ngx.var.resp_body = (ngx.var.resp_body or "") .. chunk
        end
    }

    log_by_lua_block {
        -- 定义白名单 URI
        local whitelist = {
            ["/translate"] = true,
            ["/test2"] = true
        }
        -- 获取当前请求的 URI
        local uri = ngx.var.uri
        -- 检查是否在白名单中
        if whitelist[uri] then
            local resp_headers = ngx.resp.get_headers()
            local headers_str = ""
            for k, v in pairs(resp_headers) do
                headers_str = headers_str .. "  " .. k .. ": " .. v .. "\n"
            end
            ngx.var.resp_headers = headers_str

            local log_entry = string.format(
                "\nRequest: %s\nHeaders: \n%sBody: %s\n\nResponse Status: %s\nHeaders: \n%sBody: %s\n",
                ngx.var.request,
                ngx.var.req_headers,
                ngx.var.req_body,
                ngx.var.status,
                ngx.var.resp_headers,
                ngx.var.resp_body or "-"
            )

            ngx.log(ngx.INFO, log_entry)
        else
            ngx.log(ngx.INFO, uri)
        end
    }
```