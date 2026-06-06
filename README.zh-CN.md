# BrainBridge

BrainBridge 是一个适合直接在本仓库中使用的 Python 工具集。
它主要解决这些具体问题：

- 从仓库根目录或子包模块中整理 `sys.path`
- 把通用请求参数转换成具体 provider 需要的请求体
- 使用 `requests` 发送 HTTP 请求并解析 SSE 流
- 运行一个简单的线程请求池
- 显示终端选择面板和加载条
- 读取、写入、校验和打包文件

[English](./README.md) | 中文版本 | [使用说明](./instruction.md) | [中文使用说明](./instruction.zh-CN.md)

## 仓库内容

仓库分成两层运行代码：

- `src/public/run_lib` 放运行时会用到的工具。
- `src/public/static_lib` 放日志、校验和信息读取等辅助工具。
- `src/bootstrap_paths.py` 和 `src/bootstrap_source_dir.py` 是路径引导文件。
- `config/` 保存运行配置和 provider 映射配置。
- `storage/` 只放运行时生成的输出。

这个项目不是框架，也不是包管理器。它是一组可以直接从仓库检出的源码模块。

## 快速开始

1. 激活自带的虚拟环境。

   - PowerShell: `.\.venv\Scripts\Activate.ps1`
   - Unix shell: `source .venv/Scripts/activate`

2. 安装依赖。

   ```bash
   pip install -r requirements.txt
   ```

3. 运行最小化烟雾测试。

   ```bash
   python src/bootstrap_paths.py
   python src/.test/test_2.py
   ```

4. 如果要使用终端交互界面，请先确认环境里已经安装 `pynput`。

## 导入方式

如果从仓库根目录运行代码，先使用根目录的引导模块。

```python
from src.bootstrap_source_dir import _set_source_dir, _restore_sys_path
from src.bootstrap_paths import change_sys_path, restore_sys_path

_set_source_dir()
change_sys_path(to_runlib=True)

from provider_converter.converter import Converter
from requests_core.request_core import Request

restore_sys_path()
_restore_sys_path()
```

如果你直接运行 `src/public/...` 里的文件，请使用那个子包内自带的 `bootstrap_source_dir.py` 复制版。

## 核心模块

| 模块 | 作用 |
| --- | --- |
| `src/bootstrap_paths.py` | 查找 `run_lib` 和 `static_lib`，然后把指定目录加入 `sys.path`。 |
| `src/bootstrap_source_dir.py` | 把仓库的 `src` 目录加入 `sys.path`，并在需要时恢复。 |
| `src/public/run_lib/files_manager/manager.py` | 文件与目录工具：`valid_path`、`read_file`、`read_json`、`write_content_tofile`、`return_full_tree`。 |
| `src/public/run_lib/requests_core/request_core.py` | `Request` 封装，支持 `get`、`post`、`put`、`delete` 和 SSE。 |
| `src/public/run_lib/requests_core/thread_requests/thread_requests.py` | 线程请求池：`RequestTask`、`TaskResult`、`RequestWorker`、`RequestPool`。 |
| `src/public/run_lib/provider_converter/converter.py` | `Converter` 负责 provider 参数映射，`Operator` 负责请求头和响应解析。 |
| `src/public/run_lib/mini_tools/timer.py` | `Time` 和 `Time.Timer`，用于耗时统计和时间格式化。 |
| `src/public/run_lib/mini_tools/loading_bar.py` | 终端加载条。 |
| `src/public/run_lib/mini_tools/decision_panel.py` | 基于 `pynput` 的终端交互菜单。 |
| `src/public/run_lib/mini_tools/files_convg.py` | 目录树打包和解包工具。 |
| `src/public/static_lib/checker/checker.py` | 依赖、版本、文件哈希和备份恢复工具。 |
| `src/public/static_lib/logger/log_core.py` | 结构化日志工具和 `Logger` 类。 |
| `src/public/static_lib/information/information.py` | 输出 `src/public/static_lib/information/config` 下的 JSON 文件。 |

## 配置

provider 转换器会读取下面几份配置：

- `config/sys_conf/base_arg_match.json`
- `config/sys_conf/escape_table.json`
- `config/user_conf/base_arg_match.json`
- `config/user_conf/escape_table.json`

用户配置会覆盖系统默认值中相同的键。

信息模块还会读取：

- `src/public/static_lib/information/config/project_information.json`
- `src/public/static_lib/information/config/py_env_information.json`

## 实际说明

- `Request.request_sse()` 返回的是已经解析好的事件字典，字段包含 `id`、`event`、`data`。
- 当前 SSE 解析器只会产出包含 `data` 的事件。
- `Converter` 只接受合并配置里已经定义过的 provider 方案。
- `DecisionPanelPage` 以及相关终端交互工具需要 `pynput`。
- `CheckTools.check_py_version()` 当前的目标版本是 Python `3.14.0`，虽然仓库本身是在 Python `3.12+` 环境下进行开发和烟雾测试的。
- `write_content_tofile(..., file_code="auto")` 在空文件上会回退到 UTF-8。
- `storage/` 只放运行时输出，不建议放源码。

## 推荐检查

修改路径引导文件或运行时工具后，建议执行：

```bash
python src/bootstrap_paths.py
python src/.test/test_2.py
python src/public/static_lib/logger/log_core.py
```

如果你改了文件树或备份工具，再额外跑：

```bash
python src/.test/test_1.py
```

## 许可证

本项目采用 MIT License。
