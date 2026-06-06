# BrainBridge 使用说明

[English instruction](./instruction.md) | 中文使用说明 | [项目首页](./README.md) | [中文首页](./README.zh-CN.md)

本文档是仓库当前状态下的实际使用说明。
它面向的是希望直接在本地仓库中运行这些模块的人。

## 1. 适用范围

BrainBridge 是一个仓库内工具集，不需要先打包成 wheel 才能使用。
大多数模块都需要先做一次路径引导，再执行导入。

当前仓库提供两层引导：

- `src/bootstrap_source_dir.py` 会把仓库 `src` 目录加入 `sys.path`
- `src/bootstrap_paths.py` 会查找 `run_lib` 和 `static_lib`，然后把其中一个加入 `sys.path`

一些子包里也保留了本地版 `bootstrap_source_dir.py`，这样这些模块可以直接在子包目录中执行。

## 2. 环境

推荐流程：

1. 激活自带虚拟环境
2. 安装 `requirements.txt` 里的依赖
3. 在修改运行时代码之前先跑一次烟雾测试

常用命令：

```bash
source .venv/Scripts/activate
pip install -r requirements.txt
python src/bootstrap_paths.py
python src/.test/test_2.py
```

当前依赖包括：

- `requests`
- `chardet`
- `pynput`

其中 `pynput` 是终端交互工具所必需的。

## 3. 导入方式

如果你从仓库根目录运行代码，先使用根目录的引导模块。

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

注意事项：

- `change_sys_path(to_runlib=True)` 和 `change_sys_path(to_staticlib=True)` 只能二选一
- 用完之后要调用 `restore_sys_path()`
- 用完 `src` 引导后要调用 `_restore_sys_path()`
- 不要把旧名字 `simple_import.py` 和 `set_source_dir.py` 再加回来

## 4. 模块说明

### 4.1 `src/bootstrap_paths.py`

函数：

- `packages_path()`
- `change_sys_path(to_runlib=False, to_staticlib=False)`
- `restore_sys_path()`

这个模块用于把 `src/public/run_lib` 或 `src/public/static_lib` 加入 `sys.path`。

行为：

- `packages_path()` 会从仓库根目录搜索并返回 `run_lib` 和 `static_lib`
- `change_sys_path()` 要求两个布尔参数里只有一个为 `True`
- `restore_sys_path()` 会恢复第一次缓存下来的 `sys.path`

### 4.2 `src/bootstrap_source_dir.py`

函数：

- `_set_source_dir()`
- `_restore_sys_path()`

这个模块用于把仓库 `src` 目录加入 `sys.path`。

### 4.3 `src/public/run_lib/files_manager/manager.py`

公开函数：

- `return_path_of_dir_under_root_dir(dir_name)`
- `return_dir_member(dir_path)`
- `valid_path(target_path, is_file=True)`
- `return_full_tree(*base_paths)`
- `write_content_tofile(file_path, content, file_code="utf-8", trailing_newline=True, override=False)`
- `read_file(file_path, line_by_line=False, file_code="utf-8")`
- `read_json(file_path, file_code="utf-8", parse=True)`

实际行为：

- `return_full_tree()` 返回的是嵌套的 list/dict 结构
- 对于权限错误和循环目录，会写入字符串标记
- `write_content_tofile(..., file_code="auto")` 在空文件上会回退到 UTF-8

示例：

```python
from src.bootstrap_source_dir import _set_source_dir
from src.bootstrap_paths import change_sys_path, restore_sys_path

_set_source_dir()
change_sys_path(to_runlib=True)

from files_manager.manager import return_full_tree, write_content_tofile

tree = return_full_tree("src")
write_content_tofile("src/tree.txt", str(tree), override=True)

restore_sys_path()
```

### 4.4 `src/public/run_lib/requests_core/request_core.py`

主类：

- `Request`

支持的方法：

- `get(*urls, ...)`
- `post(*urls, ...)`
- `put(*urls, ...)`
- `delete(*urls, ...)`
- `request_sse(method, url, ...)`

它的作用：

- 用一个对象封装 `requests`
- 支持单 URL 和批量 URL
- 在 `enable_logging=True` 时记录简单日志
- 解析 SSE 流

需要注意：

- 单个 URL 时返回 `requests.Response`
- 多个 URL 时返回以 URL 字符串为键的字典
- `request_sse()` 会返回包含 `id`、`event`、`data` 的事件字典
- 当前 SSE 解析器只会产出带 `data` 的事件

示例：

```python
from src.bootstrap_source_dir import _set_source_dir
from src.bootstrap_paths import change_sys_path, restore_sys_path

_set_source_dir()
change_sys_path(to_runlib=True)

from requests_core.request_core import Request

req = Request(enable_logging=True, timeout=30)
resp = req.get("https://example.com")

restore_sys_path()
```

### 4.5 `src/public/run_lib/requests_core/thread_requests/thread_requests.py`

类：

- `RequestTask`
- `TaskResult`
- `RequestWorker`
- `RequestPool`

这个模块用于并行执行多个请求任务，然后等待全部完成。

示例：

```python
from requests_core.request_core import Request
from requests_core.thread_requests.thread_requests import RequestPool, RequestTask

req = Request(timeout=20)
pool = RequestPool(req)
results = pool.execute_all([
    RequestTask("task-1", "get", ("https://example.com",)),
    RequestTask("task-2", "get", ("https://example.org",)),
])
```

### 4.6 `src/public/run_lib/provider_converter/converter.py`

类：

- `_ConfigEngine`
- `Converter`
- `Operator`

这个模块负责把通用参数转换成 provider 需要的参数格式。

当前配置文件：

- `config/sys_conf/base_arg_match.json`
- `config/sys_conf/escape_table.json`
- `config/user_conf/base_arg_match.json`
- `config/user_conf/escape_table.json`

实际行为：

- 用户配置会覆盖系统默认值
- `Converter` 会先检查 provider 是否存在
- `Converter` 会检查必要参数是否齐全
- 未知的类型 token 会被视为无效
- `Operator.HeadersBuilder.builder(api_token, include_accept=False)` 会返回标准 JSON 请求头
- `Operator.ResponseUnwarp.unwarp(provider, response)` 会返回标准化结果

示例：

```python
from src.bootstrap_source_dir import _set_source_dir
from src.bootstrap_paths import change_sys_path, restore_sys_path

_set_source_dir()
change_sys_path(to_runlib=True)

from provider_converter.converter import Converter, Operator

payload = Converter(
    "openai_completion",
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello"}],
    stream=True,
).information

headers = Operator.HeadersBuilder.builder("sk-example", include_accept=True)

restore_sys_path()
```

### 4.7 `src/public/run_lib/mini_tools/timer.py`

主类：

- `Time`

常用成员：

- `Time.Timer(precision)`
- `Time.Timer.passed()`
- `Time.Timer.reset()`
- `Time.f_time(time_part)`

适合用于简单的耗时统计和时间格式化。

### 4.8 `src/public/run_lib/mini_tools/loading_bar.py`

主函数：

- `display_loading_bar(_timer, *content, duration=6, speed="mid", method="replace", background=None, size=32, chunk_size=3)`

这是一个纯终端加载条工具，需要传入 `Time` 实例。

### 4.9 `src/public/run_lib/mini_tools/decision_panel.py`

主类：

- `DecisionPanelPage`

这个模块用于终端交互菜单。

限制和要求：

- 依赖 `pynput`
- 需要真实终端，不能当作无头环境工具来用
- `clear_mode` 支持 `system`、`ansi`、`none`

示例：

```python
from src.bootstrap_source_dir import _set_source_dir
from src.bootstrap_paths import change_sys_path, restore_sys_path

_set_source_dir()
change_sys_path(to_runlib=True)

from mini_tools.decision_panel import DecisionPanelPage

page = DecisionPanelPage(title="BrainBridge", operation_tips="Use arrow keys or WASD.")
page.set_options([
    {"prompt": "Run smoke test", "output": "run"},
    {"prompt": "Exit", "output": "exit"},
])
result = page.run_once()

restore_sys_path()
```

### 4.10 `src/public/run_lib/mini_tools/files_convg.py`

公开 API：

- `BackupError`
- `to_posix(path)`
- `is_special_marker(node)`
- `iter_tree_files(tree)`
- `root_prefix_id(root)`
- `relative_under_root(root, file_path)`
- `b64_encode_stream(src, wrap=B64_WRAP)`
- `aggregate_to_backup(tree, output_backup_path, progress_callback=None)`
- `unpack_from_backup(backup_file_path, target_extraction_dir, skip_errors=False, progress_callback=None)`

这个模块用于把目录树打包成文本备份，或者再解包回来。
它是流式文本格式，不是 zip 的替代品。

示例：

```python
from src.bootstrap_source_dir import _set_source_dir
from src.bootstrap_paths import change_sys_path, restore_sys_path

_set_source_dir()
change_sys_path(to_runlib=True)

from files_manager.manager import return_full_tree
from mini_tools.files_convg import aggregate_to_backup, unpack_from_backup

tree = return_full_tree("src/public")
aggregate_to_backup(tree, "storage/backup.bb")
unpack_from_backup("storage/backup.bb", "storage/restored")

restore_sys_path()
```

### 4.11 `src/public/static_lib/checker/checker.py`

主类：

- `CheckTools`

常用方法：

- `decision_making(content, is_fatal=False)`
- `check_py_version()`
- `dependency_check(requirements)`
- `check_code_hash(file_path, expected_hash)`
- `check_file_hash(file_path, expected_hash)`
- `fix_code_file(fix_file_path, backup_path=None)`
- `fix_conf_file(backup_path, target_conf)`
- `fix_backup_file(current_file, backup_path)`

这个模块用于环境检查、文件校验和基于备份的恢复。

注意：

- `check_py_version()` 当前检查的是 Python `3.14.0`
- 仓库本身是在 Python `3.12+` 环境下开发和烟雾测试的，所以这个检查应当当作内部警告，不要当成打包规则

### 4.12 `src/public/static_lib/logger/log_core.py`

公开类：

- `LogLevels`
- `LogPart`
- `LogFormat`
- `LogInformation`
- `Logger`

这个模块用于结构化日志输出。

行为：

- `Logger.json_log_builder()` 返回 JSON 字符串
- `Logger.text_log_builder()` 返回字典
- `Logger.output_log(to_file, display, file_path=None, write_json=True)` 可以写入 `.jsonl` 或直接打印到终端

### 4.13 `src/public/static_lib/information/information.py`

公开函数：

- `display()`

这个工具会输出 `src/public/static_lib/information/config` 目录里的 JSON 文件。
它是诊断工具，不是配置编辑器。

## 5. 常见工作流

### 5.1 构造 provider 请求体并发送请求

```python
from src.bootstrap_source_dir import _set_source_dir, _restore_sys_path
from src.bootstrap_paths import change_sys_path, restore_sys_path

_set_source_dir()
change_sys_path(to_runlib=True)

from provider_converter.converter import Converter
from requests_core.request_core import Request

payload = Converter(
    "openai_completion",
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say hello"}],
).information

req = Request(enable_logging=True, timeout=30)
response = req.post("https://example.com/api", json=payload)

restore_sys_path()
_restore_sys_path()
```

### 5.2 解析 SSE 流

这个示例接着 5.1 使用，复用的是 `req`、`payload` 和 `headers`。

```python
for event in req.request_sse(
    method="POST",
    url="https://example.com/stream",
    json=payload,
    headers=headers,
):
    print(event["data"], end="")
```

### 5.3 输出 JSONL 日志

```python
from src.bootstrap_source_dir import _set_source_dir, _restore_sys_path
from src.bootstrap_paths import change_sys_path, restore_sys_path

_set_source_dir()
change_sys_path(to_staticlib=True)

from logger.log_core import Logger, LogLevels

logger = Logger(level=LogLevels.INFO, text="Ready")
logger.output_log(to_file=True, display=False, file_path="storage/app.jsonl")

restore_sys_path()
_restore_sys_path()
```

### 5.4 检查文件和依赖

```python
from src.bootstrap_source_dir import _set_source_dir, _restore_sys_path
from src.bootstrap_paths import change_sys_path, restore_sys_path

_set_source_dir()
change_sys_path(to_staticlib=True)

from checker.checker import CheckTools

CheckTools.dependency_check(["requests", "chardet"])
CheckTools.check_file_hash("config/sys_conf/base_arg_match.json", "expected_sha256_here")

restore_sys_path()
_restore_sys_path()
```

## 6. 排错

### 导入 `provider_converter` 或 `requests_core` 时报错

确认导入顺序是：

1. `_set_source_dir()`
2. `change_sys_path(to_runlib=True)` 或 `change_sys_path(to_staticlib=True)`
3. 你的业务导入
4. `restore_sys_path()`
5. `_restore_sys_path()`

### 导入 `logger`、`checker` 或 `information` 时报错

使用同样的引导顺序，但在导入这些模块之前调用 `change_sys_path(to_staticlib=True)`。

### 缺少 `pynput`

从 `requirements.txt` 安装依赖。
终端交互界面和 `src/.test/test_5.py` 都需要它。

### `check_py_version()` 对当前解释器报提示

这个方法当前目标版本是 Python `3.14.0`。
仓库本身的日常烟雾测试仍然在 Python `3.12+` 上进行。

### `write_content_tofile(..., file_code="auto")` 作用在新空文件上

现在会回退到 UTF-8。

### `src/` 或 `storage/` 下出现生成文件

如果它们只是烟雾测试输出，请清理掉。
不要把运行时产物当成源码提交。

## 7. 扩展项目

如果你新增一个运行时代码模块：

- 放到 `src/public/run_lib` 或 `src/public/static_lib`
- 使用 snake_case 文件名
- 导入保持本地、明确、直接
- 如果公共接口变了，记得同步更新 README 和本说明
- 在 `src/.test` 下补一个烟雾测试

如果你新增一个 provider 方案：

- 更新 `config/sys_conf/base_arg_match.json`
- 更新 `config/sys_conf/escape_table.json`
- 如果需要用户自定义，再同步 `config/user_conf`

## 8. 参考命令

开发时常用的命令：

```bash
python src/bootstrap_paths.py
python src/.test/test_2.py
python src/.test/test_1.py
python src/public/static_lib/logger/log_core.py
python -m py_compile src/bootstrap_paths.py src/bootstrap_source_dir.py
```

这些检查覆盖了路径引导、导入链、文件树工具和日志模块。
