# BrainBridge Instruction Manual

## 1. Overview

BrainBridge is now used as a normal editable-installed package:

```bash
python3 -m pip install -e .
```

The active import style is package-based:

```python
from src.public.run_lib.requests_core.request_core import Request
from src.public.run_lib.provider_converter.converter import Converter
from src.public.static_lib.logger.log_core import Logger
```

The old bootstrap files remain in the repository only as legacy leftovers. New code should not depend on them.

## 2. Runtime layout

- `src/public/run_lib/files_manager`: file and path helpers
- `src/public/run_lib/mini_tools`: small runtime helpers
- `src/public/run_lib/terminial_core`: built-in terminal raw-input backend
- `src/public/run_lib/provider_converter`: provider config and payload conversion
- `src/public/run_lib/requests_core`: request engine and threaded request helpers
- `src/public/static_lib/logger`: structured logging
- `src/public/static_lib/checker`: runtime checks and backup recovery helpers
- `src/public/static_lib/information`: prints bundled JSON metadata

## 3. Dependency policy

Core runtime dependencies are standard-library only.

Removed third-party runtime dependencies:

- `requests`
- `chardet`
- `pynput`

Replacements:

- HTTP is handled by `urllib`
- encoding detection is handled by `src.public.run_lib.mini_tools.chardet.detect`
- terminal key listening is handled by `src.public.run_lib.terminial_core.keyboard`

## 4. Common import examples

### 4.1 Files

```python
from src.public.run_lib.files_manager.manager import (
    read_file,
    read_json,
    return_full_tree,
    valid_path,
    write_content_tofile,
)
```

### 4.2 Requests

```python
from src.public.run_lib.requests_core.request_core import Request

requester = Request(timeout=30)
response = requester.get("https://example.com")
print(response.status_code)
print(response.text)
```

### 4.3 Threaded requests

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

### 4.4 Provider conversion

```python
from src.public.run_lib.provider_converter.converter import Converter, Operator

payload = Converter(
    "openai_completion",
    model="openai/gpt-oss-20b",
    messages=[{"role": "user", "content": "hello"}],
).information

headers = Operator.HeadersBuilder.builder("token")
```

### 4.5 Logging

```python
from src.public.static_lib.logger.log_core import Logger, LogLevels

logger = Logger(level=LogLevels.INFO, text="hello")
print(logger.text_log_builder())
```

### 4.6 Terminal interaction

```python
from src.public.run_lib.mini_tools.decision_panel import DecisionPanelPage

page = DecisionPanelPage(operation_tips="Use arrow keys or WASD.")
page.set_options([
    {"prompt": "Open", "output": "open"},
    {"prompt": "Exit", "output": "exit"},
])
result = page.run_once()
```

`DecisionPanelPage` uses the raw terminal backend in `src.public.run_lib.terminial_core`.
The backend intentionally keeps a small `pynput`-like API surface for already-used behavior:

- `keyboard.Key`
- `keyboard.KeyCode.from_char()`
- `keyboard.Listener`

## 5. `.bb` archive helpers

Main module:

```python
from src.public.run_lib.mini_tools.files_convg import (
    aggregate_to_backup,
    has_file_tree_header,
    inject_file_tree_header,
    read_file_tree_header,
    unpack_from_backup,
)
```

Notes:

- `.bb` now uses the `BBPACK/3` format.
- file-tree headers are optional
- headers can be injected later and validated
- sandbox snapshots follow `base/` plus `YYYY-MM-DD/`

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
python3 -m py_compile $(rg --files -g '*.py' src)
python3 src/.test/test_2.py
python3 src/.test/test_1.py
python3 src/.test/test_7.py
python3 src/.test/test_5.py
python3 -m src.public.static_lib.logger.log_core
```

## 8. Practical notes

- `src/.test/test_5.py` is now an internal decision-panel/backend smoke test, not a `pynput` check.
- `write_content_tofile(..., file_code="auto")` and `read_file(..., file_code="auto")` rely on the in-repo detector.
- `storage/` is runtime output, not source.
- Keep repository guidance factual and concise.
