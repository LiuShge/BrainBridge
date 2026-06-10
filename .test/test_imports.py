import json
import importlib
import tempfile
from pathlib import Path

from brainbridge import Converter, Logger, LogLevels, Operator, Request
from brainbridge.lib.runtime.file_utils import aggregate_to_backup, read_json, unpack_from_backup, write_json
from brainbridge.lib.runtime.provider_converter import (
    Converter as RuntimeConverter,
    build_headers,
    list_providers,
    provider_exists,
    unwrap_response,
)
from brainbridge.lib.runtime.requests_core import Request as RuntimeRequest, iter_sse_json
from brainbridge.lib.runtime.terminal_core import (
    Key,
    KeyCode,
    decode_escape_sequence,
    decode_single_char,
)
from brainbridge.lib.static.logger import Logger as StaticLogger, log_to_file
from brainbridge.utils import Time, detect


assert Converter is RuntimeConverter
assert Request is RuntimeRequest
assert Logger is StaticLogger
assert LogLevels.INFO.value == "INFO"
assert hasattr(Operator, "HeadersBuilder")
assert Time.__name__ == "Time"
assert build_headers("token", include_accept=True)["Accept"] == "application/json"
assert provider_exists("openai_completion") is True
assert "openai_completion" in list_providers()
assert unwrap_response(
    "openai_completion",
    {
        "choices": [{"message": {"content": "Paris."}}],
        "usage": {"total_tokens": 1},
    },
)["response_text"] == "Paris."
assert list(iter_sse_json([{"data": "{\"x\": 1}"}, {"data": "[DONE]"}])) == [{"x": 1}]
assert decode_escape_sequence("\x1b[A") == Key.up
assert decode_single_char("a") == KeyCode.from_char("a")
assert detect(b"hello").get("encoding")

with tempfile.TemporaryDirectory() as tmpdir:
    json_path = Path(tmpdir) / "sample.json"
    log_path = Path(tmpdir) / "sample.jsonl"
    write_json(str(json_path), {"hello": "world"}, indent=2)
    assert read_json(str(json_path)) == {"hello": "world"}
    assert callable(aggregate_to_backup)
    assert callable(unpack_from_backup)

    log_to_file("hello", level=LogLevels.INFO, file_path=str(log_path))
    log_record = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert log_record["TEXT"] == "hello"

for removed_module in ("brainbridge.run_lib", "brainbridge.static_lib"):
    try:
        importlib.import_module(removed_module)
    except ImportError:
        pass
    else:
        raise AssertionError(f"{removed_module} should no longer be importable")
