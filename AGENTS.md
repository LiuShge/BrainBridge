# BrainBridge Developer Notes / BrainBridge 开发者说明

This file is for human developers and future maintainers. Keep it direct, practical, and aligned with the current tree.

## English

- The runtime modules live under `src/public/run_lib` and `src/public/static_lib`.
- Use `src/bootstrap_source_dir.py` to add `src` to `sys.path`.
- Use `src/bootstrap_paths.py` to add either `run_lib` or `static_lib` to `sys.path`.
- Some subpackages keep a local copy of `bootstrap_source_dir.py` so direct execution inside that package still works.
- Do not reintroduce `simple_import.py` or `set_source_dir.py`; those are legacy names.
- Keep changes small and focused. Prefer local fixes, path/bootstrap updates, or doc updates over broad restructuring.
- The current smoke tests are:
  - `python src/bootstrap_paths.py`
  - `python src/.test/test_2.py`
  - `python src/.test/test_1.py` when file-tree helpers change
  - `python src/public/static_lib/logger/log_core.py` when logging changes
- `src/.test/test_5.py` depends on `pynput`; do not treat it as a universal smoke test.
- `config/sys_conf` is the default layer. `config/user_conf` overrides it.
- `storage/` is runtime output. Do not commit generated files from there unless they are intentional fixtures.
- Before changing a public API, read the relevant source file and update both README files and both instruction manuals.
- Keep repository guidance factual. Avoid marketing language.

## 中文

- 真实的运行时代码位于 `src/public/run_lib` 和 `src/public/static_lib`。
- 使用 `src/bootstrap_source_dir.py` 把 `src` 加入 `sys.path`。
- 使用 `src/bootstrap_paths.py` 把 `run_lib` 或 `static_lib` 加入 `sys.path`。
- 某些子包保留了本地版 `bootstrap_source_dir.py`，这样在子包内直接执行也能工作。
- 不要再把 `simple_import.py` 或 `set_source_dir.py` 加回来；它们已经是旧名字。
- 改动尽量小而集中。优先做局部修补、路径引导更新或文档更新，不要轻易重构目录结构。
- 当前可用的烟雾测试：
  - `python src/bootstrap_paths.py`
  - `python src/.test/test_2.py`
  - 文件树工具变更时跑 `python src/.test/test_1.py`
  - 日志模块变更时跑 `python src/public/static_lib/logger/log_core.py`
- `src/.test/test_5.py` 依赖 `pynput`，不能把它当成通用烟雾测试。
- `config/sys_conf` 是默认层，`config/user_conf` 会覆盖它。
- `storage/` 只是运行时输出，不要把生成文件当源码提交，除非它们是刻意保留的 fixture。
- 在修改公共 API 之前，先读对应源码，并同步更新两份 README 和两份 instruction 文档。
- 仓库说明要保持事实和实用，不要写宣传语。
