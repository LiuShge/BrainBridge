# BrainBridge Developer Notes / BrainBridge 开发者说明

Keep this file practical and aligned with the current repository layout.

## English

- Recommended package paths:
  - `brainbridge/lib/runtime`
  - `brainbridge/lib/static`
  - `brainbridge/utils`
  - `brainbridge/lib/runtime/file_utils`
- The historical compatibility packages have been removed. Do not reintroduce them.
- Install locally with `python3 -m pip install -e .` before validation.
- New code should import from `brainbridge...` directly. Do not add new `sys.path` bootstrap dependencies.
- Public file helpers should be re-exported from `brainbridge/lib/runtime/file_utils/__init__.py`. Do not make application code import from `general.py` or `bb_utils.py` directly.
- Do not rewrite internal module architecture unless the task explicitly asks for it.
- Do not expose private APIs such as `_ConfigEngine`, `_RawKeyReader`, or other underscore-prefixed internals.
- `config/sys_conf` is the default layer. `config/user_conf` overrides it.
- Tooling may write `user_conf`, but it must not silently or automatically modify `sys_conf`.
- `storage/` is not a required runtime dependency anymore. Do not add new runtime assumptions around it.
- Runtime dependencies must remain standard-library only. Do not introduce `requests`, external `chardet`, or `pynput` as runtime requirements.
- `brainbridge/lib/runtime/terminal_core` is the authoritative terminal input backend.
- `brainbridge/utils` is the current home of the utility surface that replaced `mini_tools`.
- `brainbridge/lib/runtime/file_utils` is the public namespace for runtime file helpers and `.bb` helpers.
- If you change public APIs or behavior, update:
  - `README.md`
  - `README.zh-CN.md`
  - `instruction.md`
  - `instruction.zh-CN.md`
  - `AGENTS.md` when workflow rules also changed
- Recommended verification commands:
  - `python3 -m py_compile $(find brainbridge .test -name '*.py')`
  - `python3 -m pytest`
- `python3 .test/test_2.py`
- `python3 .test/test_1.py` when file helpers or `.bb` helpers change
- `python3 .test/test_5.py` when terminal interaction changes
- `python3 .test/test_7.py` when `.bb` header behavior changes
- `python3 -m pytest` after file utility or ignore-logic changes

## 中文

- 推荐包路径：
  - `brainbridge/lib/runtime`
  - `brainbridge/lib/static`
  - `brainbridge/utils`
- 历史兼容包已经删除，不要重新引回这些旧路径。
- 本地验证前先执行 `python3 -m pip install -e .`。
- 新代码直接从 `brainbridge...` 导入，不要再新增 `sys.path` bootstrap 依赖。
- 除非任务明确要求，否则不要重写内部模块架构。
- 不要暴露 `_ConfigEngine`、`_RawKeyReader` 或其他以下划线开头的私有 API。
- `config/sys_conf` 是默认层，`config/user_conf` 负责覆盖。
- 工具层可以写 `user_conf`，但绝不能静默或自动修改 `sys_conf`。
- `storage/` 已不再是必须的运行时依赖，不要重新引入对它的运行时假设。
- 运行时依赖必须保持标准库-only，不要引入 `requests`、外部 `chardet` 或 `pynput` 作为运行时依赖。
- `brainbridge/lib/runtime/terminal_core` 是权威终端输入后端。
- `brainbridge/utils` 是替代旧 `mini_tools` 的正式工具面。
- 如果修改了公共 API 或行为，需要同步更新：
  - `README.md`
  - `README.zh-CN.md`
  - `instruction.md`
  - `instruction.zh-CN.md`
  - 如果工作规则也变了，再更新 `AGENTS.md`
- 推荐验证命令：
  - `python3 -m py_compile $(find brainbridge .test -name '*.py')`
  - `python3 -m pytest`
  - `python3 .test/test_2.py`
  - 文件工具或 `.bb` 工具改动时跑 `python3 .test/test_1.py`
  - 终端交互改动时跑 `python3 .test/test_5.py`
  - `.bb` 文件树头行为改动时跑 `python3 .test/test_7.py`
