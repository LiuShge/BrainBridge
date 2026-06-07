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

BrainBridge 现在正常通过 `src.*` 包路径导入，不再依赖 `sys.path` 引导才能使用。

## 目录结构

- `src/public/run_lib`：运行时工具
- `src/public/static_lib`：日志、校验、信息读取等辅助工具
- `src/public/run_lib/terminial_core`：内置终端 raw 输入内核
- `config/sys_conf`：默认配置层
- `config/user_conf`：覆盖配置层
- `storage/`：运行输出目录
- `src/.test/sandbox/base`：原始 sandbox 基线
- `src/.test/sandbox/YYYY-MM-DD`：按日期归档的 sandbox 快照

## 导入示例

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

## 核心模块

| 模块 | 作用 |
| --- | --- |
| `src/public/run_lib/files_manager/manager.py` | 文件读写、目录树遍历、JSON 读取、根目录路径定位 |
| `src/public/run_lib/mini_tools/chardet.py` | 仓库内置的 `detect()` 编码检测替代实现 |
| `src/public/run_lib/mini_tools/files_convg.py` | `.bb` 打包/解包工具，支持可选文件树头 |
| `src/public/run_lib/mini_tools/decision_panel.py` | 终端选择面板 |
| `src/public/run_lib/terminial_core/keyboard.py` | 带少量 `pynput` 风格接口的 raw 终端键盘监听 |
| `src/public/run_lib/provider_converter/converter.py` | provider 参数转换与响应解析 |
| `src/public/run_lib/requests_core/request_core.py` | 基于 `urllib` 的请求内核 |
| `src/public/run_lib/requests_core/thread_requests/thread_requests.py` | 线程请求池 |
| `src/public/static_lib/logger/log_core.py` | 结构化日志 |
| `src/public/static_lib/checker/checker.py` | 版本、依赖、哈希和备份检查 |

## 说明

- 运行时依赖现在只使用标准库。
- 旧的 bootstrap 辅助文件已经从现行源码树中移除。
- `DecisionPanelPage` 不再需要 `pynput`，现在使用内置 raw 终端输入后端。
- `Converter(...)` 只有在显式传入时才会带上 `stream`。
- `DecisionPanelPage` 现在把 `Enter` 和 `Tab` 都视为确认键。
- `write_content_tofile(..., file_code="auto")` 等接口现在使用仓库内的编码检测器。
- `.bb` 归档可以选择性嵌入紧凑文件树头，方便快速检查与校验。

## 推荐检查

先执行 `python3 -m pip install -e .`，然后跑：

```bash
python3 src/.test/test_2.py
python3 src/.test/test_1.py
python3 src/.test/test_7.py
python3 -m src.public.static_lib.logger.log_core
```

如果改了终端交互相关代码，再补跑：

```bash
python3 src/.test/test_5.py
```

## 许可证

MIT。
