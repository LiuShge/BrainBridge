"""Runtime library packages for BrainBridge."""

from importlib import import_module

__all__ = [
    "file_utils",
    "provider_converter",
    "requests_core",
    "terminal_core",
]


def __getattr__(name: str):
    if name in {"file_utils", "provider_converter", "requests_core", "terminal_core"}:
        return import_module(f"brainbridge.lib.runtime.{name}")
    raise AttributeError(f"module 'brainbridge.lib.runtime' has no attribute {name!r}")
