from __future__ import annotations

import threading
import io
from dataclasses import dataclass, field
from typing import (
    Any, BinaryIO, IO, Iterable, Mapping, Optional, Tuple, Union, Literal, List
)

# ==========================================
# Type Definitions
# ==========================================
FileContent = Union[bytes, str, BinaryIO, io.BytesIO, IO[bytes]]
FileValue = Union[
    FileContent,
    Tuple[Optional[str], FileContent],
    Tuple[Optional[str], FileContent, str],
    Tuple[Optional[str], FileContent, str, Mapping[str, str]],
]


# ==========================================
# Data Models
# ==========================================

@dataclass(frozen=True, slots=True)
class RequestTask:
    """
    Data container for a single request task.
    :param task_id: unique identifier for the task
    :param method: HTTP method or "sse"
    :param urls: tuple of URL strings
    :param kwargs: additional arguments for the request method
    Example:
    >>> task = RequestTask("001", "get", ("https://example.com",))
    """
    task_id: str
    method: Literal["get", "post", "put", "delete", "sse"]
    urls: Tuple[str, ...] = field(default_factory=tuple)
    kwargs: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class TaskResult:
    """
    Data container for the result of a request task.
    :param task_id: identifier of the original task
    :param success: boolean indicating if the request was successful
    :param value: the Response object or an Iterable (for SSE)
    :param error: exception message if success is False
    Example:
    >>> res = TaskResult("001", True, "result_object")
    """
    task_id: str
    success: bool
    value: Any = None
    error: Optional[str] = None


# ==========================================
# Core Logic
# ==========================================

class RequestWorker(threading.Thread):
    def __init__(self, req_instance: Any, task: RequestTask):
        """
        :param req_instance: the Request engine instance
        :param task: RequestTask object defining what to do
        Example:
        >>> worker = RequestWorker(None, RequestTask("1", "get"))
        """
        super().__init__()
        self._req = req_instance
        self._task = task
        self.result: Optional[TaskResult] = None

    def run(self) -> None:
        """
        Executes the task and stores the result.
        :return: None
        """
        try:
            val = self._execute()
            self.result = TaskResult(self._task.task_id, True, value=val)
        except Exception as e:
            self.result = TaskResult(self._task.task_id, False, error=f"{type(e).__name__}: {str(e)}")

    def _execute(self) -> Any:
        """
        Dispatches the task to the correct method of the Request instance.
        :return: The return value of the request method
        """
        method_name = self._task.method.lower()
        args = self._task.urls
        kwargs = dict(self._task.kwargs)

        if method_name == "sse":
            # SSE usually requires specific 'method' and 'url' instead of *urls
            m = kwargs.pop("method", "GET")
            u = kwargs.pop("url", args[0] if args else None)
            if not u:
                raise ValueError("SSE requires a URL")
            return self._req.request_sse(method=m, url=u, **kwargs)

        # Standard methods: get, post, put, delete
        func = getattr(self._req, method_name, None)
        if not func:
            raise AttributeError(f"Request instance has no method '{method_name}'")

        return func(*args, **kwargs)


class RequestPool:
    def __init__(self, req_instance: Any):
        """
        :param req_instance: Shared Request instance for all threads
        Example:
        >>> pool = RequestPool(None)
        """
        self._req = req_instance

    def execute_all(self, tasks: Iterable[RequestTask]) -> List[TaskResult]:
        """
        Starts all tasks in parallel and waits for completion.
        :param tasks: An iterable of RequestTask objects
        :return: List of TaskResult objects
        Example:
        >>> pool = RequestPool(None)
        >>> # results = pool.execute_all([task1, task2])
        """
        workers = [RequestWorker(self._req, t) for t in tasks]

        for w in workers:
            w.start()

        for w in workers:
            w.join()

        return [w.result for w in workers if w.result is not None]


# ==========================================
# Simulation & Test Execution
# ==========================================