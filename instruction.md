# BrainBridge Instruction Manual

This document describes the current public surface of BrainBridge after the package layout refactor.

## 1. Installation and import style

Install in editable mode:

```bash
python3 -m pip install -e .
```

Recommended import style:

```python
from brainbridge import Converter, Operator, Request, Logger, LogLevels
from brainbridge.lib.runtime.files_manager import read_json, write_json
from brainbridge.lib.runtime.provider_converter import build_headers, unwrap_response
from brainbridge.utils import DecisionPanelPage, Time, detect, display_loading_bar
```

Do not add new `sys.path` bootstrap helpers for normal package use.

## 2. Package layout

- `brainbridge/lib/runtime`
  Runtime request, conversion, file, and terminal modules.
- `brainbridge/lib/static`
  Logging, checking, and bundled information helpers.
- `brainbridge/utils`
  User-facing helper modules migrated from the old `mini_tools`.
- `config/sys_conf`
  Default provider configuration.
- `config/user_conf`
  Override layer for provider configuration.
- `.test`
  Smoke tests, pytest entrypoints, and sandbox fixtures.

The old compatibility packages have been removed. Use only:

- `brainbridge.lib.runtime`
- `brainbridge.lib.static`
- `brainbridge.utils`

## 3. Public and private API guidance

Public APIs are the objects exported from:

- `brainbridge`
- `brainbridge.lib.runtime.provider_converter`
- `brainbridge.lib.runtime.requests_core`
- `brainbridge.lib.runtime.files_manager`
- `brainbridge.lib.runtime.terminal_core`
- `brainbridge.lib.static.logger`
- `brainbridge.utils`

Do not build new code around private internals such as:

- `_ConfigEngine`
- `_RawKeyReader`
- any name beginning with `_`

## 4. Top-level API

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

Recommended usage:

- `Converter` for provider payload conversion
- `Operator` for header building and response unwrapping
- `Request` for HTTP and SSE requests
- `Logger` and `LogLevels` for structured logs

## 5. Provider payload conversion

Recommended imports:

```python
from brainbridge.lib.runtime.provider_converter import (
    Converter,
    build_headers,
    list_providers,
    provider_exists,
    unwrap_response,
)
```

Example:

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

Notes:

- `Converter(...)` validates provider payloads against merged config schemas.
- `stream` is only included when you pass it explicitly.
- `build_headers(...)` calls `Operator.HeadersBuilder.builder(...)`.
- `unwrap_response(...)` calls `Operator.ResponseUnwrap.unwrap(...)`.

### Direct `ResponseUnwrap` usage

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

## 6. Requests: GET, POST, and SSE

Recommended imports:

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

### POST with JSON

```python
response = requester.post(
    "https://example.com/api",
    json={"hello": "world"},
)
print(response.ok)
print(response.json())
```

### SSE request

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

Notes:

- `iter_sse_json(...)` consumes the event dictionaries produced by `request_sse(...)`.
- It skips empty payloads and the default `[DONE]` token.

## 7. Files: read, write, and JSON

Recommended imports:

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

Example:

```python
config_root = return_path_of_dir_under_root_dir("config")
print(config_root)

write_json("sample.json", {"hello": "world"}, indent=2)
data = read_json("sample.json")
print(data["hello"])
```

Notes:

- `write_json(...)` is a thin helper around `json.dumps(...)` and `write_content_tofile(...)`.
- `read_file(..., file_code="auto")` and `write_content_tofile(..., file_code="auto")` use the in-repo detector.

## 8. Terminal keyboard API

Recommended imports:

```python
from brainbridge.lib.runtime.terminal_core import (
    Key,
    KeyCode,
    Listener,
    decode_escape_sequence,
    decode_single_char,
)
```

Examples:

```python
assert decode_escape_sequence("\x1b[A") == Key.up
assert decode_escape_sequence("\x1b[3~") == Key.delete
assert decode_single_char("\x01") == Key.ctrl_a
assert decode_single_char("w") == KeyCode.from_char("w")
```

Supported public helpers:

- `decode_escape_sequence(...)`
- `decode_single_char(...)`
- `Listener`
- `Key`
- `KeyCode`

Common mapped keys include:

- arrows: `up`, `down`, `left`, `right`
- editing/navigation: `delete`, `home`, `end`, `page_up`, `page_down`, `insert`
- control keys: `ctrl_a`, `ctrl_c`, `ctrl_d`, `ctrl_e`, `ctrl_k`, `ctrl_u`

Do not use `_RawKeyReader` directly.

## 9. DecisionPanelPage

Recommended import:

```python
from brainbridge.utils import DecisionPanelPage
```

Minimal example:

```python
page = DecisionPanelPage(operation_tips="Use arrow keys or WASD.")
page.set_options([
    {"prompt": "Open", "output": "open"},
    {"prompt": "Exit", "output": "exit"},
])
result = page.run_once()
print(result)
```

Default behavior:

- requires an interactive TTY
- arrow keys and `WASD` move the current selection
- `Enter` confirms
- `Tab` also confirms
- `Esc` returns `None`

Current extension points:

- `enable_input_box=True`
- `input_clear_keys={...}`
- `input_return_mode="selection"` or `"dict"`
- `highlight_current=True`

Notes:

- Default behavior remains the same when extensions are not enabled.
- When `enable_input_box=True` and `input_return_mode="dict"`, `run_once()` returns `{"selection": ..., "input": ...}`.
- The optional input box accepts printable characters plus editing helpers such as `backspace`, `delete`, `home`, `end`, `ctrl_a`, `ctrl_e`, `ctrl_k`, and `ctrl_u`.
- Arrow keys continue to control option selection, not input-box cursor movement.

## 10. Loading bar

Recommended import:

```python
from brainbridge.utils import Time, display_loading_bar
```

Example:

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

## 11. Logger

Recommended import:

```python
from brainbridge.lib.static.logger import Logger, LogLevels, log_to_file
```

Examples:

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

Notes:

- `log_to_file(...)` is a convenience wrapper around `Logger.output_log(...)`.
- It prepares the target file path for append-style logging.

## 12. `user_conf` write backend

Recommended import:

```python
from brainbridge.lib.runtime.provider_converter import (
    read_user_provider_config,
    update_user_provider_config,
    write_user_provider_config,
)
```

Example:

```python
cfg = read_user_provider_config("base_arg_match.json")

update_user_provider_config(
    "escape_table.json",
    {"demo_provider": {"input": {"model": "str"}}},
)
```

Rules:

- only `config/user_conf/base_arg_match.json` and `config/user_conf/escape_table.json` are writable
- absolute paths are rejected
- path traversal is rejected
- writes are validated as JSON
- `sys_conf` is not modified by these helpers

Configuration merge semantics stay the same:

- `sys_conf` provides defaults
- `user_conf` overrides defaults

## 13. `.bb` archive helpers

Recommended import:

```python
from brainbridge.utils import (
    aggregate_to_backup,
    has_file_tree_header,
    inject_file_tree_header,
    read_file_tree_header,
    unpack_from_backup,
)
```

Example:

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

Format notes:

- current magic header: `BBPACK/3`
- metadata is stored as JSON text records
- file payloads are Base64 text records
- file-tree headers are optional
- extraction rejects absolute paths and `..` traversal

## 14. Storage and runtime behavior

- `storage/` is no longer a required runtime dependency.
- Runtime code should use explicit output paths or caller-supplied destinations.

## 15. Testing

Recommended flow:

```bash
python3 -m pip install -e .
python3 -m py_compile $(find brainbridge .test -name '*.py')
python3 -m pytest
```

Useful smoke tests:

```bash
python3 .test/test_1.py
python3 .test/test_2.py
python3 .test/test_5.py
python3 .test/test_7.py
```
