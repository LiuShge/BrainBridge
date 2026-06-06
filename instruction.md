# BrainBridge Instruction Manual

English instruction | [中文使用说明](./instruction.zh-CN.md) | [Project README](./README.md) | [中文首页](./README.zh-CN.md)

This document is the practical usage guide for the current repository state.
It is written for people who want to run the modules directly from a local checkout.

## 1. Scope

BrainBridge is a repository-local toolkit. It does not require packaging into a wheel before use.
Most modules are imported after a path bootstrap step.

The repository currently ships two bootstrap layers:

- `src/bootstrap_source_dir.py` adds the repository `src` directory to `sys.path`.
- `src/bootstrap_paths.py` locates `run_lib` and `static_lib`, then adds one of them to `sys.path`.

Several subpackages also keep a local copy of `bootstrap_source_dir.py` so they can be executed directly from inside the package tree.

## 2. Environment

Recommended setup:

1. Activate the bundled virtual environment.
2. Install dependencies from `requirements.txt`.
3. Run the smoke tests before you start changing runtime code.

Typical commands:

```bash
source .venv/Scripts/activate
pip install -r requirements.txt
python src/bootstrap_paths.py
python src/.test/test_2.py
```

The repository currently lists:

- `chardet`
- `pynput`

`pynput` is required by the terminal interaction helpers.

## 3. Bootstrapping imports

If you are working from the repository root, use the root bootstrap modules first.

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

Rules to keep in mind:

- Call exactly one of `change_sys_path(to_runlib=True)` or `change_sys_path(to_staticlib=True)`.
- Use `restore_sys_path()` after you finish importing from the selected runtime layer.
- Use `_restore_sys_path()` after you finish using the `src` bootstrap helper.
- Do not reintroduce the legacy names `simple_import.py` or `set_source_dir.py`.

## 4. Module reference

### 4.1 `src/bootstrap_paths.py`

Functions:

- `packages_path()`
- `change_sys_path(to_runlib=False, to_staticlib=False)`
- `restore_sys_path()`

Use this module when you need to add either `src/public/run_lib` or `src/public/static_lib` to `sys.path`.

Behavior:

- `packages_path()` searches from the repository root and returns a dictionary with `run_lib` and `static_lib`.
- `change_sys_path()` requires exactly one of the two boolean flags to be `True`.
- `restore_sys_path()` restores the original `sys.path` snapshot that was cached on first use.

### 4.2 `src/bootstrap_source_dir.py`

Functions:

- `_set_source_dir()`
- `_restore_sys_path()`

Use this module when you want the repository `src` directory itself on `sys.path`.

### 4.3 `src/public/run_lib/files_manager/manager.py`

Public functions:

- `return_path_of_dir_under_root_dir(dir_name)`
- `return_dir_member(dir_path)`
- `valid_path(target_path, is_file=True)`
- `return_full_tree(*base_paths)`
- `write_content_tofile(file_path, content, file_code="utf-8", trailing_newline=True, override=False)`
- `read_file(file_path, line_by_line=False, file_code="utf-8")`
- `read_json(file_path, file_code="utf-8", parse=True)`

Practical notes:

- `return_full_tree()` returns a nested list/dict structure.
- Loop detection and access errors are represented with string markers.
- `write_content_tofile(..., file_code="auto")` falls back to UTF-8 when the detected encoding is empty.

Example:

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

Main class:

- `Request`

Supported methods:

- `get(*urls, ...)`
- `post(*urls, ...)`
- `put(*urls, ...)`
- `delete(*urls, ...)`
- `request_sse(method, url, ...)`

What it does:

- Wraps standard-library `urllib` with a single object.
- Supports one URL or a batch of URLs.
- Stores simple request logs when `enable_logging=True`.
- Parses SSE streams into event dictionaries.

Important behavior:

- For a single URL, the method returns a compatibility `Response` object with `status_code`, `content`, `text`, `json()`, and `raise_for_status()`.
- For multiple URLs, the method returns a dictionary keyed by URL string.
- `request_sse()` yields dictionaries with `id`, `event`, and `data`.
- The current SSE parser only yields events that contain data.

Example:

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

Classes:

- `RequestTask`
- `TaskResult`
- `RequestWorker`
- `RequestPool`

Use this module when you want to dispatch several request tasks in parallel and wait for all of them to finish.

Example:

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

Classes:

- `_ConfigEngine`
- `Converter`
- `Operator`

Use this module to build provider-specific request payloads from a generic argument set.

Current config files:

- `config/sys_conf/base_arg_match.json`
- `config/sys_conf/escape_table.json`
- `config/user_conf/base_arg_match.json`
- `config/user_conf/escape_table.json`

Practical behavior:

- User config overrides system defaults on key collision.
- `Converter` validates the provider name against the merged config.
- `Converter` checks that essential arguments exist before building the payload.
- Unknown type tokens in the config are treated as invalid.
- `Operator.HeadersBuilder.builder(api_token, include_accept=False)` returns a standard JSON header set.
- `Operator.ResponseUnwarp.unwarp(provider, response)` returns normalized response data.

Example:

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

Main class:

- `Time`

Useful members:

- `Time.Timer(precision)`
- `Time.Timer.passed()`
- `Time.Timer.reset()`
- `Time.f_time(time_part)`

Use this module when you need a small elapsed-time helper or simple time formatting for logs.

### 4.8 `src/public/run_lib/mini_tools/loading_bar.py`

Main function:

- `display_loading_bar(_timer, *content, duration=6, speed="mid", method="replace", background=None, size=32, chunk_size=3)`

Use this module for a terminal-only loading bar.
It expects a `Time` instance.

### 4.9 `src/public/run_lib/mini_tools/decision_panel.py`

Main class:

- `DecisionPanelPage`

Use this module for interactive terminal selection pages.

Requirements and limits:

- It depends on `pynput`.
- It is meant for a real terminal session, not for a headless environment.
- `clear_mode` accepts `system`, `ansi`, or `none`.

Typical use:

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

Public API:

- `BackupError`
- `to_posix(path)`
- `is_special_marker(node)`
- `iter_tree_files(tree)`
- `root_prefix_id(root)`
- `relative_under_root(root, file_path)`
- `b64_encode_stream(src, wrap=B64_WRAP)`
- `build_compact_file_tree(tree)`
- `has_file_tree_header(backup_file_path)`
- `read_file_tree_header(backup_file_path, validate=False)`
- `inject_file_tree_header(backup_file_path, tree, validate=True)`
- `aggregate_to_backup(tree, output_backup_path, progress_callback=None, include_file_tree_header=False, validate_file_tree_header=True)`
- `unpack_from_backup(backup_file_path, target_extraction_dir, skip_errors=False, progress_callback=None)`

Use this module when you want to pack a directory tree into a text backup file or restore it later.
It is a streaming `.bb` text format, not a ZIP replacement.

Behavior:

- The current `.bb` format uses JSON metadata lines instead of space-split headers, so paths with spaces are handled safely.
- `aggregate_to_backup(..., include_file_tree_header=True)` embeds a compact tree header at the top of the backup for quick inspection.
- `has_file_tree_header()` only checks for the presence of that header.
- `read_file_tree_header(..., validate=True)` verifies that the embedded tree header matches the file records stored in the backup.
- `inject_file_tree_header()` can add or replace the top-level tree header in an existing `.bb` file.

Example:

```python
from src.bootstrap_source_dir import _set_source_dir
from src.bootstrap_paths import change_sys_path, restore_sys_path

_set_source_dir()
change_sys_path(to_runlib=True)

from files_manager.manager import return_full_tree
from mini_tools.files_convg import aggregate_to_backup, unpack_from_backup

tree = return_full_tree("src/public")
aggregate_to_backup(tree, "storage/backup.bb", include_file_tree_header=True)
unpack_from_backup("storage/backup.bb", "storage/restored")

restore_sys_path()
```

### 4.11 `src/public/static_lib/checker/checker.py`

Main class:

- `CheckTools`

Useful methods:

- `decision_making(content, is_fatal=False)`
- `check_py_version()`
- `dependency_check(requirements)`
- `check_code_hash(file_path, expected_hash)`
- `check_file_hash(file_path, expected_hash)`
- `fix_code_file(fix_file_path, backup_path=None)`
- `fix_conf_file(backup_path, target_conf)`
- `fix_backup_file(current_file, backup_path)`

Use this module for basic environment checks, file integrity checks, and backup-based recovery.

Important note:

- `check_py_version()` currently checks against Python `3.12.0`.
- The repository itself is developed and smoke-tested on Python `3.12+`, so treat the version check as an internal guard rather than a packaging rule.

### 4.12 `src/public/static_lib/logger/log_core.py`

Public classes:

- `LogLevels`
- `LogPart`
- `LogFormat`
- `LogInformation`
- `Logger`

Use this module when you want structured log output.

Behavior:

- `Logger.json_log_builder()` returns a JSON string.
- `Logger.text_log_builder()` returns a dictionary.
- `Logger.output_log(to_file, display, file_path=None, write_json=True)` can write to `.jsonl` or print to the terminal.

### 4.13 `src/public/static_lib/information/information.py`

Public function:

- `display()`

This helper prints the JSON files located under `src/public/static_lib/information/config`.
It is a diagnostic helper, not a configuration editor.

## 5. Typical workflows

### 5.1 Build a provider payload and send a request

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

### 5.2 Parse an SSE stream

This example continues from 5.1 and reuses `req`, `payload`, and `headers`.

```python
for event in req.request_sse(
    method="POST",
    url="https://example.com/stream",
    json=payload,
    headers=headers,
):
    print(event["data"], end="")
```

### 5.3 Log output to a JSONL file

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

### 5.4 Check files and dependencies

```python
from src.bootstrap_source_dir import _set_source_dir, _restore_sys_path
from src.bootstrap_paths import change_sys_path, restore_sys_path

_set_source_dir()
change_sys_path(to_staticlib=True)

from checker.checker import CheckTools

CheckTools.dependency_check(["chardet"])
CheckTools.check_file_hash("config/sys_conf/base_arg_match.json", "expected_sha256_here")

restore_sys_path()
_restore_sys_path()
```

## 6. Troubleshooting

### ImportError for `provider_converter` or `requests_core`

Make sure you called the bootstrap helpers in this order:

1. `_set_source_dir()`
2. `change_sys_path(to_runlib=True)` or `change_sys_path(to_staticlib=True)`
3. your imports
4. `restore_sys_path()`
5. `_restore_sys_path()`

### ImportError for `logger`, `checker`, or `information`

Use the same bootstrap order, but call `change_sys_path(to_staticlib=True)` before importing those modules.

### `pynput` is missing

Install the dependency from `requirements.txt`.
The terminal UI and `src/.test/test_5.py` need it.

### `check_py_version()` warns on your interpreter

That method currently targets Python `3.12.0`.
The repository badge and day-to-day smoke tests still use `3.12+`.

### `write_content_tofile(..., file_code="auto")` on a new empty file

It now falls back to UTF-8.

### Generated files in `src/` or `storage/`

Clean them up if they are only smoke-test output.
Do not commit runtime artifacts unless they are intentionally part of the repository.

## 7. Extending the project

If you add a new runtime module:

- keep the file inside `src/public/run_lib` or `src/public/static_lib`
- use snake_case file names
- keep imports local and explicit
- update the README and this instruction manual if the public surface changes
- add a smoke test under `src/.test`

If you add a new provider profile:

- update `config/sys_conf/base_arg_match.json`
- update `config/sys_conf/escape_table.json`
- mirror the override in `config/user_conf` only if you need user customization

## 8. Reference commands

Useful commands during development:

```bash
python src/bootstrap_paths.py
python src/.test/test_2.py
python src/.test/test_1.py
python src/public/static_lib/logger/log_core.py
python -m py_compile src/bootstrap_paths.py src/bootstrap_source_dir.py
```

These checks cover the bootstrap path, the import chain, file-tree helpers, and the logger module.
