- **新项目**
  使用 `uv init` 命令快速生成项目结构和配置（如 `pyproject.toml`、`.python-version`）:
  ```bash
  uv init my_project
  cd my_project
  
  uv venv --python 3.11 .venv   # 默认生成 .venv 目录
  # 或自定义名称
  uv venv --python 3.12 my_env  # 创建名为 my_env 的环境
  
  source .venv/bin/activate     
  ```

- **现有项目**
  ```bash
  cd existing_project
  uv init
  uv run              # 生成 .venv 环境
  uv add flask
  uv add -r requirements.txt
  ```

- **依赖同步**
  对于已有 `pyproject.toml` 和 `uv.lock` 的项目，快速同步环境:
  ```bash
  uv sync
  ```

- **重新生成requirements.txt**
```bash
uv pip freeze > requirements.txt
```

- **检测并升级依赖**
```bash
uv pip list --outdated
uv pip install --upgrade urllib3
```

- **查看依赖树**
```bash
uv tree
```

- **Python 版本切换**
  ```bash
  # 指定安装镜像 默认到github下载, 可能会慢
  export UV_PYTHON_INSTALL_MIRROR=https://cf.ghproxy.cc/https://github.com/indygreg/python-build-standalone/releases/download
  uv python install 3.11    # 安装指定版本
  uv python use 3.11        # 切换当前环境版本
  ```


- **检测无用依赖**
`uv pip install deptry`

```log
# deptry .
Scanning 7 files...

pyproject.toml: DEP002 'flask' defined as a dependency but not used in the codebase
pyproject.toml: DEP002 'loguru' defined as a dependency but not used in the codebase
Found 2 dependency issues.
```

