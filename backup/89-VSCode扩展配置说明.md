
## [Better Cron Tasks](https://marketplace.visualstudio.com/items?itemName=Freaxys.better-cron-tasks)

在workspace的.vscode添加tasks.json任务

```jsonc
{
    // See https://go.microsoft.com/fwlink/?LinkId=733558
    // for the documentation about the tasks.json format
    "version": "2.0.0",
    "tasks": [
      {
        "label": "Auto Sync",
        "type": "shell",
        "command": "D:\\demo\\sync.bat",
        "problemMatcher": []
      }
    ]
}
```

在workspace的settings.json配置中添加定时任务配置, 任务跟workspace

```jsonc
"cronTasks.tasks": [
    {
        "at": "*/5 * * * *", // 每5分钟执行
        "run": "workbench.action.tasks.runTask",
        "args": ["Auto Sync"]  // 对应tasks中的任务label
    },
],
"cronTasks.debug": false // debug模式, 在OUTPUT输出日志
```

需要修改终端的默认Profile为Command Prompt, 选其它可能会有问题