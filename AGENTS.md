
# Repository Guidelines

## Project Structure & Module Organization
- The repo is rooted in `src/` (core logic), `config/` (runtime, sys, user conf folders), and `storage/` (generated logs and program metadata), with helper scripts (`simple_import.py`, `launcher.py`, `_launcher.py`, `_reset.py`) at the root.
- `src/` splits into `public/run_lib` (service helpers such as `requests_core` and `provider_converter`), `public/static_lib`, GUI stubs under `GUI/`, and a manual sandbox under `.tests/`. Use `simple_import.py` when you need to resolve those run/static libraries before importing other subpackages.
- Keep future modules in `src/` and `src/public`; mirror the current naming so `snake_case` folders map to Python modules and duplicate interfaces live in `run_lib`/`static_lib` when shared across runtimes.

## Build, Test, and Development Commands
- Activate the bundled virtual environment first (`.\.venv\Scripts\Activate.ps1` on PowerShell, `source .venv/Scripts/activate` on Unix). Then work from the repository root to keep relative imports stable.
- Run `python simple_import.py` to confirm the dynamic loader finds `run_lib` and `static_lib` before spinning up more complex scripts. This script demonstrates the expected `requests_core` import path.
- Sprint through the minimal sandbox test with `python src/.tests/sandbox/test.py`; it only prints its own path but verifies the interpreter can traverse the hidden `.tests` tree. There is currently no automated build step beyond these lightweight invocations.

## Coding Style & Naming Conventions
- Follow Python idioms: four-space indentation, ASCII-safe identifiers, docstrings on public helpers, and `snake_case` for functions/modules alongside `PascalCase` for classes. Keep constants UPPERCASE in shared configs.
- Mirror the small examples already committed (see `simple_import.py`) for spacing, inline error handling, and logging-style comments. Avoid magic numbers; document expectations when a directory name, such as `src/public/run_lib`, is required.
- No additional formatter is configured yet; run `python -m py_compile ...` or your linting tool of choice before merging, but keep changes short and focused.

## Testing Guidelines
- Tests live under `src/.tests/`. Give new files a `test_*.py` name, add them alongside the sandbox directory if they exercise GUI bits, and keep assertions simple while you expand tooling.
- Use the sandbox stub (`python src/.tests/sandbox/test.py`) as a template to make sure imports resolve before adding heavier suites or dependencies. There is no coverage tooling yet, so document any manual verification meant to accompany a change.

## Commit & Pull Request Guidelines
- The repository currently lacks version history, so adopt a transparent commit narrative: single-topic changes, imperative summaries, and (once Git is enabled) a `type(scope): summary` pattern helps future contributors.
- Every PR should explain the change, list the smoke-test commands (`python simple_import.py`, relevant sandbox test), and mention any environmental configuration touched in `config/*`. Include screenshots only if the UI surface in `src/GUI/` changes.

## Configuration & Environment Notes
- Store editable runtime bits under `config/runtime_conf`, system defaults under `config/sys_conf`, and user overrides under `config/user_conf`. Do not commit secrets into these directories; treat them as live configuration vaults.
- `storage/` is purely runtime output—log files, telemetry, and crafted program information. Clean it before packaging or exposing the repository to a public channel.
