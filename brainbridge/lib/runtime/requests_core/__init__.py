"""Request-core APIs for BrainBridge runtime."""

import json
from typing import Any, Iterable, Iterator, Mapping

from .request_core import Request, RequestException, Response


def iter_sse_json(events: Iterable[Mapping[str, str]], *, done_token: str = "[DONE]") -> Iterator[Any]:
    """Yield decoded JSON payloads from ``Request.request_sse`` event dictionaries."""
    for event in events:
        data = event.get("data", "")
        if not data or data.strip() == done_token:
            continue
        yield json.loads(data)


__all__ = ["Request", "RequestException", "Response", "iter_sse_json", "thread_requests"]
