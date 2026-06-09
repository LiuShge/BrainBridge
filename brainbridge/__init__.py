"""Public BrainBridge APIs and package namespaces."""

from importlib import import_module

__all__ = [
    "Converter",
    "LogLevels",
    "Logger",
    "Operator",
    "Request",
    "RequestException",
    "Response",
]


def __getattr__(name: str):
    if name in {"Converter", "Operator"}:
        module = import_module("brainbridge.lib.runtime.provider_converter")
        return getattr(module, name)
    if name in {"Request", "RequestException", "Response"}:
        module = import_module("brainbridge.lib.runtime.requests_core")
        return getattr(module, name)
    if name in {"Logger", "LogLevels"}:
        module = import_module("brainbridge.lib.static.logger")
        return getattr(module, name)
    raise AttributeError(f"module 'brainbridge' has no attribute {name!r}")
