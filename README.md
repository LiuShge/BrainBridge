# BrainBridge

BrainBridge is a small Python toolkit for direct, local use inside this repository.
It focuses on a few concrete jobs:

- bootstrapping import paths from the repository root or from a package-local module
- converting generic request arguments into provider-specific payloads
- sending HTTP requests and parsing SSE streams with standard-library `urllib`
- running a simple threaded request pool
- showing a terminal decision panel and a loading bar
- reading, writing, checking, and packaging files

English | [中文版本](./README.zh-CN.md) | [Instruction Manual](./instruction.md) | [中文使用说明](./instruction.zh-CN.md)

## What this repo contains

The repository is split into two runtime layers:

- `src/public/run_lib` contains the runtime helpers that are used while the program is running.
- `src/public/static_lib` contains the supporting helpers for logging, integrity checks, and metadata.
- `src/bootstrap_paths.py` and `src/bootstrap_source_dir.py` are the path bootstrap helpers.
- `config/` holds runtime configuration and provider mapping files.
- `storage/` is for generated output only.

This project is not a framework or a package manager. It is a set of modules that are meant to be imported directly from the repository checkout.

## Quick start

1. Activate the bundled virtual environment.

   - PowerShell: `.\.venv\Scripts\Activate.ps1`
   - Unix shell: `source .venv/Scripts/activate`

2. Install the dependencies.

   ```bash
   pip install -r requirements.txt
   ```

3. Smoke test the bootstrap logic.

   ```bash
   python src/bootstrap_paths.py
   python src/.test/test_2.py
   ```

4. If you need the interactive terminal UI, make sure `pynput` is available in the environment.

## Import pattern

When you run code from the repository root, use the root bootstrap helpers first.

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

If you execute a file directly from inside `src/public/...`, use that subpackage's local `bootstrap_source_dir.py` mirror.

## Core modules

| Module | What it does |
| --- | --- |
| `src/bootstrap_paths.py` | Finds `run_lib` and `static_lib`, then adds one of them to `sys.path`. |
| `src/bootstrap_source_dir.py` | Adds the repository `src` directory to `sys.path` and restores it later. |
| `src/public/run_lib/files_manager/manager.py` | File and directory helpers: `valid_path`, `read_file`, `read_json`, `write_content_tofile`, `return_full_tree`. |
| `src/public/run_lib/requests_core/request_core.py` | `Request` wrapper around standard-library `urllib` with `get`, `post`, `put`, `delete`, and SSE support. |
| `src/public/run_lib/requests_core/thread_requests/thread_requests.py` | Threaded request pool: `RequestTask`, `TaskResult`, `RequestWorker`, `RequestPool`. |
| `src/public/run_lib/provider_converter/converter.py` | `Converter` for provider payload mapping and `Operator` helpers for headers and response parsing. |
| `src/public/run_lib/mini_tools/timer.py` | `Time` and `Time.Timer` for elapsed time and time formatting. |
| `src/public/run_lib/mini_tools/loading_bar.py` | Console loading bar helper. |
| `src/public/run_lib/mini_tools/decision_panel.py` | Interactive terminal menu built with `pynput`. |
| `src/public/run_lib/mini_tools/files_convg.py` | `.bb` backup packing and unpacking helpers, with optional embedded file-tree headers. |
| `src/public/static_lib/checker/checker.py` | Dependency, version, file hash, and backup recovery helpers. |
| `src/public/static_lib/logger/log_core.py` | Structured logging helpers and the `Logger` class. |
| `src/public/static_lib/information/information.py` | Prints the JSON files under `src/public/static_lib/information/config`. |

## Configuration

The provider converter reads two layers of configuration:

- `config/sys_conf/base_arg_match.json`
- `config/sys_conf/escape_table.json`
- `config/user_conf/base_arg_match.json`
- `config/user_conf/escape_table.json`

User configuration overrides the system defaults when keys overlap.

The information module also reads:

- `src/public/static_lib/information/config/project_information.json`
- `src/public/static_lib/information/config/py_env_information.json`

## Practical notes

- `Request.request_sse()` returns parsed event dictionaries with `id`, `event`, and `data`.
- The current SSE parser only yields events that contain data.
- `Converter` accepts only provider profiles that exist in the merged config.
- `DecisionPanelPage` and the related terminal UI helpers need `pynput`.
- `CheckTools.check_py_version()` targets Python `3.12.0` as the recommended baseline, while the repo itself is developed and smoke-tested on Python `3.12+`.
- `write_content_tofile(..., file_code="auto")` now falls back to UTF-8 on empty files.
- `storage/` should stay free of source files unless you intentionally want generated output there.

## Recommended checks

Run these after changing the runtime helpers or the import bootstrap files:

```bash
python src/bootstrap_paths.py
python src/.test/test_2.py
python src/public/static_lib/logger/log_core.py
```

If you touched the file tree or backup helpers, also run:

```bash
python src/.test/test_1.py
```

## License

This project is distributed under the MIT License.
