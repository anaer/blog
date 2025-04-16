在使用uv管理python环境后, 需要在进入不同项目时 执行`source .venv/bin/activate`

---

### 使用 `direnv` 工具

1. **安装 `direnv`**：
   ```bash
   apt install direnv
   ```

2. **配置 Shell 环境**（以 Bash 为例）：
   编辑 `~/.bashrc` 文件，添加配置, 如果已配置PS1, 可在现有配置上添加`${VIRTUAL_ENV_PROMPT}`变量：
   ```bash
   eval "$(direnv hook bash)"
   
   export PS1='${VIRTUAL_ENV_PROMPT}${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
   ```
   然后运行 `source ~/.bashrc` 使配置生效。

3. **在目标目录创建 `.envrc` 文件**：
   ```bash
   cd /path/to/target_directory
   vim .envrc
   ```
   
   ```rc
   source .venv/bin/activate
   if [ -z "${VIRTUAL_ENV_PROMPT:-}" ] && [ -n "${VIRTUAL_ENV}" ]; then
       VIRTUAL_ENV_PROMPT=$(basename "${VIRTUAL_ENV}")
   fi
   export VIRTUAL_ENV_PROMPT
   ```

4. **授权 `.envrc`**：
   ```bash
   direnv allow
   ```
   首次进入目录时需执行此命令以允许 `.envrc` 生效。

5. **验证**：
   进入目录时，`direnv` 会自动执行 `.envrc` 中的命令。
   会有PS1告警信息, 暂不知道怎么去掉.

```log
# cd /path/to/target_directory
direnv: loading ~/path/to/target_directory/.envrc
direnv: PS1 cannot be exported. For more information see https://github.com/direnv/direnv/wiki/PS1
direnv: export ~PATH
```
