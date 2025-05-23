### AI总结

1. AI总结需要在以下地址设置变量信息
https://github.com/anaer/blog/settings/secrets/actions

![Image](https://github.com/user-attachments/assets/33a8b0a5-2b38-42bd-8526-e7e7075b6bd2)

```
API_URL = "https://models.inference.ai.azure.com/chat/completions"
API_KEY = "github_pat_xxxxxxx"
API_MODEL = "gpt-4o"
```

2. API_KEY 需要在以下链接进行创建
https://github.com/settings/personal-access-tokens

GitHub Models key 需要设置Models权限为Read-only

![Image](https://github.com/user-attachments/assets/c1efd265-a865-4440-8b00-fe7d4a0b00cc)

如果未设置权限 会报错
```json
{"error":{"code":"unauthorized","message":"The `models` permission is required to access this endpoint","details":"The `models` permission is required to access this endpoint"}}
```