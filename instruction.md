# BrainBridge Instruction Manual

## 1. Overview

BrainBridge is used as a normal editable-installed package:

```bash
python3 -m pip install -e .
```

The active import style is package-based:

```python
from brainbridge.run_lib.requests_core.request_core import Request
from brainbridge.run_lib.provider_converter.converter import Converter
from brainbridge.static_lib.logger.log_core import Logger
```

The old bootstrap helpers have been removed from the active source tree.

## 2. Runtime layout

- `brainbridge/run_lib/files_manager`: file and path helpers
- `brainbridge/run_lib/mini_tools`: small runtime helpers
- `brainbridge/run_lib/terminal_core`: built-in terminal raw-input backend
- `brainbridge/run_lib/provider_converter`: provider config and payload conversion
- `brainbridge/run_lib/requests_core`: request engine and threaded request helpers
- `brainbridge/static_lib/logger`: structured logging
- `brainbridge/static_lib/checker`: runtime checks and backup recovery helpers
- `brainbridge/static_lib/information`: prints bundled JSON metadata
- `.test`: smoke tests and sandbox fixtures

## 3. Dependency policy

Core runtime dependencies are standard-library only.

Removed third-party runtime dependencies:

- `requests`
- `chardet`
- `pynput`

Replacements:

- HTTP is handled by `urllib`
- encoding detection is handled by `brainbridge.run_lib.mini_tools.chardet.detect`
- terminal key listening is handled by `brainbridge.run_lib.terminal_core.keyboard`

## 4. Common import examples

### 4.1 Files

```python
from brainbridge.run_lib.files_manager.manager import (
    read_file,
    read_json,
    return_full_tree,
    valid_path,
    write_content_tofile,
)
```

### 4.2 Requests

```python
from brainbridge.run_lib.requests_core.request_core import Request

requester = Request(timeout=30)
response = requester.get("https://example.com")
print(response.status_code)
print(response.text)
```

### 4.3 Threaded requests

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

### 4.4 Provider conversion

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

Notes:

- `stream` is only included when you pass it explicitly.
- Prefer `Operator.ResponseUnwrap.unwrap(...)`; `ResponseUnwarp` and `unwarp()` remain compatibility aliases.

### 4.5 Logging

```python
from brainbridge.static_lib.logger.log_core import Logger, LogLevels

logger = Logger(level=LogLevels.INFO, text="hello")
print(logger.text_log_builder())
```

### 4.6 Terminal interaction

```python
from brainbridge.run_lib.mini_tools.decision_panel import DecisionPanelPage

page = DecisionPanelPage(operation_tips="Use arrow keys or WASD.")
page.set_options([
    {"prompt": "Open", "output": "open"},
    {"prompt": "Exit", "output": "exit"},
])
result = page.run_once()
```

`DecisionPanelPage` uses the raw terminal backend in `brainbridge.run_lib.terminal_core`.
Confirm uses `Enter` by default, and `Tab` is accepted as the same confirm action.
The backend intentionally keeps a small `pynput`-like API surface for already-used behavior:

- `keyboard.Key`
- `keyboard.KeyCode.from_char()`
- `keyboard.Listener`

## 5. `.bb` archive helpers

Main module:

```python
from brainbridge.run_lib.mini_tools.files_convg import (
    aggregate_to_backup,
    has_file_tree_header,
    inject_file_tree_header,
    read_file_tree_header,
    unpack_from_backup,
)
```

Notes:

- `.bb` now uses the `BBPACK/3` format
- file-tree headers are optional
- headers can be injected later and validated
- sandbox snapshots follow `base/` plus `YYYY-MM-DD/`

### 5.1 Record-level format specification

`.bb` files are UTF-8 text with one logical record per line:

```text
BBPACK/3
META {"kind":"backup","version":3,"b64_wrap":76,"chunk_size":1048576}
META {"kind":"root","root_id":"<sha16>","root_posix":"<root path>"}
META {"kind":"tree_header","format":"compact-tree-v1","line_count":N,"sha256":"<digest>"}   # optional
TREE_BEGIN
TREE_DATA <base64-encoded JSON tree header>                                                    # optional
TREE_END                                                                                        # optional
FILE_BEGIN
FILE_META {"root_id":"<sha16>","rel":"path/in/root","src_full_posix":"<source path>","encoding":"b64"}
FILE_DATA <base64 payload chunk>
FILE_CHECK {"size":123,"sha256":"<digest>"}
FILE_END
...
BBPACK_END
```

- The leading `META {"kind":"backup",...}` line declares format version and Base64 chunking metadata.
- Each `META {"kind":"root",...}` line maps a stable `root_id` to the original root path.
- The optional tree-header block stores Base64-encoded JSON for the `compact-tree-v1` summary and is guarded by `line_count` plus `sha256`.
- Each file record begins with `FILE_BEGIN`, carries one `FILE_META`, one or more `FILE_DATA` lines, then a `FILE_CHECK` and `FILE_END`.

### 5.2 Validation and extraction rules

- `FILE_DATA` always stores Base64 text, even for plain-text files.
- Restore validates both `FILE_CHECK.size` and `FILE_CHECK.sha256`.
- `rel` must stay relative to its declared root; absolute paths and `..` traversal are rejected.
- If a tree header is present and validation is requested, its flattened file list must match the actual file records.

## 6. Configuration

Provider conversion reads:

- `config/sys_conf/base_arg_match.json`
- `config/sys_conf/escape_table.json`
- `config/user_conf/base_arg_match.json`
- `config/user_conf/escape_table.json`

`user_conf` overrides `sys_conf`.

## 7. Validation

Recommended validation flow:

```bash
python3 -m pip install -e .
python3 -m py_compile $(rg --files -g '*.py' .test brainbridge)
python3 .test/test_2.py
python3 .test/test_1.py
python3 .test/test_7.py
python3 .test/test_5.py
python3 -m brainbridge.static_lib.logger.log_core
```

## 8. Practical notes

- `.test/test_5.py` is the internal decision-panel/backend smoke test, not a `pynput` check.
- `write_content_tofile(..., file_code="auto")` and `read_file(..., file_code="auto")` rely on the in-repo detector.
- `storage/` is runtime output, not source.
- Keep repository guidance factual and concise.
