# BrainBridge

BrainBridge 是一个面向本地仓库使用的 Python 工具集，现在采用标准的可编辑安装方式。

当前主要能力包括：

- provider 参数转换
- 基于 `urllib` 的 HTTP / SSE 请求
- 线程请求分发
- 文件工具与 `.bb` 打包
- 结构化日志与完整性校验
- 基于终端 raw 模式的交互工具

[English](./README.md) | 中文版本 | [使用说明](./instruction.md) | [中文使用说明](./instruction.zh-CN.md)

## 安装

使用 Python 3.12+，并在仓库根目录执行：

```bash
python3 -m pip install -e .
```

BrainBridge 现在通过 `brainbridge.*` 包路径导入，不再依赖 `sys.path` 引导才能使用。

## 目录结构

- `brainbridge/run_lib`：对外运行时工具
- `brainbridge/static_lib`：对外日志、校验、信息读取等辅助工具
- `brainbridge/run_lib/terminal_core`：内置终端 raw 输入内核
- `config/sys_conf`：默认配置层
- `config/user_conf`：覆盖配置层
- `storage/`：运行输出目录
- `.test/sandbox/base`：原始 sandbox 基线
- `.test/sandbox/YYYY-MM-DD`：按日期归档的 sandbox 快照

## 导入示例

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

## 核心模块

| 模块 | 作用 |
| --- | --- |
| `brainbridge/run_lib/files_manager/manager.py` | 文件读写、目录树遍历、JSON 读取、根目录路径定位 |
| `brainbridge/run_lib/mini_tools/chardet.py` | 仓库内置的 `detect()` 编码检测替代实现 |
| `brainbridge/run_lib/mini_tools/files_convg.py` | `.bb` 打包/解包工具，支持可选文件树头 |
| `brainbridge/run_lib/mini_tools/decision_panel.py` | 终端选择面板 |
| `brainbridge/run_lib/terminal_core/keyboard.py` | 带少量 `pynput` 风格接口的 raw 终端键盘监听 |
| `brainbridge/run_lib/provider_converter/converter.py` | provider 参数转换与响应解析 |
| `brainbridge/run_lib/requests_core/request_core.py` | 基于 `urllib` 的请求内核 |
| `brainbridge/run_lib/requests_core/thread_requests/thread_requests.py` | 线程请求池 |
| `brainbridge/static_lib/logger/log_core.py` | 结构化日志 |
| `brainbridge/static_lib/checker/checker.py` | 版本、依赖、哈希和备份检查 |

## 依赖策略

- 运行时依赖现在只使用标准库。
- 旧的 bootstrap 辅助文件已经从现行源码树中移除。
- HTTP 由 `urllib` 处理。
- 编码检测由 `brainbridge.run_lib.mini_tools.chardet.detect` 处理。
- 终端按键监听由 `brainbridge.run_lib.terminal_core.keyboard` 处理。

## 说明

- `DecisionPanelPage` 不再需要 `pynput`，现在使用内置 raw 终端输入后端。
- `Converter(...)` 只有在显式传入时才会带上 `stream`。
- `DecisionPanelPage` 现在把 `Enter` 和 `Tab` 都视为确认键。
- `write_content_tofile(..., file_code="auto")` 等接口现在使用仓库内的编码检测器。
- `.bb` 归档可以选择性嵌入紧凑文件树头，方便快速检查与校验。
- `terminial_core`、`ResponseUnwarp` 和 `unwarp()` 仍保留为兼容别名。

## 更多示例

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

## `.bb` 格式规范

`.bb` 归档采用 UTF-8、按行分隔的文本容器格式：

```text
BBPACK/3
META {"kind":"backup","version":3,"b64_wrap":76,"chunk_size":1048576}
META {"kind":"root","root_id":"<sha16>","root_posix":"<root path>"}
META {"kind":"tree_header","format":"compact-tree-v1","line_count":N,"sha256":"<digest>"}   # 可选
TREE_BEGIN
TREE_DATA <base64 编码后的 JSON 文件树头>                                                      # 可选
TREE_END                                                                                        # 可选
FILE_BEGIN
FILE_META {"root_id":"<sha16>","rel":"root 内相对路径","src_full_posix":"<源路径>","encoding":"b64"}
FILE_DATA <base64 载荷分块>
FILE_CHECK {"size":123,"sha256":"<digest>"}
FILE_END
...
BBPACK_END
```

- `TREE_*` 记录是可选的，用于快速查看紧凑文件树。
- `FILE_DATA` 始终是 Base64 文本；恢复时会同时校验 `size` 和 `sha256`。
- `rel` 必须保持相对且安全；解包会拒绝绝对路径和 `..` 路径穿越。

## 配置

Provider 转换会读取：

- `config/sys_conf/base_arg_match.json`
- `config/sys_conf/escape_table.json`
- `config/user_conf/base_arg_match.json`
- `config/user_conf/escape_table.json`

`user_conf` 会覆盖 `sys_conf`。

## 推荐检查

先执行 `python3 -m pip install -e .`，然后跑：

```bash
python3 .test/test_2.py
python3 .test/test_1.py
python3 .test/test_7.py
python3 -m py_compile $(rg --files -g '*.py' .test brainbridge)
python3 -m brainbridge.static_lib.logger.log_core
```

如果改了终端交互相关代码，再补跑：

```bash
python3 .test/test_5.py
```

## 实用说明

- `.test/test_5.py` 是 decision panel / 终端后端的内部烟雾测试。
- 优先使用 `Operator.ResponseUnwrap.unwrap(...)`；`ResponseUnwarp` 和 `unwarp()` 仍是兼容别名。
- `storage/` 是运行输出目录，不是源码目录。

## 许可证

MIT。
