# BrainBridge 使用说明

## 1. 总览

BrainBridge 现在按标准可编辑安装方式使用：

```bash
python3 -m pip install -e .
```

当前推荐导入方式是直接使用包路径：

```python
from src.public.run_lib.requests_core.request_core import Request
from src.public.run_lib.provider_converter.converter import Converter
from src.public.static_lib.logger.log_core import Logger
```

仓库里的旧 bootstrap 辅助文件已经从现行源码树中移除。

## 2. 运行时结构

- `src/public/run_lib/files_manager`：文件与路径工具
- `src/public/run_lib/mini_tools`：小型运行时工具
- `src/public/run_lib/terminial_core`：内置终端 raw 输入后端
- `src/public/run_lib/provider_converter`：provider 配置与参数转换
- `src/public/run_lib/requests_core`：请求内核与线程请求工具
- `src/public/static_lib/logger`：结构化日志
- `src/public/static_lib/checker`：检查与备份恢复工具
- `src/public/static_lib/information`：输出内置 JSON 信息

## 3. 依赖策略

核心运行时现在只使用标准库。

已移除的第三方运行时依赖：

- `requests`
- `chardet`
- `pynput`

当前替代方案：

- HTTP 由 `urllib` 处理
- 编码检测由 `src.public.run_lib.mini_tools.chardet.detect` 处理
- 终端按键监听由 `src.public.run_lib.terminial_core.keyboard` 处理

## 4. 常见导入示例

### 4.1 文件工具

```python
from src.public.run_lib.files_manager.manager import (
    read_file,
    read_json,
    return_full_tree,
    valid_path,
    write_content_tofile,
)
```

### 4.2 请求

```python
from src.public.run_lib.requests_core.request_core import Request

requester = Request(timeout=30)
response = requester.get("https://example.com")
print(response.status_code)
print(response.text)
```

### 4.3 线程请求

```python
from src.public.run_lib.requests_core.request_core import Request
from src.public.run_lib.requests_core.thread_requests.thread_requests import RequestPool, RequestTask

requester = Request(timeout=30)
pool = RequestPool(requester)
tasks = [
    RequestTask("a", "get", ("https://example.com",)),
    RequestTask("b", "get", ("https://example.org",)),
]
results = pool.execute_all(tasks)
```

### 4.4 Provider 转换

```python
from src.public.run_lib.provider_converter.converter import Converter, Operator

payload = Converter(
    "openai_completion",
    model="openai/gpt-oss-20b",
    messages=[{"role": "user", "content": "hello"}],
    stream=True,
).information

headers = Operator.HeadersBuilder.builder("token")
```

### 4.5 日志

```python
from src.public.static_lib.logger.log_core import Logger, LogLevels

logger = Logger(level=LogLevels.INFO, text="hello")
print(logger.text_log_builder())
```

### 4.6 终端交互

```python
from src.public.run_lib.mini_tools.decision_panel import DecisionPanelPage

page = DecisionPanelPage(operation_tips="Use arrow keys or WASD.")
page.set_options([
    {"prompt": "Open", "output": "open"},
    {"prompt": "Exit", "output": "exit"},
])
result = page.run_once()
```

`DecisionPanelPage` 现在使用 `src.public.run_lib.terminial_core` 里的 raw 终端后端。
默认用 `Enter` 确认，`Tab` 也会按同样的确认动作处理。
这个后端刻意保留了一小部分 `pynput` 风格接口，以兼容已经在用的行为：

- `keyboard.Key`
- `keyboard.KeyCode.from_char()`
- `keyboard.Listener`

## 5. `.bb` 归档工具

主要入口：

```python
from src.public.run_lib.mini_tools.files_convg import (
    aggregate_to_backup,
    has_file_tree_header,
    inject_file_tree_header,
    read_file_tree_header,
    unpack_from_backup,
)
```

说明：

- `.bb` 现为 `BBPACK/3` 格式
- 文件树头是可选的
- 文件树头可以后注入并校验
- sandbox 快照遵循 `base/` 加 `YYYY-MM-DD/` 规则

## 6. 配置

Provider 转换会读取：

- `config/sys_conf/base_arg_match.json`
- `config/sys_conf/escape_table.json`
- `config/user_conf/base_arg_match.json`
- `config/user_conf/escape_table.json`

`user_conf` 会覆盖 `sys_conf`。

## 7. 验证

推荐验证流程：

```bash
python3 -m pip install -e .
python3 -m py_compile $(rg --files -g '*.py' src)
python3 src/.test/test_2.py
python3 src/.test/test_1.py
python3 src/.test/test_7.py
python3 src/.test/test_5.py
python3 -m src.public.static_lib.logger.log_core
```

## 8. 实用说明

- `src/.test/test_5.py` 现在是 decision panel / 终端后端的内部烟雾测试，不再是 `pynput` 检查。
- `write_content_tofile(..., file_code="auto")` 和 `read_file(..., file_code="auto")` 现在使用仓库内置检测器。
- `storage/` 是运行输出目录，不是源码目录。
- 仓库说明保持简洁、准确、可维护。
