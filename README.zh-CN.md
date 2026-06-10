# BrainBridge

BrainBridge 是一个面向本地开发使用的 Python 工具库，主要覆盖 provider payload 转换、基于 `urllib` 的请求、终端交互、结构化日志，以及 `.bb` 归档工具。

[English](./README.md) | [Instruction Manual](./instruction.md) | [中文使用说明](./instruction.zh-CN.md)

## 安装

使用 Python 3.12+，并在仓库根目录执行：

```bash
python3 -m pip install -e .
```

BrainBridge 按标准包方式使用。新代码应直接从 `brainbridge...` 导入。

## 当前目录结构

- `brainbridge/lib/runtime`
  运行时模块，如 provider 转换、请求、文件工具、终端输入。
  `brainbridge.lib.runtime.file_utils` 是公开的文件工具命名空间；`general.py`、`bb_utils.py` 和 `ignores.py` 只是内部实现划分。
- `brainbridge/lib/static`
  结构化日志、完整性检查、内置信息等静态辅助模块。
- `brainbridge/utils`
  面向应用层的小工具，这部分由旧 `mini_tools` 迁移而来。
- `config/sys_conf`
  默认 provider 配置层。
- `config/user_conf`
  用户覆盖配置层。
- `.test`
  烟雾测试、pytest 入口和 sandbox fixtures。

## 推荐顶层 API

```python
from brainbridge import Converter, Operator, Request, Logger, LogLevels
```

顶层暴露面刻意保持精简，适合常见应用代码，不用于承载所有内部工具。

## 推荐子包 API

### Provider 转换

```python
from brainbridge.lib.runtime.provider_converter import (
    Converter,
    build_headers,
    list_providers,
    provider_exists,
    unwrap_response,
)
```

### 请求

```python
from brainbridge.lib.runtime.requests_core import Request, Response, RequestException, iter_sse_json
```

### 文件

```python
from brainbridge.lib.runtime.file_utils import (
    read_file,
    read_json,
    return_full_tree,
    return_path_of_dir_under_root_dir,
    valid_path,
    write_content_tofile,
    write_json,
)
```

### 终端输入

```python
from brainbridge.lib.runtime.terminal_core import (
    Key,
    KeyCode,
    KeyInput,
    Listener,
    decode_escape_sequence,
    decode_single_char,
    keyboard,
)
```

### 工具集

```python
from brainbridge.utils import (
    DecisionPanelPage,
    Time,
    detect,
    display_loading_bar,
)
```

### 日志

```python
from brainbridge.lib.static.logger import Logger, LogLevels, log_to_file
```

## 清理状态

旧兼容包已经完全删除。

- 历史上的 `run_lib` 结构现在统一使用 `brainbridge.lib.runtime`
- 历史上的 `static_lib` 结构现在统一使用 `brainbridge.lib.static`
- 原先属于 `mini_tools` 的工具面现在统一使用 `brainbridge.utils`

## 运行时依赖策略

BrainBridge 运行时坚持仅使用标准库。

- HTTP 由 `urllib` 处理
- 终端输入由内置 `brainbridge.lib.runtime.terminal_core` 处理
- 编码检测由仓库内的 `brainbridge.utils.chardet.detect` 处理

运行时不应依赖 `requests`、外部 `chardet` 或 `pynput`。

## Provider 配置

Provider 转换会读取并合并：

- `config/sys_conf/base_arg_match.json`
- `config/sys_conf/escape_table.json`
- `config/user_conf/base_arg_match.json`
- `config/user_conf/escape_table.json`

`user_conf` 会覆盖 `sys_conf`。

仓库也提供只写 `user_conf` 的后端工具：

```python
from brainbridge.lib.runtime.provider_converter import (
    read_user_provider_config,
    update_user_provider_config,
    write_user_provider_config,
)
```

这些工具不会写入 `sys_conf`。

## `.bb` 归档格式

BrainBridge 在 `brainbridge.lib.runtime.file_utils` 中提供 `.bb` 备份工具。

当前格式特点：

- 魔术头：`BBPACK/3`
- UTF-8 按行文本容器
- JSON 元数据记录
- Base64 载荷记录
- 可选紧凑文件树头，便于快速检查和校验

主要入口：

- `aggregate_to_backup(...)`
- `unpack_from_backup(...)`
- `has_file_tree_header(...)`
- `read_file_tree_header(...)`
- `inject_file_tree_header(...)`

忽略规则支持：

- `ignores=".pyc"`
- `ignores=[".pyc", ".log"]`
- `ignores={"dir": [".git", "__pycache__"], "file": [".pyc"]}`

字符串和列表形式只作用于文件名，不作用于目录名；目录忽略需要使用字典形式。

## 验证

推荐验证流程：

```bash
python3 -m pip install -e .
python3 -m py_compile $(find brainbridge .test -name '*.py')
python3 -m pytest
```

常用烟雾测试：

```bash
python3 .test/test_2.py
python3 .test/test_1.py
python3 .test/test_5.py
python3 .test/test_7.py
```

## 说明

- `storage/` 已不再是必需的运行时依赖。
- `DecisionPanelPage` 使用内置终端后端，不依赖 `pynput`。
- `Converter(...)` 只有在显式传入时才会带上 `stream`。
- `DecisionPanelPage` 中 `Tab` 与 `Enter` 都会作为确认键。

## 许可证

MIT。
