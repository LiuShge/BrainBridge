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
Runtime code imports packages directly from `brainbridge.*`.

## Layout

- `brainbridge/run_lib`: public runtime helpers
- `brainbridge/static_lib`: public logging, checking, and information helpers
- `brainbridge/run_lib/terminal_core`: built-in terminal raw-input backend
- `config/sys_conf`: default config layer
- `config/user_conf`: override config layer
- `storage/`: runtime output only
- `.test/sandbox/base`: original sandbox baseline
- `.test/sandbox/YYYY-MM-DD`: dated sandbox archives

## Import examples

```python
from brainbridge.run_lib.provider_converter.converter import Converter
from brainbridge.run_lib.requests_core.request_core import Request
from brainbridge.static_lib.logger.log_core import Logger, LogLevels

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
| `brainbridge/run_lib/files_manager/manager.py` | file IO, tree traversal, JSON reading, root path lookup |
| `brainbridge/run_lib/mini_tools/chardet.py` | built-in `detect()` replacement for the old `chardet` usage |
| `brainbridge/run_lib/mini_tools/files_convg.py` | `.bb` pack/unpack helpers with optional file-tree headers |
| `brainbridge/run_lib/mini_tools/decision_panel.py` | terminal decision panel |
| `brainbridge/run_lib/terminal_core/keyboard.py` | raw terminal keyboard listener with a small `pynput`-like surface |
| `brainbridge/run_lib/provider_converter/converter.py` | provider payload conversion and response parsing helpers |
| `brainbridge/run_lib/requests_core/request_core.py` | `urllib`-backed request layer |
| `brainbridge/run_lib/requests_core/thread_requests/thread_requests.py` | threaded request pool |
| `brainbridge/static_lib/logger/log_core.py` | structured logging |
| `brainbridge/static_lib/checker/checker.py` | version, dependency, hash, and backup checks |

## Dependency policy

- Runtime dependencies are now standard-library only.
- The old bootstrap helpers have been removed from the active source tree.
- HTTP is handled by `urllib`.
- Encoding detection is handled by `brainbridge.run_lib.mini_tools.chardet.detect`.
- Terminal key listening is handled by `brainbridge.run_lib.terminal_core.keyboard`.

## Notes

- `DecisionPanelPage` no longer requires `pynput`; it uses the built-in raw terminal backend.
- `Converter(...)` only includes `stream` when you pass it explicitly.
- `DecisionPanelPage` treats both `Enter` and `Tab` as confirm keys.
- `write_content_tofile(..., file_code="auto")` and related readers now rely on the in-repo detector.
- `.bb` archives can optionally embed a compact file-tree header for quick inspection and validation.
- `terminial_core`, `ResponseUnwarp`, and `unwarp()` remain as compatibility aliases.

## More examples

```python
from brainbridge.run_lib.requests_core.thread_requests.thread_requests import RequestPool, RequestTask
from brainbridge.run_lib.provider_converter.converter import Operator

pool = RequestPool(Request(timeout=30))
tasks = [
    RequestTask("a", "get", ("https://example.com",)),
    RequestTask("b", "get", ("https://example.org",)),
]
results = pool.execute_all(tasks)

headers = Operator.HeadersBuilder.builder("token")
parsed = Operator.ResponseUnwrap.unwrap("openai_completion", {"choices": []})
```

## `.bb` format

`.bb` archives use a UTF-8, newline-delimited container format:

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

- `TREE_*` records are optional and describe the compact file tree for quick inspection.
- `FILE_DATA` is Base64 text; restore verifies both `size` and `sha256`.
- `rel` paths must stay relative and safe; extraction rejects absolute paths and `..` traversal.

## Configuration

Provider conversion reads:

- `config/sys_conf/base_arg_match.json`
- `config/sys_conf/escape_table.json`
- `config/user_conf/base_arg_match.json`
- `config/user_conf/escape_table.json`

`user_conf` overrides `sys_conf`.

## Recommended checks

Run these after `python3 -m pip install -e .`:

```bash
python3 .test/test_2.py
python3 .test/test_1.py
python3 .test/test_7.py
python3 -m py_compile $(rg --files -g '*.py' .test brainbridge)
python3 -m brainbridge.static_lib.logger.log_core
```

If you touch terminal interaction code, also run:

```bash
python3 .test/test_5.py
```

## Practical notes

- `.test/test_5.py` is the internal decision-panel/backend smoke test.
- Prefer `Operator.ResponseUnwrap.unwrap(...)`; `ResponseUnwarp` and `unwarp()` remain compatibility aliases.
- `storage/` is runtime output, not source.

## License

MIT.
