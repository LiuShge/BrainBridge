from typing import List, Dict, Literal, Optional, Union, Mapping, MutableMapping, Tuple, Iterable, Any, BinaryIO, IO
import io

FileContent = Union[
        bytes,
        str,
        BinaryIO,
        io.BytesIO,
        IO[bytes]
    ]
FileValue = Union[
        FileContent,
        Tuple[Optional[str], FileContent],
        Tuple[Optional[str], FileContent, str],
        Tuple[Optional[str], FileContent, str, Mapping[str, str]],
    ]

class RequestException(RuntimeError): ...

class Response:
    status_code: int
    reason: str
    url: str
    headers: Dict[str, str]
    _status_error: bool

    @property
    def ok(self) -> bool: ...

    @property
    def content(self) -> bytes: ...

    @property
    def text(self) -> str: ...

    def json(self) -> Any: ...
    def raise_for_status(self) -> None: ...
    def iter_content(self, chunk_size: Optional[int] = None, decode_unicode: bool = False) -> Iterable[Union[bytes, str]]: ...
    def close(self) -> None: ...
    def __enter__(self) -> "Response": ...
    def __exit__(self, exc_type, exc, tb) -> None: ...

class Request:
    _class_default_timeout = 5

    def __init__(self, enable_logging: bool = False, timeout: Union[int, float, None] = None): ...
    def __len__(self) -> int: ...
    def _log(self, content: Union[List[str], str]) -> None: ...

    @staticmethod
    def _make_request(method: str, url: Union[str, bytes], **kwargs) -> Response: ...

    def _handle_single_request(self, method: str, url: Union[str, bytes], **kwargs) -> Response: ...
    def _handle_multiple_requests(self, method: str, urls: Tuple[Union[str, bytes], ...], **kwargs) -> Dict[str, Union[Response, str]]: ...

    def get(
            self,
            *urls: Union[str, bytes],
            headers: Mapping[str, Union[str, bytes, None]] | None = None,
            timeout: Union[float, Tuple[float, float], Tuple[float, None], None] = None,
            proxies: MutableMapping[str, str] | None = None,
            stream: bool = False) -> Union[Response, Dict[str, Union[Response, str]]]: ...

    def post(
             self,
             *urls: Union[str, bytes],
             data: Optional[Union[str, bytes, Mapping[str, Any]]] = None,
             json: Optional[Mapping[str, Any]] = None,
             files: Optional[Union[
                 Mapping[str, FileValue],
                 Iterable[Tuple[str, FileValue]]
             ]] = None,
             headers: Optional[Mapping[str, str]] = None,
             auth: Optional[Tuple[str, str]] = None,
             cookies: Optional[Union[Mapping[str, str], List[Tuple[str, str]]]] = None,
             proxies: Optional[Mapping[str, str]] = None,
             timeout: Union[int, float, None] = None,
             stream: bool = False) -> Union[Response, Dict[str, Union[Response, str]]]: ...

    def delete(
               self,
               *urls: Union[str, bytes],
               headers: Optional[Mapping[str, str]] = None,
               timeout: Union[int, float, None] = None,
               proxies: Optional[Mapping[str, str]] = None) -> Union[Response, Dict[str, Union[Response, str]]]: ...

    def put(
            self,
            *urls: Union[str, bytes],
            data: Optional[Union[str, bytes, Mapping[str, Any]]] = None,
            json: Optional[Mapping[str, Any]] = None,
            files: Optional[Union[
                Mapping[str, FileValue],
                Iterable[Tuple[str, FileValue]]
            ]] = None,
            headers: Optional[Mapping[str, str]] = None,
            proxies: Optional[Mapping[str, str]] = None,
            timeout: Union[int, float, None] = None,
            verify: Optional[Union[bool, str]] = None,
            stream: bool = False) -> Union[Response, Dict[str, Union[Response, str]]]: ...

    def request_sse(
            self,
            method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"],
            url: str,
            params: Optional[dict] = None,
            data: Optional[Union[dict, str, bytes, BinaryIO]] = None,
            json: Optional[dict] = None,
            headers: Optional[dict] = None,
            files: Optional[Dict[str, FileValue]] = None,
            timeout: Optional[float] = None) -> Iterable[Dict[str, str]]: ...
