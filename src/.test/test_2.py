import os
from typing import Dict, Any
from sys import path as sys_path

# 1. 尝试导入 simple_import 模块（这是我们调整 sys.path 的入口点）
try:
    import simple_import
except ImportError:
    print("FATAL: set_source_dir.py not found or accessible.")
    # 如果找不到 simple_import，通常说明当前工作目录不对。
    # 在实际测试中，你需要确保当前执行位置能让它被找到。
    exit(1)

# 2. 缓存初始状态 (重要：这是 restore_sys_path 的前提)
try:
    initial_sys_path = sys_path.copy()

    # --- 测试用例 1: 导入 run_lib 模块 ---
    print("--- Testing run_lib import (provider_converter) ---")

    # 动态设置环境，让 converter 模块可见
    simple_import.change_sys_path(to_runlib=True)

    # 现在可以尝试导入深度依赖的模块
    from provider_converter.converter import Converter
    from requests_core.request_core import Request

    # 实例化以验证导入的类是否工作正常（使用一个最小的测试）
    try:
        # 尝试初始化一个 Converter 来验证依赖是否都到了位
        # 注意：这里需要一个假的配置环境，为简化测试，我们只检查类是否存在
        # 实际测试中，应创建临时的 config 结构或模拟 ConfigEngine

        # 仅测试类名，不测试配置加载的复杂性
        print(f"Converter class found: {Converter.__name__}")
        print(f"Request class found: {Request.__name__}")

    except Exception as e:
        print(f"RunLib module loading failed: {e}")

    # --- 测试用例 2: 导入 static_lib 模块 ---
    print("\n--- Testing static_lib import (logger) ---")

    # 动态设置环境，让 log_core 模块可见 (注意：这会覆盖上一次的 path 修改)
    simple_import.change_sys_path(to_staticlib=True)

    from logger.log_core import Logger, LogLevels

    try:
        # 实例化 Logger 检查
        test_logger = Logger(level=LogLevels.INFO, text="Import Test Success via simple_import")
        print(f"Logger class found: {test_logger.__class__.__name__}")

        # 打印一个日志（因为没有文件管理器，我们只打印到控制台）
        print("Log Output:")
        print(test_logger.text_log_builder())

    except Exception as e:
        print(f"StaticLib module loading failed: {e}")


finally:
    # 3. 清理环境 (无论成功还是失败，都恢复 sys.path)
    simple_import.restore_sys_path()

    # 验证是否恢复成功
    if sys_path == initial_sys_path:
        print("\n--- Cleanup Successful: sys.path restored to initial state. ---")
    else:
        print(f"\n--- Cleanup Warning: sys.path was NOT fully restored. Current: {sys_path}")

