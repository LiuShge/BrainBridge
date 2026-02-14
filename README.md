# BrainBridge

BrainBridge is a small Python toolkit that collects reusable runtime helpers
and static utilities used by the broader project. The current codebase focuses
on three areas:

- Request helpers that wrap `requests` with simple logging, batching, and SSE
  streaming support.
- Provider argument conversion and validation driven by JSON configuration.
- File and directory helpers for walking the repository and reading/writing
  files safely.

There is no full application entry point yet. The root launch scripts and GUI
folder are placeholders, while the core logic lives under `src/public`.

## Project layout

```
BrainBridge/
  config/
    sys_conf/
      base_arg_match.json     # Generic arg mapping -> provider args
      escape_table.json       # Provider input/output schema definitions
  src/
    simple_import.py          # Dynamic sys.path helper
    public/
      run_lib/                # Runtime helpers (requests, converters, file tools)
      static_lib/             # Static helpers (package checks, info stubs)
    stubs/                    # .pyi type stubs for run_lib modules
    .test/                    # Manual sandbox copy of run_lib/static_lib
  storage/                    # Runtime output (logs, metadata, etc.)
  requirements.txt
  launcher.py / _launcher.py / _reset.py  # Empty placeholders
```

## Setup

1) (Optional) Activate the bundled virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies:

```powershell
pip install -r requirements.txt
```

## Quick smoke test

Run the import helper to confirm `run_lib` and `static_lib` resolution works:

```powershell
python src/simple_import.py
```

## Usage

### Dynamic import helper

`src/simple_import.py` provides a small helper that locates `run_lib` and
`static_lib` and appends the chosen path to `sys.path` at runtime.

```python
from simple_import import change_sys_path, restore_sys_path

change_sys_path(to_runlib=True)
from requests_core.request_core import Request
restore_sys_path()
```

Use `restore_sys_path()` after importing to avoid polluting the import path for
the rest of the program.

### Requests helper

`src/public/run_lib/requests_core/request_core.py` wraps `requests` to provide:

- Single or multi-URL GET/POST/PUT/DELETE helpers
- Optional logging of request events
- A simple SSE iterator for streaming endpoints
- A small timing utility (`Time.Timer`)

Example:

```python
from simple_import import change_sys_path, restore_sys_path

change_sys_path(to_runlib=True)
from requests_core.request_core import Request
restore_sys_path()

req = Request(enable_logging=True, timeout=10)
resp = req.get("https://www.example.com")
print(resp.status_code)
print(len(req))  # number of logged events
```

### Provider converter

`src/public/run_lib/provider_converter/converter.py` validates and translates
generic arguments into provider-specific payloads. Validation rules and allowed
types are stored in `config/sys_conf/escape_table.json`, while the generic
argument mapping lives in `config/sys_conf/base_arg_match.json`.

Example:

```python
from simple_import import change_sys_path, restore_sys_path

change_sys_path(to_runlib=True)
from provider_converter.converter import Converter
restore_sys_path()

conv = Converter(
    "openai_completion",
    model="gpt-4o-mini",
    input=[{"role": "user", "content": "Hello"}],
    max_tokens=128
)
payload = conv.information
```

Notes:
- `model` and `input` are required and validated.
- Generic keys like `input` and `max_tokens` are translated using the mapping
  in `base_arg_match.json` (for example, `input` -> `messages`).

### Files manager

`src/public/run_lib/files_manager/manager.py` provides utilities for working
with repository-relative paths and filesystem IO:

- `return_path_of_dir_under_root_dir()` finds a top-level directory (ex: `config`)
- `return_dir_member()` lists files and directories in a path
- `return_full_free()` does a BFS traversal and returns a flat listing
- `read_file()`, `read_json()`, `write_content_tofile()` read/write content with
  optional encoding detection via `chardet`

Example:

```python
from simple_import import change_sys_path, restore_sys_path

change_sys_path(to_runlib=True)
from files_manager.manager import return_path_of_dir_under_root_dir, read_json
restore_sys_path()

config_root = return_path_of_dir_under_root_dir("config")
schema = read_json(f"{config_root}/sys_conf/escape_table.json")
```

### Static helpers

`src/public/static_lib/checker/version_checker.py` exposes a lightweight
`check_packages()` helper to check import availability without importing.

```python
from simple_import import change_sys_path, restore_sys_path

change_sys_path(to_staticlib=True)
from checker.version_checker import check_packages
restore_sys_path()

print(check_packages(["requests", "chardet", "PySide6"]))
```

## Configuration

`config/sys_conf` stores provider metadata and conversion rules:

- `base_arg_match.json` defines generic argument mappings and required fields.
- `escape_table.json` provides the allowed parameter sets and output schema
  shapes for supported providers.

The `Converter` class reads both files to validate types and translate generic
arguments into provider-specific payloads.

## Tests and sandbox

There is no automated test runner yet. A manual sandbox tree exists under
`src/.test/sandbox/` that mirrors parts of `run_lib` and `static_lib` for quick
experimentation and isolated checks.

## Type stubs

`src/stubs/` contains `.pyi` files for the `run_lib` modules so editors can
provide type hints without importing the runtime code.

## Development notes

- Keep new runtime modules under `src/public/run_lib` and static helpers under
  `src/public/static_lib`.
- Use `src/simple_import.py` to resolve those libraries before importing them.
- `storage/` is treated as runtime output and should stay out of source control.

## Status

The repository currently provides reusable building blocks rather than a full
application. The root launcher scripts and `src/GUI/` are placeholders for
future expansion.
