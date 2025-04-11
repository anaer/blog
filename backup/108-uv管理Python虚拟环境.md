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

- **Python 版本切换**
  ```bash
  uv python install 3.11    # 安装指定版本
  uv python use 3.11        # 切换当前环境版本
  ```