## Continue

```
C:\Users\Administrator\.continue\config.json
```

```json
{
  "tabAutocompleteModel": {
    "title": "Pro/Qwen/Qwen2.5-Coder-7B-Instruct | ME",
    "model": "Pro/Qwen/Qwen2.5-Coder-7B-Instruct",
    "apiBase": "http://myecs/v1/",
    "contextLength": 32000,
    "provider": "siliconflow"
  },
  "models": [
    {
      "title": "Qwen/Qwen2.5-Coder-32B-Instruct | ME",
      "model": "Qwen/Qwen2.5-Coder-32B-Instruct",
      "apiBase": "http://myecs/v1/",
      "contextLength": 32000,
      "provider": "siliconflow"
    },
    {
      "title": "deepseek-ai/DeepSeek-R1 | ME",
      "model": "deepseek-ai/DeepSeek-R1",
      "apiBase": "http://myecs/v1/",
      "contextLength": 32000,
      "provider": "siliconflow"
    }
  ],
  "customCommands": [
    {
      "name": "test",
      "prompt": "{{{ input }}}\n\nWrite a comprehensive set of unit tests for the selected code. It should setup, run tests that check for correctness including important edge cases, and teardown. Ensure that the tests are complete and sophisticated. Give the tests just as chat output, don't edit any file.",
      "description": "Write unit tests for highlighted code"
    }
  ],
  "contextProviders": [
    {
      "name": "code",
      "params": {}
    },
    {
      "name": "docs",
      "params": {}
    },
    {
      "name": "diff",
      "params": {}
    },
    {
      "name": "terminal",
      "params": {}
    },
    {
      "name": "problems",
      "params": {}
    },
    {
      "name": "folder",
      "params": {}
    },
    {
      "name": "codebase",
      "params": {}
    }
  ],
  "slashCommands": [
    {
      "name": "share",
      "description": "Export the current chat session to markdown"
    },
    {
      "name": "cmd",
      "description": "Generate a shell command"
    },
    {
      "name": "commit",
      "description": "Generate a git commit message"
    }
  ]
}
```

## Codegeex

```json
  "Codegeex.Local": {
    "apiURL": "http://myecs/v1/chat/completions",
    "useChatGLM": true,
    "chatGLM": {
      "apiKey": "",
      "model": "Qwen/Qwen2.5-Coder-32B-Instruct"
    },
    "chat": {
      "useDefaultSystemPrompt": true,
      "systemPrompt": "",
      "temperature": 0.2,
      "top_p": 0.95,
      "max_tokens": 1024,
      "presence_penalty": 1
    },
    "completions": {
      "useDefaultSystemPrompt": true,
      "systemPrompt": "",
      "temperature": 0.2,
      "top_p": 0.95,
      "max_tokens": 64,
      "presence_penalty": 1
    }
  },
```