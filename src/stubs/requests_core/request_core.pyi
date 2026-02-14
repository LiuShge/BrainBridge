from typing import List, Dict, Literal, Optional, Union, Mapping, MutableMapping, Tuple, Iterable, Any, BinaryIO, \
    Set, IO
import io
import requests as _req

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

class Request:
    _class_default_timeout = 5

    def __init__(self, enable_logging: bool = False, timeout: Union[int, float, None] = None):
        """
        :param enable_logging: turn "logging" function off or on
        :param timeout: control the value of timeout
        """
        pass

    def __len__(self) -> int:
        """
        get the length of logging
        :return: how much information was logged
        """
        pass

    def _log(self, content: Union[List[str], str]):
        """
        the logger
        :param content: content of logging
        :return: None, if not enable logging
        """
        pass

    @staticmethod
    def _make_request(method: str, url: Union[str, bytes], **kwargs) -> _req.models.Response:
        """
        get the result of request
        :param method: like "GET", "POST", "PUT", "DELETE" etc.
        :param url: just url~
        :param kwargs: args
        :return: the result of request
        """
        pass

    def _handle_single_request(self, method: str, url: Union[str, bytes], **kwargs) -> _req.models.Response:
        """
        pack the _make_request
        :param method: like "GET", "POST", "PUT", "DELETE" etc.
        :param url: just url~
        :param kwargs: args
        :return: the result of one request
        """
        pass

    def _handle_multiple_requests(self, method: str, urls: Tuple[Union[str, bytes], ...], **kwargs) -> Dict[
        str, Union[_req.models.Response, str]]:
        """
        pack the _make_request
        :param method: like "GET", "POST", "PUT", "DELETE" etc.
        :param urls: just many urls~
        :param kwargs: args
        :return: the result of many requests
        """
        pass


    def get(self,
            *urls: Union[str, bytes],
            headers: Mapping[str, Union[str, bytes, None]] | None = None,
            timeout: Union[float, Tuple[float, float], Tuple[float, None], None] = None,
            proxies: MutableMapping[str, str] | None = None,
            stream: bool = False) -> Union[_req.models.Response, Dict[str, Union[_req.models.Response, str]]]:
        """
        powered by "_handle_single_request" and "_handle_multiple_requests"
        :param urls: URL(s) to send GET request(s). Can be single string/bytes or multiple arguments.
        :param headers: (Optional) Dictionary of HTTP headers to send with the request.
        :param timeout: (Optional) Override instance/class timeout value (in seconds). Can be int/float/None.
        :param proxies: (Optional) Dictionary mapping protocol to proxy URL (e.g., {'http': 'http://proxy:8080'}).
        :param stream: (Optional) If True, response content will not be immediately downloaded (default: False).

        Returns:
            - Single URL: <requests.models.Response> object if successful, Exception if failed
            - Multiple URLs: Dict[str, Union[Response, str]] where str is error message if exception occurred
        """
        pass

    def post(self,
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
             stream: bool = False,  # 明确默认值为 False
             ) -> Union[_req.models.Response, Dict[str, Union[_req.models.Response, str]]]:
        """
        powered by "_handle_single_request" and "_handle_multiple_requests"
        :param urls: One or more URLs (string or bytes) to send the POST request(s).
                     Multiple URLs will trigger batch processing.
        :param data: (Optional) Dictionary, bytes, or string to send in the request body.
                     Typically used for form-encoded data.
        :param json: (Optional) JSON-serializable dictionary to send in the request body.
                     Automatically sets `Content-Type: application/json`.
        :param files: (Optional) Dictionary or iterable of file tuples for multipart uploads.
                     Format: `{'fieldname': FileValue}` or `[('fieldname', FileValue)]`.
                     See `FileValue` type for details on supported file formats.
        :param headers: (Optional) Dictionary of HTTP headers to include in the request.
        :param auth: (Optional) Tuple of `(username, password)` for HTTP Basic Authentication.
        :param cookies: (Optional) Dictionary or list of tuples for request cookies.
        :param proxies: (Optional) Dictionary mapping protocol to proxy URL (e.g., `{'http': 'http://proxy:8080'}`).
        :param timeout: (Optional) Override instance/class timeout value (in seconds).
                        Can be `int`, `float`, or `None` (uses default).
        :param stream: (Optional) If `True`, response content will be streamed (default: `False`).
        :return:
            - **Single URL**: `_req.models.Response` object on success.
              Raises `requests.exceptions.RequestException` or other `Exception` on failure.
            - **Multiple URLs**: `Dict[str, Union[_req.models.Response, str]]` where:
              - Key: URL string.
              - Value: Response object (success) or error message string (failure).
        """
        pass

    def delete(self,
               *urls: Union[str, bytes],
               headers: Optional[Mapping[str, str]] = None,
               timeout: Union[int, float, None] = None,
               proxies: Optional[Mapping[str, str]] = None,
               ) -> Union[_req.models.Response, Dict[str, Union[_req.models.Response, str]]]:
        """
        powered by "_handle_single_request" and "_handle_multiple_requests".
        Sends HTTP DELETE request(s) to the specified URL(s) to delete resources.

        :param urls: One or more URLs (string or bytes) to send the DELETE request(s).
                     Multiple URLs will trigger batch processing.
        :param headers: (Optional) Dictionary of HTTP headers to include in the request.
        :param timeout: (Optional) Override instance/class timeout value (in seconds).
                        Can be `int`, `float`, or `None` (uses default timeout).
        :param proxies: (Optional) Dictionary mapping protocol to proxy URL
                        (e.g., `{'http': 'http://proxy:8080'}`).
        :return:
            - **Single URL**: `_req.models.Response` object on success.
              Raises `requests.exceptions.RequestException` or other `Exception` on failure.
            - **Multiple URLs**: `Dict[str, Union[_req.models.Response, str]]` where:
              - Key: URL string.
              - Value: Response object (success) or error message string (failure).
        """
        pass

    _c_put = _req.put

    def put(self,
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
            stream: bool = False,
            ) -> Union[_req.models.Response, Dict[str, Union[_req.models.Response, str]]]:
        """
        Powered by "_handle_single_request" and "_handle_multiple_requests".
        Sends HTTP PUT request(s) to the specified URL(s) to update or create resources.

        :param urls: One or more URLs (string or bytes) to send the PUT request(s).
                     Multiple URLs will trigger batch processing.
        :param data: (Optional) Dictionary, bytes, or string to send in the request body.
                     Typically used for form-encoded data or raw payloads.
        :param json: (Optional) JSON-serializable dictionary to send in the request body.
                     Automatically sets `Content-Type: application/json`.
        :param files: (Optional) Dictionary or iterable of file tuples for multipart uploads.
                     Format: `{'fieldname': FileValue}` or `[('fieldname', FileValue)]`.
                     Note: PUT requests with files are less common but supported.
                     See `FileValue` type for details on supported file formats.
        :param headers: (Optional) Dictionary of HTTP headers to include in the request.
        :param proxies: (Optional) Dictionary mapping protocol to proxy URL
                        (e.g., `{'http': 'http://proxy:8080'}`).
        :param timeout: (Optional) Override instance/class timeout value (in seconds).
                        Can be `int`, `float`, or `None` (uses default timeout).
        :param verify: (Optional) Controls SSL certificate verification.
                      `True` (default): Verify certificates.
                      `False`: Skip verification (insecure).
                      String path: Path to CA_BUNDLE file or directory.
        :param stream: (Optional) If `True`, response content will be streamed (default: `False`).
        :return:
            - **Single URL**: `_req.models.Response` object on success.
              Raises `requests.exceptions.RequestException` or other `Exception` on failure.
            - **Multiple URLs**: `Dict[str, Union[_req.models.Response, str]]` where:
              - Key: URL string.
              - Value: Response object (success) or error message string (failure).
        """
        pass

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
        """
        Initiate an SSE request and return an event iterator (supports methods like GET/POST/PUT, etc.).

        :param method: HTTP method, such as "GET", "POST", "PUT", etc.
        :param url: SSE endpoint URL.
        :param params: Query parameters (for GET requests).
        :param data: Request body (for POST/PUT requests, can be a dict/string/bytes/file-like object).
        :param json: Request body in JSON format (automatically sets Content-Type).
        :param headers: Request headers.
        :param files: File uploads (dict with field name as key and `FileValue` type as value).
        :param timeout: Timeout duration (overrides the default instance value).
        :return: Iterator of event dictionaries in the format: {"id": str, "event": str, "data": str}.
        """
        pass

class Time:

    class Timer:
        """
            A high-precision timer for measuring elapsed time with customizable decimal precision.

            This timer uses `perf_counter()` for maximum accuracy and supports runtime precision adjustment.
            Ideal for benchmarking src execution time or timing operations in performance-sensitive applications.

            Key Features:
            - Microsecond-level precision via `perf_counter()`.
            - Configurable decimal places (1 to 4) for output formatting.
            - Reset functionality to restart timing.
            - String-formatted output for direct use in logs or UI.

            Constraints:
            - Precision is capped at 4 decimal places to avoid floating-point noise.
            - Not thread-safe (use separate instances in multi-threaded contexts).
            """

        def __init__(self, precision: Literal[1, 2, 3, 4]):
            """
            Initialize a Timer instance with specified precision.

            Args:
                precision: Number of decimal places for time reporting (1-4).
                          Higher precision may include floating-point artifacts.

            Raises:
                ValueError: If precision is not in [1, 2, 3, 4].
            """
            pass

        @property
        def precision(self) -> Literal[1, 2, 3, 4]:
            """
            Get the current decimal precision for time reporting.

            Returns:
                Current precision (1-4).
            """
            pass

        @precision.setter
        def precision(self, value: Literal[1, 2, 3, 4]):
            """
            Set the decimal precision for time reporting.

            Args:
                value: New precision (1-4).
            """
            pass

        def passed(self) -> str:
            """
            Get the elapsed time since the timer was started or last reset.

            Returns:
                Formatted string of elapsed time with specified precision (e.g., '1.23').
                Avoids scientific notation and trailing zeros after decimal.
            """
            pass

        def reset(self):
            """
            Reset the timer's start time to the current moment.
            """
            pass

    @staticmethod
    def f_time(time_part: Set[Literal["Y", "M", "D", "h", "m", "s"]]) -> Dict[
        Literal["Y", "M", "D", "h", "m", "s"], int]:
        """
            Format a time component (year/month/day/hour/minute/second) as a fixed-width string.

            This is a utility method for consistent time formatting, primarily used by `Time.get_current_time()`.
            Automatically pads single-digit values with leading zeros to maintain uniform length.

            Args:
                time_part: Integer time component (e.g., `1` for January or `5` for 5 AM).

            Returns:
                Formatted string (e.g., `"5"` → `"05"` if `length=2`).

            Raises:
                ValueError: If `length` is not 1 or 2, or if `time_part` cannot fit in specified length
                           (e.g., `time_part=100` with `length=2`).
        """
        pass
