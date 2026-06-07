# BrainBridge Developer Notes / BrainBridge 开发者说明

Keep this file practical and aligned with the current tree.

## English

- Runtime modules live under `src/public/run_lib` and `src/public/static_lib`.
- Install the repo with `python3 -m pip install -e .` before running local smoke tests.
- New code should import from `src.public...` directly. Do not add new `sys.path` bootstrap dependencies.
- The old bootstrap helper files have been removed from the active source tree.
- Do not reintroduce `requests`, `chardet`, or `pynput` as core runtime dependencies.
- `src/public/run_lib/terminial_core` is the terminal input backend. Keep the directory name as-is.
- `config/sys_conf` is the default layer. `config/user_conf` overrides it.
- `storage/` is runtime output. Do not commit generated files from there unless they are intentional fixtures.
- Sandbox archives under `src/.test/sandbox/` use `base/` for the baseline and `YYYY-MM-DD/` for dated snapshots.
- If you change public APIs or behavior, update both README files and both instruction manuals.
- Preferred smoke tests:
  - `python3 src/.test/test_2.py`
  - `python3 src/.test/test_1.py` when file helpers or `.bb` helpers change
  - `python3 src/.test/test_7.py` when `.bb` header behavior changes
  - `python3 src/.test/test_5.py` when terminal interaction changes
  - `python3 -m src.public.static_lib.logger.log_core` when logging changes

## 中文

- 运行时代码位于 `src/public/run_lib` 和 `src/public/static_lib`。
- 本地验证前先执行 `python3 -m pip install -e .`。
- 新代码直接从 `src.public...` 导入，不要再新增 `sys.path` 引导依赖。
- 旧的 bootstrap 辅助文件已经从现行源码树中移除。
- 不要把 `requests`、`chardet`、`pynput` 重新引回核心运行时依赖。
- `src/public/run_lib/terminial_core` 是终端输入后端，目录名保持现状即可。
- `config/sys_conf` 是默认层，`config/user_conf` 会覆盖它。
- `storage/` 只是运行输出目录，不要把生成文件当源码提交，除非它们是刻意保留的 fixture。
- `src/.test/sandbox/` 里的 sandbox 归档规则是：`base/` 保存基线，`YYYY-MM-DD/` 保存日期快照。
- 如果修改了公共 API 或行为，记得同步两份 README 和两份 instruction 文档。
- 推荐烟雾测试：
  - `python3 src/.test/test_2.py`
  - 文件工具或 `.bb` 工具改动时跑 `python3 src/.test/test_1.py`
  - `.bb` 文件树头改动时跑 `python3 src/.test/test_7.py`
  - 终端交互改动时跑 `python3 src/.test/test_5.py`
  - 日志模块改动时跑 `python3 -m src.public.static_lib.logger.log_core`
