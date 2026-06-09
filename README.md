# BrainBridge

BrainBridge is a local Python toolkit for provider payload conversion, `urllib`-based requests, terminal interaction, structured logging, and `.bb` archive helpers.

[中文版本](./README.zh-CN.md) | [Instruction Manual](./instruction.md) | [中文使用说明](./instruction.zh-CN.md)

## Install

Use Python 3.12+ and install the repository in editable mode:

```bash
python3 -m pip install -e .
```

BrainBridge is designed to work through normal package imports. New code should import from `brainbridge...` directly.

## Current layout

- `brainbridge/lib/runtime`
  Runtime modules such as provider conversion, requests, file helpers, and terminal input.
- `brainbridge/lib/static`
  Structured logging, integrity checks, and bundled information helpers.
- `brainbridge/utils`
  Small application-facing utilities migrated from the old `mini_tools` area.
- `config/sys_conf`
  Default provider configuration.
- `config/user_conf`
  User override layer for provider configuration.
- `.test`
  Smoke tests, pytest entrypoints, and sandbox fixtures.

## Recommended top-level API

```python
from brainbridge import Converter, Operator, Request, Logger, LogLevels
```

This top-level surface is intentionally small. It is meant for common application code, not for every internal helper.

## Recommended subpackage APIs

### Provider conversion

```python
from brainbridge.lib.runtime.provider_converter import (
    Converter,
    build_headers,
    list_providers,
    provider_exists,
    unwrap_response,
)
```

### Requests

```python
from brainbridge.lib.runtime.requests_core import Request, Response, RequestException, iter_sse_json
```

### Files

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

### Terminal input

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

### Utilities

```python
from brainbridge.utils import (
    DecisionPanelPage,
    Time,
    detect,
    display_loading_bar,
    aggregate_to_backup,
    has_file_tree_header,
    inject_file_tree_header,
    read_file_tree_header,
    unpack_from_backup,
)
```

### Logger

```python
from brainbridge.lib.static.logger import Logger, LogLevels, log_to_file
```

## Package cleanup status

The old compatibility packages have been removed.

- use `brainbridge.lib.runtime` instead of the historical `run_lib` layout
- use `brainbridge.lib.static` instead of the historical `static_lib` layout
- use `brainbridge.utils` for the utility surface that previously lived under `mini_tools`

## Runtime dependency policy

BrainBridge keeps runtime dependencies standard-library only.

- HTTP uses `urllib`
- terminal input uses the built-in `brainbridge.lib.runtime.terminal_core`
- encoding detection uses the in-repo `brainbridge.utils.chardet.detect`

The runtime should not require `requests`, external `chardet`, or `pynput`.

## Provider configuration

Provider conversion reads and merges:

- `config/sys_conf/base_arg_match.json`
- `config/sys_conf/escape_table.json`
- `config/user_conf/base_arg_match.json`
- `config/user_conf/escape_table.json`

`user_conf` overrides `sys_conf`.

BrainBridge also provides a write backend for `user_conf` only:

```python
from brainbridge.lib.runtime.provider_converter import (
    read_user_provider_config,
    update_user_provider_config,
    write_user_provider_config,
)
```

These helpers do not write `sys_conf`.

## `.bb` archive format

BrainBridge ships `.bb` backup helpers in `brainbridge.utils.files_convg`.

Current format:

- magic header: `BBPACK/3`
- UTF-8 line-oriented container
- JSON metadata records
- Base64 payload records
- optional compact file-tree header for quick inspection and validation

Main helper entrypoints:

- `aggregate_to_backup(...)`
- `unpack_from_backup(...)`
- `has_file_tree_header(...)`
- `read_file_tree_header(...)`
- `inject_file_tree_header(...)`

## Validation

Recommended validation flow:

```bash
python3 -m pip install -e .
python3 -m py_compile $(find brainbridge .test -name '*.py')
python3 -m pytest
```

Useful smoke tests:

```bash
python3 .test/test_2.py
python3 .test/test_1.py
python3 .test/test_5.py
python3 .test/test_7.py
```

## Notes

- `storage/` is no longer a required runtime dependency.
- `DecisionPanelPage` uses the built-in terminal backend, not `pynput`.
- `Converter(...)` only includes `stream` when you pass it explicitly.
- `Tab` and `Enter` both act as confirm keys in `DecisionPanelPage`.

## License

MIT.
