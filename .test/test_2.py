import os

from brainbridge.lib.runtime.provider_converter.converter import Converter
from brainbridge.lib.runtime.requests_core.request_core import Request, Response
from brainbridge.lib.static.logger.log_core import Logger, LogLevels

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


class _FakeSSERaw:
    code = 200
    status = 200
    reason = "OK"
    headers = {"Content-Type": "text/event-stream; charset=utf-8"}

    def __init__(self) -> None:
        self._lines = iter([
            b"id: 1\n",
            b"event: message\n",
            b"data: first\n",
            b"\n",
            b"data: [DONE]\n",
            b"\n",
        ])
        self.read_called = False

    def geturl(self) -> str:
        return "https://example.test/sse"

    def read(self, *_args, **_kwargs) -> bytes:
        self.read_called = True
        raise AssertionError("SSE should be consumed with readline(), not read(chunk_size)")

    def readline(self) -> bytes:
        return next(self._lines, b"")

    def close(self) -> None:
        pass


fake_raw = _FakeSSERaw()
original_make_request = Request._make_request


def _fake_make_request(method, url, **kwargs):
    assert method == "POST"
    assert url == "https://example.test/sse"
    assert kwargs["headers"]["Accept"] == "text/event-stream"
    assert kwargs["stream"] is True
    return Response(fake_raw, preload_content=False)


try:
    Request._make_request = staticmethod(_fake_make_request)
    events = list(Request().request_sse("POST", "https://example.test/sse"))
finally:
    Request._make_request = original_make_request

assert events == [
    {"id": "1", "event": "message", "data": "first"},
    {"id": "", "event": "", "data": "[DONE]"},
]
assert fake_raw.read_called is False
