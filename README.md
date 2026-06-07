# BrainBridge

BrainBridge is a local Python toolkit built around a normal editable-install workflow.

It currently focuses on:

- provider argument conversion
- `urllib`-based HTTP and SSE requests
- threaded request dispatch
- file helpers and `.bb` packaging
- structured logging and integrity checks
- terminal interaction helpers backed by raw terminal input

English | [中文版本](./README.zh-CN.md) | [Instruction Manual](./instruction.md) | [中文使用说明](./instruction.zh-CN.md)

## Install

Use Python 3.12+ and install the repository in editable mode:

```bash
python3 -m pip install -e .
```

BrainBridge no longer depends on `sys.path` bootstrap helpers for normal use.
Runtime code now imports packages directly from `src.*`.

## Layout

- `src/public/run_lib`: runtime helpers
- `src/public/static_lib`: logging, checking, information helpers
- `src/public/run_lib/terminial_core`: built-in terminal raw-input backend
- `config/sys_conf`: default config layer
- `config/user_conf`: override config layer
- `storage/`: runtime output only
- `src/.test/sandbox/base`: original sandbox baseline
- `src/.test/sandbox/YYYY-MM-DD`: dated sandbox archives

## Import examples

```python
from src.public.run_lib.provider_converter.converter import Converter
from src.public.run_lib.requests_core.request_core import Request
from src.public.static_lib.logger.log_core import Logger, LogLevels

payload = Converter(
    "openai_completion",
    model="openai/gpt-oss-20b",
    messages=[{"role": "user", "content": "hello"}],
).information

requester = Request(timeout=30)
logger = Logger(level=LogLevels.INFO, text="ready")
```

## Core modules

| Module | Purpose |
| --- | --- |
| `src/public/run_lib/files_manager/manager.py` | file IO, tree traversal, JSON reading, root path lookup |
| `src/public/run_lib/mini_tools/chardet.py` | built-in `detect()` replacement for the old `chardet` usage |
| `src/public/run_lib/mini_tools/files_convg.py` | `.bb` pack/unpack helpers with optional file-tree headers |
| `src/public/run_lib/mini_tools/decision_panel.py` | terminal decision panel |
| `src/public/run_lib/terminial_core/keyboard.py` | raw terminal keyboard listener with a small `pynput`-like surface |
| `src/public/run_lib/provider_converter/converter.py` | provider payload conversion and response parsing helpers |
| `src/public/run_lib/requests_core/request_core.py` | `urllib`-backed request layer |
| `src/public/run_lib/requests_core/thread_requests/thread_requests.py` | threaded request pool |
| `src/public/static_lib/logger/log_core.py` | structured logging |
| `src/public/static_lib/checker/checker.py` | version, dependency, hash, and backup checks |

## Notes

- Runtime dependencies are now standard-library only.
- The old bootstrap helpers have been removed from the active source tree.
- `DecisionPanelPage` no longer requires `pynput`; it uses the built-in raw terminal backend.
- `Converter(...)` only includes `stream` when you pass it explicitly.
- `DecisionPanelPage` treats both `Enter` and `Tab` as confirm keys.
- `write_content_tofile(..., file_code="auto")` and related readers now rely on the in-repo detector.
- `.bb` archives can optionally embed a compact file-tree header for quick inspection and validation.

## Recommended checks

Run these after `python3 -m pip install -e .`:

```bash
python3 src/.test/test_2.py
python3 src/.test/test_1.py
python3 src/.test/test_7.py
python3 -m src.public.static_lib.logger.log_core
```

If you touch terminal interaction code, also run:

```bash
python3 src/.test/test_5.py
```

## License

MIT.
