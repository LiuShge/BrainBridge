from __future__ import annotations

import base64
import io
import json as _json
import mimetypes
import ssl
from os import path
from time import localtime
from typing import (
    IO,
    Any,
    BinaryIO,
    Dict,
    Iterable,
    List,
    Literal,
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
    Union,
)
from urllib import error as _url_error
from urllib import parse as _url_parse
from urllib import request as _url_request
from uuid import uuid4

__all__ = [
    "FILE_PATH",
    "FileContent",
    "FileValue",
    "RequestException",
    "Response",
    "Request",
]

FILE_PATH = __file__

FileContent = Union[
    bytes,
    str,
    BinaryIO,
    io.BytesIO,
    IO[bytes],
]
FileValue = Union[
    FileContent,
    Tuple[Optional[str], FileContent],
    Tuple[Optional[str], FileContent, str],
    Tuple[Optional[str], FileContent, str, Mapping[str, str]],
]


class RequestException(RuntimeError):
    """Network-layer exception used by the urllib-backed request engine."""


class Response:
    """A small requests-like compatibility wrapper for urllib responses."""

    def __init__(self, raw: Any, preload_content: bool = True):
        self._raw = raw
        self.url = raw.geturl() if hasattr(raw, "geturl") else ""
        self.status_code = int(getattr(raw, "code", getattr(raw, "status", 0)) or 0)
        self.reason = getattr(raw, "reason", "")
        self.headers: Dict[str, str] = dict(raw.headers.items()) if getattr(raw, "headers", None) else {}
        self._body: Optional[bytes] = None
        self._status_error = not self.ok

        if preload_content:
            self._body = self._read_all()
            self.close()

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 400

    @property
    def content(self) -> bytes:
        if self._body is None:
            self._body = self._read_all()
            self.close()
        return self._body

    @property
    def text(self) -> str:
        encoding = self._detect_encoding()
        return self.content.decode(encoding, errors="replace")

    def json(self) -> Any:
        return _json.loads(self.text)

    def raise_for_status(self) -> None:
        if not self.ok:
            raise RequestException(f"HTTP {self.status_code}: {self.reason or self.text[:200]}")

    def iter_content(self, chunk_size: Optional[int] = None, decode_unicode: bool = False) -> Iterable[Union[bytes, str]]:
        effective_chunk_size = chunk_size or 8192

        if self._body is not None:
            for start in range(0, len(self._body), effective_chunk_size):
                chunk = self._body[start:start + effective_chunk_size]
                if decode_unicode:
                    yield chunk.decode(self._detect_encoding(), errors="replace")
                else:
                    yield chunk
            return

        try:
            while True:
                chunk = self._raw.read(effective_chunk_size)
                if not chunk:
                    break
                if decode_unicode:
                    yield chunk.decode(self._detect_encoding(), errors="replace")
                else:
                    yield chunk
        finally:
            self.close()

    def iter_lines(self, decode_unicode: bool = False) -> Iterable[Union[bytes, str]]:
        if self._body is not None:
            lines = self._body.splitlines(keepends=True)
            for line in lines:
                if decode_unicode:
                    yield line.decode(self._detect_encoding(), errors="replace")
                else:
                    yield line
            return

        try:
            while True:
                line = self._raw.readline()
                if not line:
                    break
                if decode_unicode:
                    yield line.decode(self._detect_encoding(), errors="replace")
                else:
                    yield line
        finally:
            self.close()

    def close(self) -> None:
        if self._raw is not None and hasattr(self._raw, "close"):
            self._raw.close()
        self._raw = None

    def __enter__(self) -> "Response":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"<Response [{self.status_code}]>"

    def _read_all(self) -> bytes:
        if self._raw is None:
            return self._body or b""
        return self._raw.read()

    def _detect_encoding(self) -> str:
        content_type = self.headers.get("Content-Type", "")
        for part in content_type.split(";"):
            part = part.strip()
            if part.lower().startswith("charset="):
                return part.split("=", 1)[1].strip() or "utf-8"
        return "utf-8"


def _normalize_timeout(timeout: Union[int, float, Tuple[Optional[float], Optional[float]], None]) -> Optional[float]:
    if timeout is None:
        return None
    if isinstance(timeout, tuple):
        for item in timeout:
            if item is not None:
                return float(item)
        return None
    return float(timeout)


def _normalize_headers(headers: Optional[Mapping[str, Union[str, bytes, None]]]) -> Dict[str, str]:
    normalized: Dict[str, str] = {}
    for key, value in (headers or {}).items():
        if value is None:
            continue
        normalized[str(key)] = value.decode("utf-8", errors="replace") if isinstance(value, bytes) else str(value)
    return normalized


def _normalize_cookies(cookies: Optional[Union[Mapping[str, str], List[Tuple[str, str]]]]) -> Optional[str]:
    if cookies is None:
        return None
    items = cookies.items() if isinstance(cookies, Mapping) else cookies
    return "; ".join(f"{key}={value}" for key, value in items)


def _normalize_auth(auth: Optional[Tuple[str, str]]) -> Optional[str]:
    if auth is None:
        return None
    token = base64.b64encode(f"{auth[0]}:{auth[1]}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


def _read_file_content(file_content: FileContent) -> bytes:
    if isinstance(file_content, bytes):
        return file_content
    if isinstance(file_content, str):
        return file_content.encode("utf-8")
    data = file_content.read()
    if isinstance(data, str):
        return data.encode("utf-8")
    return data


def _parse_file_value(field_name: str, file_value: FileValue) -> Tuple[Optional[str], bytes, Optional[str], Dict[str, str]]:
    filename: Optional[str] = None
    content_type: Optional[str] = None
    extra_headers: Dict[str, str] = {}

    if isinstance(file_value, tuple):
        tuple_len = len(file_value)
        if tuple_len >= 1:
            filename = file_value[0]
        file_content = file_value[1]
        if tuple_len >= 3:
            content_type = file_value[2]
        if tuple_len >= 4:
            extra_headers = dict(file_value[3])
    else:
        file_content = file_value

    if filename is None and hasattr(file_content, "name"):
        candidate = path.basename(str(getattr(file_content, "name", "")))
        filename = candidate or field_name
    if filename is None:
        filename = field_name

    return filename, _read_file_content(file_content), content_type, extra_headers


def _encode_multipart_body(
    files: Union[Mapping[str, FileValue], Iterable[Tuple[str, FileValue]]],
    data: Optional[Union[str, bytes, Mapping[str, Any]]] = None,
) -> Tuple[bytes, str]:
    boundary = f"brainbridge-{uuid4().hex}"
    body = bytearray()

    if isinstance(data, Mapping):
        for key, value in data.items():
            body.extend(f"--{boundary}\r\n".encode("utf-8"))
            body.extend(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode("utf-8"))
            body.extend(str(value).encode("utf-8"))
            body.extend(b"\r\n")
    elif isinstance(data, str):
        body.extend(f"--{boundary}\r\n\r\n".encode("utf-8"))
        body.extend(data.encode("utf-8"))
        body.extend(b"\r\n")
    elif isinstance(data, bytes):
        body.extend(f"--{boundary}\r\n\r\n".encode("utf-8"))
        body.extend(data)
        body.extend(b"\r\n")

    file_items = files.items() if isinstance(files, Mapping) else files
    for field_name, file_value in file_items:
        filename, payload, content_type, extra_headers = _parse_file_value(field_name, file_value)
        mime_type = content_type or mimetypes.guess_type(filename or "")[0] or "application/octet-stream"

        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        disposition = f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'
        body.extend(disposition.encode("utf-8"))
        body.extend(f"Content-Type: {mime_type}\r\n".encode("utf-8"))
        for header_key, header_value in extra_headers.items():
            body.extend(f"{header_key}: {header_value}\r\n".encode("utf-8"))
        body.extend(b"\r\n")
        body.extend(payload)
        body.extend(b"\r\n")

    body.extend(f"--{boundary}--\r\n".encode("utf-8"))
    return bytes(body), boundary


def _prepare_body_and_headers(
    *,
    data: Optional[Union[str, bytes, Mapping[str, Any]]] = None,
    json_payload: Optional[Mapping[str, Any]] = None,
    files: Optional[Union[Mapping[str, FileValue], Iterable[Tuple[str, FileValue]]]] = None,
    headers: Optional[Mapping[str, Union[str, bytes, None]]] = None,
    auth: Optional[Tuple[str, str]] = None,
    cookies: Optional[Union[Mapping[str, str], List[Tuple[str, str]]]] = None,
) -> Tuple[Optional[bytes], Dict[str, str]]:
    normalized_headers = _normalize_headers(headers)

    auth_header = _normalize_auth(auth)
    if auth_header and "Authorization" not in normalized_headers:
        normalized_headers["Authorization"] = auth_header

    cookie_header = _normalize_cookies(cookies)
    if cookie_header and "Cookie" not in normalized_headers:
        normalized_headers["Cookie"] = cookie_header

    if files is not None:
        body, boundary = _encode_multipart_body(files, data=data)
        normalized_headers.setdefault("Content-Type", f"multipart/form-data; boundary={boundary}")
        normalized_headers["Content-Length"] = str(len(body))
        return body, normalized_headers

    if json_payload is not None:
        body = _json.dumps(json_payload).encode("utf-8")
        normalized_headers.setdefault("Content-Type", "application/json; charset=utf-8")
        normalized_headers["Content-Length"] = str(len(body))
        return body, normalized_headers

    if isinstance(data, Mapping):
        body = _url_parse.urlencode(data, doseq=True).encode("utf-8")
        normalized_headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
        normalized_headers["Content-Length"] = str(len(body))
        return body, normalized_headers

    if isinstance(data, str):
        body = data.encode("utf-8")
        normalized_headers.setdefault("Content-Type", "text/plain; charset=utf-8")
        normalized_headers["Content-Length"] = str(len(body))
        return body, normalized_headers

    if isinstance(data, bytes):
        normalized_headers["Content-Length"] = str(len(data))
        return data, normalized_headers

    return None, normalized_headers


def _append_params(url: str, params: Optional[Mapping[str, Any]]) -> str:
    if not params:
        return url
    parsed = _url_parse.urlsplit(url)
    existing = _url_parse.parse_qsl(parsed.query, keep_blank_values=True)
    merged = existing + list(params.items())
    new_query = _url_parse.urlencode(merged, doseq=True)
    return _url_parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, new_query, parsed.fragment))


def _build_ssl_context(verify: Optional[Union[bool, str]]) -> ssl.SSLContext:
    if verify is False:
        return ssl._create_unverified_context()
    if isinstance(verify, str):
        if path.isdir(verify):
            return ssl.create_default_context(capath=verify)
        return ssl.create_default_context(cafile=verify)
    return ssl.create_default_context()


def _build_opener(proxies: Optional[Mapping[str, str]], verify: Optional[Union[bool, str]], target_url: str) -> Any:
    handlers: List[Any] = [_url_request.HTTPSHandler(context=_build_ssl_context(verify))]
    if proxies:
        scheme = _url_parse.urlsplit(target_url).scheme or "http"
        proxy_url = proxies.get(scheme) or proxies.get(f"{scheme}://")
        if proxy_url:
            handlers.append(_url_request.ProxyHandler({scheme: proxy_url}))
    return _url_request.build_opener(*handlers)


class Request:
    _class_default_timeout = 5

    def __init__(self, enable_logging: bool = False, timeout: Union[int, float, None] = None):
        self._enable_logging = enable_logging
        self._instance_timeout = timeout if timeout is not None else Request._class_default_timeout
        if self._enable_logging:
            self.logs: List[Dict[str, Union[List[str], str]]] = []

    def __len__(self) -> int:
        return len(self.logs) if self._enable_logging else 0

    def _log(self, content: Union[List[str], str]):
        if not self._enable_logging:
            return

        tn = localtime()
        log_time_str = f"{tn.tm_year}-{tn.tm_mon:02d}-{tn.tm_mday:02d} {tn.tm_hour:02d}:{tn.tm_min:02d}:{tn.tm_sec:02d}"

        if isinstance(content, str):
            self.logs.append({"time": log_time_str, "content": content})
        elif isinstance(content, list):
            for text_item in content:
                self.logs.append({"time": log_time_str, "content": text_item})
        else:
            self.logs.append({
                "time": log_time_str,
                "content": f"LOG ERROR: Invalid content type '{type(content).__name__}' - {content}",
            })

    @staticmethod
    def _make_request(method: str, url: Union[str, bytes], **kwargs) -> Response:
        url_text = url.decode("utf-8") if isinstance(url, bytes) else str(url)
        request_url = _append_params(url_text, kwargs.get("params"))

        body, headers = _prepare_body_and_headers(
            data=kwargs.get("data"),
            json_payload=kwargs.get("json"),
            files=kwargs.get("files"),
            headers=kwargs.get("headers"),
            auth=kwargs.get("auth"),
            cookies=kwargs.get("cookies"),
        )

        request = _url_request.Request(
            url=request_url,
            data=body,
            headers=headers,
            method=method.upper(),
        )
        opener = _build_opener(kwargs.get("proxies"), kwargs.get("verify"), request_url)
        timeout = _normalize_timeout(kwargs.get("timeout"))

        try:
            raw_response = opener.open(request, timeout=timeout)
        except _url_error.HTTPError as exc:
            raw_response = exc
        except _url_error.URLError as exc:
            raise RequestException(str(exc.reason)) from exc
        except ValueError as exc:
            raise RequestException(str(exc)) from exc

        return Response(raw_response, preload_content=not kwargs.get("stream", False))

    def _handle_single_request(self, method: str, url: Union[str, bytes], **kwargs) -> Response:
        url_str = str(url)
        try:
            response = self._make_request(method, url, **kwargs)
            self._log(f"{FILE_PATH} Request.{method}() for {url_str} completed")
            return response
        except RequestException as exc:
            error_msg = f"ERROR: RequestException for {url_str}: {exc}"
            self._log(f"{FILE_PATH} Request.{method}() failed - {error_msg}")
            raise
        except Exception as exc:
            error_msg = f"CRITICAL ERROR: Unexpected exception for {url_str}: {exc}"
            self._log(f"{FILE_PATH} Request.{method}() failed - {error_msg}")
            raise

    def _handle_multiple_requests(self, method: str, urls: Tuple[Union[str, bytes], ...], **kwargs) -> Dict[str, Union[Response, str]]:
        result: Dict[str, Union[Response, str]] = {}
        for u_item in urls:
            url_str = str(u_item)
            try:
                response = self._make_request(method, u_item, **kwargs)
                response._status_error = not response.ok
                result[url_str] = response
            except RequestException as exc:
                error_msg = f"ERROR: RequestException for {url_str}: {exc}"
                self._log(f"{FILE_PATH} Request.{method}() failed - {error_msg}")
                result[url_str] = error_msg
            except Exception as exc:
                error_msg = f"CRITICAL ERROR: Unexpected exception for {url_str}: {exc}"
                self._log(f"{FILE_PATH} Request.{method}() failed - {error_msg}")
                result[url_str] = error_msg

        self._log(f"{FILE_PATH} Request.{method}() for multiple URLs completed")
        return result

    @staticmethod
    def _require_urls(method: str, urls: Tuple[Union[str, bytes], ...]) -> None:
        if not urls:
            raise ValueError(f"Request.{method}() requires at least one URL.")

    def get(
        self,
        *urls: Union[str, bytes],
        headers: Mapping[str, Union[str, bytes, None]] | None = None,
        timeout: Union[float, Tuple[float, float], Tuple[float, None], None] = None,
        proxies: MutableMapping[str, str] | None = None,
        stream: bool = False,
    ) -> Union[Response, Dict[str, Union[Response, str]]]:
        effective_timeout = timeout if timeout is not None else self._instance_timeout
        kwargs = {
            "headers": headers,
            "timeout": effective_timeout,
            "proxies": proxies,
            "stream": stream,
        }

        if len(urls) > 1:
            return self._handle_multiple_requests("get", urls, **kwargs)
        Request._require_urls("get", urls)
        return self._handle_single_request("get", urls[0], **kwargs)

    def post(
        self,
        *urls: Union[str, bytes],
        data: Optional[Union[str, bytes, Mapping[str, Any]]] = None,
        json: Optional[Mapping[str, Any]] = None,
        files: Optional[Union[Mapping[str, FileValue], Iterable[Tuple[str, FileValue]]]] = None,
        headers: Optional[Mapping[str, str]] = None,
        auth: Optional[Tuple[str, str]] = None,
        cookies: Optional[Union[Mapping[str, str], List[Tuple[str, str]]]] = None,
        proxies: Optional[Mapping[str, str]] = None,
        timeout: Union[int, float, None] = None,
        stream: bool = False,
    ) -> Union[Response, Dict[str, Union[Response, str]]]:
        effective_timeout = timeout if timeout is not None else self._instance_timeout
        kwargs = {
            "data": data,
            "json": json,
            "headers": headers,
            "auth": auth,
            "timeout": effective_timeout,
            "proxies": proxies,
            "cookies": cookies,
            "files": files,
            "stream": stream,
        }

        if len(urls) > 1:
            return self._handle_multiple_requests("post", urls, **kwargs)
        Request._require_urls("post", urls)
        return self._handle_single_request("post", urls[0], **kwargs)

    def delete(
        self,
        *urls: Union[str, bytes],
        headers: Optional[Mapping[str, str]] = None,
        timeout: Union[int, float, None] = None,
        proxies: Optional[Mapping[str, str]] = None,
    ) -> Union[Response, Dict[str, Union[Response, str]]]:
        effective_timeout = timeout if timeout is not None else self._instance_timeout
        kwargs = {
            "headers": headers,
            "timeout": effective_timeout,
            "proxies": proxies,
        }

        if len(urls) > 1:
            return self._handle_multiple_requests("delete", urls, **kwargs)
        Request._require_urls("delete", urls)
        return self._handle_single_request("delete", urls[0], **kwargs)

    def put(
        self,
        *urls: Union[str, bytes],
        data: Optional[Union[str, bytes, Mapping[str, Any]]] = None,
        json: Optional[Mapping[str, Any]] = None,
        files: Optional[Union[Mapping[str, FileValue], Iterable[Tuple[str, FileValue]]]] = None,
        headers: Optional[Mapping[str, str]] = None,
        proxies: Optional[Mapping[str, str]] = None,
        timeout: Union[int, float, None] = None,
        verify: Optional[Union[bool, str]] = None,
        stream: bool = False,
    ) -> Union[Response, Dict[str, Union[Response, str]]]:
        effective_timeout = timeout if timeout is not None else self._instance_timeout
        kwargs = {
            "data": data,
            "json": json,
            "headers": headers,
            "timeout": effective_timeout,
            "proxies": proxies,
            "files": files,
            "verify": verify,
            "stream": stream,
        }

        if len(urls) > 1:
            return self._handle_multiple_requests("put", urls, **kwargs)
        Request._require_urls("put", urls)
        return self._handle_single_request("put", urls[0], **kwargs)

    def request_sse(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"],
        url: str,
        params: Optional[dict] = None,
        data: Optional[Union[dict, str, bytes, BinaryIO]] = None,
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
        files: Optional[Dict[str, FileValue]] = None,
        timeout: Optional[float] = None,
    ) -> Iterable[Dict[str, str]]:
        sse_headers = dict(headers or {})
        sse_headers["Accept"] = "text/event-stream"

        response = self._make_request(
            method=method,
            url=url,
            params=params,
            data=data,
            json=json,
            headers=sse_headers,
            files=files,
            timeout=timeout if timeout is not None else self._instance_timeout,
            stream=True,
        )

        with response:
            response.raise_for_status()
            event = {"id": "", "event": "", "data": ""}

            def emit_event() -> Optional[Dict[str, str]]:
                if not event["data"]:
                    return None
                ready_event = {
                    "id": event["id"],
                    "event": event["event"],
                    "data": event["data"].rstrip("\n"),
                }
                event["id"] = ""
                event["event"] = ""
                event["data"] = ""
                return ready_event

            for raw_line in response.iter_lines(decode_unicode=True):
                line = raw_line.rstrip("\r\n")
                if line == "":
                    ready_event = emit_event()
                    if ready_event is None:
                        continue
                    yield ready_event
                    if self._enable_logging:
                        self._log(f"SSE Event: {ready_event}")
                    continue
                if line.startswith(":"):
                    continue
                if line.startswith("id:"):
                    event["id"] = line[3:].strip()
                elif line.startswith("event:"):
                    event["event"] = line[6:].strip()
                elif line.startswith("data:"):
                    event["data"] += line[5:].lstrip() + "\n"

            ready_event = emit_event()
            if ready_event is not None:
                yield ready_event
                if self._enable_logging:
                    self._log(f"SSE Event: {ready_event}")
