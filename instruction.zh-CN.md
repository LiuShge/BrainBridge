# BrainBridge 使用说明

## 1. 总览

BrainBridge 现在按标准可编辑安装方式使用：

```bash
python3 -m pip install -e .
```

当前推荐导入方式是直接使用包路径：

```python
from brainbridge.run_lib.requests_core.request_core import Request
from brainbridge.run_lib.provider_converter.converter import Converter
from brainbridge.static_lib.logger.log_core import Logger
```

仓库里的旧 bootstrap 辅助文件已经从现行源码树中移除。

## 2. 运行时结构

- `brainbridge/run_lib/files_manager`：文件与路径工具
- `brainbridge/run_lib/mini_tools`：小型运行时工具
- `brainbridge/run_lib/terminal_core`：内置终端 raw 输入后端
- `brainbridge/run_lib/provider_converter`：provider 配置与参数转换
- `brainbridge/run_lib/requests_core`：请求内核与线程请求工具
- `brainbridge/static_lib/logger`：结构化日志
- `brainbridge/static_lib/checker`：检查与备份恢复工具
- `brainbridge/static_lib/information`：输出内置 JSON 信息
- `.test`：烟雾测试和 sandbox fixture

## 3. 依赖策略

核心运行时现在只使用标准库。

已移除的第三方运行时依赖：

- `requests`
- `chardet`
- `pynput`

当前替代方案：

- HTTP 由 `urllib` 处理
- 编码检测由 `brainbridge.run_lib.mini_tools.chardet.detect` 处理
- 终端按键监听由 `brainbridge.run_lib.terminal_core.keyboard` 处理

## 4. 常见导入示例

### 4.1 文件工具

```python
from brainbridge.run_lib.files_manager.manager import (
    read_file,
    read_json,
    return_full_tree,
    valid_path,
    write_content_tofile,
)
```

### 4.2 请求

```python
from brainbridge.run_lib.requests_core.request_core import Request

requester = Request(timeout=30)
response = requester.get("https://example.com")
print(response.status_code)
print(response.text)
```

### 4.3 线程请求

```python
from brainbridge.run_lib.requests_core.request_core import Request
from brainbridge.run_lib.requests_core.thread_requests.thread_requests import RequestPool, RequestTask

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
from brainbridge.run_lib.provider_converter.converter import Converter, Operator

payload = Converter(
    "openai_completion",
    model="openai/gpt-oss-20b",
    messages=[{"role": "user", "content": "hello"}],
    stream=True,
).information

headers = Operator.HeadersBuilder.builder("token")
parsed = Operator.ResponseUnwrap.unwrap("openai_completion", {"choices": []})
```

说明：

- `stream` 只有在显式传入时才会进入 payload。
- 优先使用 `Operator.ResponseUnwrap.unwrap(...)`；`ResponseUnwarp` 和 `unwarp()` 仍保留为兼容别名。

### 4.5 日志

```python
from brainbridge.static_lib.logger.log_core import Logger, LogLevels

logger = Logger(level=LogLevels.INFO, text="hello")
print(logger.text_log_builder())
```

### 4.6 终端交互

```python
from brainbridge.run_lib.mini_tools.decision_panel import DecisionPanelPage

page = DecisionPanelPage(operation_tips="Use arrow keys or WASD.")
page.set_options([
    {"prompt": "Open", "output": "open"},
    {"prompt": "Exit", "output": "exit"},
])
result = page.run_once()
```

`DecisionPanelPage` 使用 `brainbridge.run_lib.terminal_core` 里的 raw 终端后端。
默认用 `Enter` 确认，`Tab` 也会按同样的确认动作处理。
这个后端刻意保留了一小部分 `pynput` 风格接口，以兼容已经在用的行为：

- `keyboard.Key`
- `keyboard.KeyCode.from_char()`
- `keyboard.Listener`

## 5. `.bb` 归档工具

主要入口：

```python
from brainbridge.run_lib.mini_tools.files_convg import (
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

### 5.1 记录级格式规范

`.bb` 文件是 UTF-8 文本，每一行都是一条逻辑记录：

```text
BBPACK/3
META {"kind":"backup","version":3,"b64_wrap":76,"chunk_size":1048576}
META {"kind":"root","root_id":"<sha16>","root_posix":"<root path>"}
META {"kind":"tree_header","format":"compact-tree-v1","line_count":N,"sha256":"<digest>"}   # 可选
TREE_BEGIN
TREE_DATA <base64 编码后的 JSON 文件树头>                                                      # 可选
TREE_END                                                                                        # 可选
FILE_BEGIN
FILE_META {"root_id":"<sha16>","rel":"root 内相对路径","src_full_posix":"<源路径>","encoding":"b64"}
FILE_DATA <base64 载荷分块>
FILE_CHECK {"size":123,"sha256":"<digest>"}
FILE_END
...
BBPACK_END
```

- 开头的 `META {"kind":"backup",...}` 用来声明格式版本和 Base64 分块元数据。
- 每一条 `META {"kind":"root",...}` 把稳定的 `root_id` 映射回原始根路径。
- 可选的文件树头块保存 `compact-tree-v1` 摘要的 Base64 JSON，并由 `line_count` 和 `sha256` 保护。
- 每个文件记录都以 `FILE_BEGIN` 开始，随后是一个 `FILE_META`、一行或多行 `FILE_DATA`，最后是 `FILE_CHECK` 和 `FILE_END`。

### 5.2 校验与解包规则

- `FILE_DATA` 无论源文件是否是文本，都会以 Base64 文本方式存储。
- 恢复时会同时校验 `FILE_CHECK.size` 和 `FILE_CHECK.sha256`。
- `rel` 必须始终相对于声明的 root；绝对路径和 `..` 路径穿越会被拒绝。
- 如果存在文件树头且启用了校验，展开后的文件列表必须与实际文件记录完全匹配。

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
python3 -m py_compile $(rg --files -g '*.py' .test brainbridge)
python3 .test/test_2.py
python3 .test/test_1.py
python3 .test/test_7.py
python3 .test/test_5.py
python3 -m brainbridge.static_lib.logger.log_core
```

## 8. 实用说明

- `.test/test_5.py` 现在是 decision panel / 终端后端的内部烟雾测试，不再是 `pynput` 检查。
- `write_content_tofile(..., file_code="auto")` 和 `read_file(..., file_code="auto")` 现在使用仓库内置检测器。
- `storage/` 是运行输出目录，不是源码目录。
- 仓库说明保持简洁、准确、可维护。
