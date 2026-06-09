# BrainBridge 使用说明

本文档描述包结构重整之后，BrainBridge 当前真实可用的公开接口。

## 1. 安装与导入风格

使用可编辑安装：

```bash
python3 -m pip install -e .
```

推荐导入方式：

```python
from brainbridge import Converter, Operator, Request, Logger, LogLevels
from brainbridge.lib.runtime.files_manager import read_json, write_json
from brainbridge.lib.runtime.provider_converter import build_headers, unwrap_response
from brainbridge.utils import DecisionPanelPage, Time, detect, display_loading_bar
```

正常包使用场景下，不要再新增 `sys.path` bootstrap 代码。

## 2. 包结构

- `brainbridge/lib/runtime`
  运行时请求、转换、文件、终端模块。
- `brainbridge/lib/static`
  日志、检查、内置信息等静态辅助模块。
- `brainbridge/utils`
  面向使用者的小工具模块，由旧 `mini_tools` 迁移而来。
- `config/sys_conf`
  默认 provider 配置层。
- `config/user_conf`
  provider 配置覆盖层。
- `.test`
  烟雾测试、pytest 入口和 sandbox fixtures。

旧兼容包已经删除。现在只使用：

- `brainbridge.lib.runtime`
- `brainbridge.lib.static`
- `brainbridge.utils`

## 3. Public / private API 说明

公开 API 以以下导出面为准：

- `brainbridge`
- `brainbridge.lib.runtime.provider_converter`
- `brainbridge.lib.runtime.requests_core`
- `brainbridge.lib.runtime.files_manager`
- `brainbridge.lib.runtime.terminal_core`
- `brainbridge.lib.static.logger`
- `brainbridge.utils`

不要基于以下私有内部实现写新代码：

- `_ConfigEngine`
- `_RawKeyReader`
- 任意以下划线开头的名称

## 4. 顶层 API

```python
from brainbridge import (
    Converter,
    Logger,
    LogLevels,
    Operator,
    Request,
    RequestException,
    Response,
)
```

推荐职责：

- `Converter` 用于 provider payload 转换
- `Operator` 用于构造请求头和解包响应
- `Request` 用于 HTTP / SSE 请求
- `Logger` 与 `LogLevels` 用于结构化日志

## 5. Provider payload 转换

推荐导入：

```python
from brainbridge.lib.runtime.provider_converter import (
    Converter,
    build_headers,
    list_providers,
    provider_exists,
    unwrap_response,
)
```

示例：

```python
payload = Converter(
    "openai_completion",
    model="openai/gpt-oss-20b",
    messages=[{"role": "user", "content": "Hello"}],
).information

headers = build_headers("your-token", include_accept=True)
print(provider_exists("openai_completion"))
print(list_providers()[:3])
```

说明：

- `Converter(...)` 会按合并后的配置 schema 校验 payload。
- `stream` 只有在显式传入时才会进入 payload。
- `build_headers(...)` 内部调用 `Operator.HeadersBuilder.builder(...)`。
- `unwrap_response(...)` 内部调用 `Operator.ResponseUnwrap.unwrap(...)`。

### 直接使用 `ResponseUnwrap`

```python
from brainbridge.lib.runtime.provider_converter import Operator

parsed = Operator.ResponseUnwrap.unwrap(
    "openai_completion",
    {
        "choices": [{"message": {"content": "Paris."}}],
        "usage": {"total_tokens": 1},
    },
)
print(parsed["response_text"])
```

## 6. 请求：GET、POST 与 SSE

推荐导入：

```python
from brainbridge.lib.runtime.requests_core import Request, iter_sse_json
```

### GET

```python
requester = Request(timeout=30)
response = requester.get("https://example.com")
print(response.status_code)
print(response.text)
```

### 带 JSON 的 POST

```python
response = requester.post(
    "https://example.com/api",
    json={"hello": "world"},
)
print(response.ok)
print(response.json())
```

### SSE 请求

```python
events = requester.request_sse(
    "POST",
    "https://example.com/sse",
    json={"stream": True},
    headers={"Authorization": "Bearer token"},
)

for event in events:
    print(event["data"])
```

### SSE JSON helper

```python
for item in iter_sse_json(events):
    print(item)
```

说明：

- `iter_sse_json(...)` 接收 `request_sse(...)` 产出的事件字典。
- 它会跳过空数据和默认 `[DONE]` 结束标记。

## 7. 文件：读取、写入、JSON

推荐导入：

```python
from brainbridge.lib.runtime.files_manager import (
    read_file,
    read_json,
    return_full_tree,
    return_path_of_dir_under_root_dir,
    valid_path,
    write_content_tofile,
    write_json,
)
```

示例：

```python
config_root = return_path_of_dir_under_root_dir("config")
print(config_root)

write_json("sample.json", {"hello": "world"}, indent=2)
data = read_json("sample.json")
print(data["hello"])
```

说明：

- `write_json(...)` 是对 `json.dumps(...)` 和 `write_content_tofile(...)` 的薄封装。
- `read_file(..., file_code="auto")` 和 `write_content_tofile(..., file_code="auto")` 使用仓库内置编码检测器。

## 8. 终端键盘 API

推荐导入：

```python
from brainbridge.lib.runtime.terminal_core import (
    Key,
    KeyCode,
    Listener,
    decode_escape_sequence,
    decode_single_char,
)
```

示例：

```python
assert decode_escape_sequence("\x1b[A") == Key.up
assert decode_escape_sequence("\x1b[3~") == Key.delete
assert decode_single_char("\x01") == Key.ctrl_a
assert decode_single_char("w") == KeyCode.from_char("w")
```

当前公开 helper：

- `decode_escape_sequence(...)`
- `decode_single_char(...)`
- `Listener`
- `Key`
- `KeyCode`

常见映射包括：

- 方向键：`up`、`down`、`left`、`right`
- 编辑/导航：`delete`、`home`、`end`、`page_up`、`page_down`、`insert`
- 控制键：`ctrl_a`、`ctrl_c`、`ctrl_d`、`ctrl_e`、`ctrl_k`、`ctrl_u`

不要直接使用 `_RawKeyReader`。

## 9. DecisionPanelPage

推荐导入：

```python
from brainbridge.utils import DecisionPanelPage
```

最小示例：

```python
page = DecisionPanelPage(operation_tips="Use arrow keys or WASD.")
page.set_options([
    {"prompt": "Open", "output": "open"},
    {"prompt": "Exit", "output": "exit"},
])
result = page.run_once()
print(result)
```

默认行为：

- 需要交互式 TTY
- 方向键和 `WASD` 用于移动当前选项
- `Enter` 确认
- `Tab` 也会确认
- `Esc` 返回 `None`

当前扩展点：

- `enable_input_box=True`
- `input_clear_keys={...}`
- `input_return_mode="selection"` 或 `"dict"`
- `highlight_current=True`

说明：

- 关闭扩展参数时，默认行为保持原样。
- 当 `enable_input_box=True` 且 `input_return_mode="dict"` 时，`run_once()` 返回 `{"selection": ..., "input": ...}`。
- 可选输入框支持可打印字符，以及 `backspace`、`delete`、`home`、`end`、`ctrl_a`、`ctrl_e`、`ctrl_k`、`ctrl_u` 等编辑键。
- 方向键仍然用于选项移动，而不是输入框光标移动。

## 10. Loading bar

推荐导入：

```python
from brainbridge.utils import Time, display_loading_bar
```

示例：

```python
timer = Time()
display_loading_bar(
    timer,
    "=",
    ">",
    ".",
    duration=2,
    speed="high",
    method="replace",
)
```

## 11. 日志

推荐导入：

```python
from brainbridge.lib.static.logger import Logger, LogLevels, log_to_file
```

示例：

```python
logger = Logger(level=LogLevels.INFO, text="ready", context="boot")
print(logger.text_log_builder())

log_to_file(
    "request complete",
    level=LogLevels.INFO,
    context="api",
    file_path="logs/app.jsonl",
)
```

说明：

- `log_to_file(...)` 是对 `Logger.output_log(...)` 的便捷封装。
- 它会先准备目标文件路径，再进行追加式日志写入。

## 12. `user_conf` 写入后端

推荐导入：

```python
from brainbridge.lib.runtime.provider_converter import (
    read_user_provider_config,
    update_user_provider_config,
    write_user_provider_config,
)
```

示例：

```python
cfg = read_user_provider_config("base_arg_match.json")

update_user_provider_config(
    "escape_table.json",
    {"demo_provider": {"input": {"model": "str"}}},
)
```

规则：

- 只允许写 `config/user_conf/base_arg_match.json` 与 `config/user_conf/escape_table.json`
- 拒绝绝对路径
- 拒绝路径穿越
- 写入前后都会校验 JSON 合法性
- 这些 helper 不会修改 `sys_conf`

配置合并语义保持不变：

- `sys_conf` 提供默认值
- `user_conf` 负责覆盖默认值

## 13. `.bb` 归档工具

推荐导入：

```python
from brainbridge.utils import (
    aggregate_to_backup,
    has_file_tree_header,
    inject_file_tree_header,
    read_file_tree_header,
    unpack_from_backup,
)
```

示例：

```python
from brainbridge.lib.runtime.files_manager import return_full_tree

tree = return_full_tree("/path/to/project")

aggregate_to_backup(
    tree,
    "/path/to/archive.bb",
    include_file_tree_header=True,
)

header = read_file_tree_header("/path/to/archive.bb", validate=True)
print(header["format"])
```

格式说明：

- 当前魔术头：`BBPACK/3`
- 元数据以 JSON 文本记录存储
- 文件内容以 Base64 文本记录存储
- 文件树头是可选的
- 解包会拒绝绝对路径和 `..` 路径穿越

## 14. Storage 与运行时行为

- `storage/` 已不再是必须的运行时依赖。
- 运行时代码应使用显式输出路径或调用方提供的目标位置。

## 15. 测试

推荐流程：

```bash
python3 -m pip install -e .
python3 -m py_compile $(find brainbridge .test -name '*.py')
python3 -m pytest
```

常用烟雾测试：

```bash
python3 .test/test_1.py
python3 .test/test_2.py
python3 .test/test_5.py
python3 .test/test_7.py
```
