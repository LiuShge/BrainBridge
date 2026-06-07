import os

from src.public.run_lib.provider_converter.converter import Converter
from src.public.run_lib.requests_core.request_core import Request
from src.public.static_lib.logger.log_core import Logger, LogLevels

print("--- Testing editable-install style imports ---")
print(f"Working directory: {os.getcwd()}")
print(f"Converter class found: {Converter.__name__}")
print(f"Request class found: {Request.__name__}")

test_logger = Logger(level=LogLevels.INFO, text="Import test success via package imports")
print(f"Logger class found: {test_logger.__class__.__name__}")
print("Log Output:")
print(test_logger.text_log_builder())

for method_name in ("get", "post", "put", "delete"):
    try:
        getattr(Request(), method_name)()
    except ValueError as exc:
        assert "requires at least one URL" in str(exc)
    else:
        raise AssertionError(f"Request.{method_name}() should reject empty URL input")

payload = Converter(
    "openai_completion",
    model="openai/gpt-oss-20b",
    messages=[],
).information
assert "stream" not in payload

valid_payload = Converter(
    "openai_completion",
    model="openai/gpt-oss-20b",
    messages=[{"role": "user", "content": "hello"}],
).information
assert valid_payload["messages"][0]["role"] == "user"

invalid_messages = [
    [1, 2, 3],
    [{"role": "invalid", "content": "hello"}],
    [{"role": "assistant", "content": "hello", "tool_calls": ["bad"]}],
]

for bad_messages in invalid_messages:
    try:
        Converter("openai_completion", model="openai/gpt-oss-20b", messages=bad_messages)
    except ValueError:
        pass
    else:
        raise AssertionError(f"messages should be rejected: {bad_messages!r}")
