import json

import requests as _req
from typing import List, Dict, Literal, Optional, Union, Mapping, MutableMapping, Tuple, Iterable, Any, BinaryIO, \
    Set, IO
from time import localtime, perf_counter, sleep
import io

FILE_PATH = __file__

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
        Example:
        >>> req = Request(enable_logging=True, timeout=10)
        >>> print(len(req.logs))
        0
        >>> req.get("https://www.example.com")
        <Response [200]>
        >>> print(len(req.logs))
        1
        """
        self._enable_logging = enable_logging
        self._instance_timeout = timeout if timeout is not None else Request._class_default_timeout
        if self._enable_logging:
            self.logs: List[Dict[str, Union[List[str], str]]] = []

    def __len__(self) -> int:
        """
        get the length of logging
        :return: how much information was logged
        Example:
        >>> req = Request(enable_logging=True)
        >>> req.get("https://www.example.com")
        <Response [200]>
        >>> print(len(req))
        1
        """
        return len(self.logs) if self._enable_logging else 0

    def _log(self, content: Union[List[str], str]):
        """
        the logger
        :param content: content of logging
        :return: None, if not enable logging
        Example:
        >>> req = Request(enable_logging=True)
        >>> req._log("Test log message")
        >>> req._log(["Log entry 1", "Log entry 2"])
        >>> print(len(req.logs))
        3
        """
        if not self._enable_logging:
            return

        # 内联_get_current_time_parts以减少函数调用开销
        tn = localtime()
        log_time_str = f"{tn.tm_year}-{tn.tm_mon:02d}-{tn.tm_mday:02d} {tn.tm_hour:02d}:{tn.tm_min:02d}:{tn.tm_sec:02d}"

        if isinstance(content, str):
            self.logs.append({'time': log_time_str, 'content': content})
        elif isinstance(content, list):
            for text_item in content:
                self.logs.append({'time': log_time_str, 'content': text_item})
        else:
            self.logs.append({
                'time': log_time_str,
                'content': f"LOG ERROR: Invalid content type '{type(content).__name__}' - {content}"
            })

    @staticmethod
    def _make_request(method: str, url: Union[str, bytes], **kwargs) -> _req.models.Response:
        """
        get the result of request
        :param method: like "GET", "POST", "PUT", "DELETE" etc.
        :param url: just url~
        :param kwargs: args
        :return: the result of request
        Example:
        >>> req = Request()
        >>> response = req._make_request("get", "https://www.example.com", timeout=5)
        >>> print(response.status_code)
        200
        """
        request_func = getattr(_req, method)
        return request_func(url=url, **kwargs)

    def _handle_single_request(self, method: str, url: Union[str, bytes], **kwargs) -> _req.models.Response:
        """
        pack the _make_request
        :param method: like "GET", "POST", "PUT", "DELETE" etc.
        :param url: just url~
        :param kwargs: args
        :return: the result of one request
        Example:
        >>> req = Request(enable_logging=True)
        >>> _response = req._handle_single_request("get", "https://www.example.com")
        >>> print(_response.status_code)
        200
        """
        url_str = str(url)
        try:
            response = self._make_request(method, url, **kwargs)
            self._log(f"{FILE_PATH} Request.{method}() for {url_str} completed")
            return response
        except _req.exceptions.RequestException as e:
            error_msg = f"ERROR: RequestException for {url_str}: {e}"
            self._log(f"{FILE_PATH} Request.{method}() failed - {error_msg}")
            raise
        except Exception as e:
            error_msg = f"CRITICAL ERROR: Unexpected exception for {url_str}: {e}"
            self._log(f"{FILE_PATH} Request.{method}() failed - {error_msg}")
            raise

    def _handle_multiple_requests(self, method: str, urls: Tuple[Union[str, bytes], ...], **kwargs) -> Dict[
        str, Union[_req.models.Response, str]]:
        """
        pack the _make_request
        :param method: like "GET", "POST", "PUT", "DELETE" etc.
        :param urls: just many urls~
        :param kwargs: args
        :return: the result of many requests
        Example:
        >>> req = Request()
        >>> results = req._handle_multiple_requests("get", ("https://www.example.com", "https://www.github.com"))
        >>> print(results["https://www.example.com"])
        <Response [200]>
        >>> print("Error" in results["https://www.github.com"])
        False
        """
        result: Dict[str, Union[_req.models.Response, str]] = {}
        for u_item in urls:
            url_str = str(u_item)
            try:
                response = self._make_request(method, u_item, **kwargs)
                response._status_error = response.status_code != 200  # 添加标记
                result[url_str] = response
            except _req.exceptions.RequestException as e:
                error_msg = f"ERROR: RequestException for {url_str}: {e}"
                self._log(f"{FILE_PATH} Request.{method}() failed - {error_msg}")
                result[url_str] = error_msg
            except Exception as e:
                error_msg = f"CRITICAL ERROR: Unexpected exception for {url_str}: {e}"
                self._log(f"{FILE_PATH} Request.{method}() failed - {error_msg}")
                result[url_str] = error_msg

        self._log(f'{FILE_PATH} Request.{method}() for multiple URLs completed')
        return result

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

        Example:
        >>> _o=Request()
        >>> _x=_o.get("https://www.example.com")
        >>> print(_x.status_code)
        200
        >>> _x=_o.get('https://github.com','https://www.bing.com',timeout=6)
        >>> print(_x)
        {'https://github.com': <Response [200]>, 'https://www.bing.com': <Response [200]>}
        """
        effective_timeout = timeout if timeout is not None else self._instance_timeout
        kwargs = {
            'headers': headers,
            'timeout': effective_timeout,
            'proxies': proxies,
            'stream': stream
        }

        if len(urls) > 1:
            return self._handle_multiple_requests('get', urls, **kwargs)
        else:
            return self._handle_single_request('get', urls[0], **kwargs)

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

        Example:
        >>> req = Request()
        >>> response = req.post("https://httpbin.org/post", data={"key": "value"})
        >>> print(response.json()["form"])
        {'key': 'value'}

        # post with JSON data
        >>> response = req.post("https://httpbin.org/post", json={"key": "value"})
        >>> print(response.json()["json"])
        {'key': 'value'}

        # post file
        >>> _files = {'file': open('./Interface/openai_completion.py', 'rb')}
        >>> response = req.post("https://httpbin.org/post", files=_files)
        >>> print("files" in response.json())
        True

        # Batch requests
        >>> results = req.post("https://httpbin.org/post", "https://httpbin.org/post", json={"key": "value"})
        >>> print(len(results))
        1
        """
        effective_timeout = timeout if timeout is not None else self._instance_timeout
        kwargs = {
            'data': data,
            'json': json,
            'headers': headers,
            'auth': auth,
            'timeout': effective_timeout,
            'proxies': proxies,
            'cookies': cookies,
            'files': files,
            'stream': stream if stream is not None else False  # 确保 stream 是布尔值
        }

        if len(urls) > 1:
            return self._handle_multiple_requests('post', urls, **kwargs)
        else:
            return self._handle_single_request('post', urls[0], **kwargs)

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

        Example:
        >>> req = Request()
        >>> response = req.delete("https://httpbin.org/delete")
        >>> print(response.status_code)
        200

        # Batch delete resources
        >>> results = req.delete(
        ...     "https://httpbin.org/delete",
        ...     "https://httpbin.org/delete/another",
        ...     timeout=3
        ... )
        >>> print(len(results))
        2
        >>> print(results["https://httpbin.org/delete"])
        <Response [200]>
        """
        effective_timeout = timeout if timeout is not None else self._instance_timeout
        kwargs = {
            'headers': headers,
            'timeout': effective_timeout,
            'proxies': proxies,
        }

        if len(urls) > 1:
            return self._handle_multiple_requests('delete', urls, **kwargs)
        else:
            return self._handle_single_request('delete', urls[0], **kwargs)

    # ---------------------------------2026.2.3-------------------------------------
    #由gemini-2.5-flash整订
    #由qwen3-coder-480b-a35b-instruct重构

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

        Example:
        >>> req = Request()
        >>> response = req.put(
        ...     "https://httpbin.org/put",
        ...     data={"key": "updated_value"}
        ... )
        >>> print(response.json()["form"])
        {'key': 'updated_value'}

        # Update with JSON data
        >>> response = req.put(
        ...     "https://httpbin.org/put",
        ...     json={"name": "new_name", "status": "active"}
        ... )
        >>> print(response.json()["json"])
        {'name': 'new_name', 'status': 'active'}

        # Batch update
        >>> results = req.put(
        ...     "https://httpbin.org/put",
        ...     "https://httpbin.org/put/another",
        ...     json={"status": "updated"},
        ...     timeout=3
        ... )
        >>> print(len(results))
        2
        >>> print(results["https://httpbin.org/put"].status_code)
        200
        """
        effective_timeout = timeout if timeout is not None else self._instance_timeout
        kwargs = {
            'data': data,
            'json': json,
            'headers': headers,
            'timeout': effective_timeout,
            'proxies': proxies,
            'files': files,
            'verify': verify,
            'stream': stream
        }

        if len(urls) > 1:
            return self._handle_multiple_requests('put', urls, **kwargs)
        else:
            return self._handle_single_request('put', urls[0], **kwargs)

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
        if headers is None:
            headers = {}
        headers.update({"Accept": "text/event-stream"})
        kwargs = {
            "params": params,
            "headers": headers,
            "stream": True,
            "timeout": timeout or self._instance_timeout,
        }
        if json is not None:
            kwargs["json"] = json
        elif files is not None:
            kwargs["files"] = files
        elif data is not None:
            kwargs["data"] = data
        with _req.request(
                method=method.upper(),
                url=url,
                **kwargs
        ) as response:
            response.raise_for_status()
            buffer = ""

            for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                if chunk:
                    buffer += chunk
                    while "\n\n" in buffer:
                        event_str, buffer = buffer.split("\n\n", 1)
                        event = {"id": "", "event": "", "data": ""}
                        for line in event_str.split("\n"):
                            if line.startswith("id:"):
                                event["id"] = line[3:].strip()
                            elif line.startswith("event:"):
                                event["event"] = line[6:].strip()
                            elif line.startswith("data:"):
                                event["data"] += line[5:].strip() + "\n"
                        if event["data"]:
                            yield event
                            if self._enable_logging:
                                self._log(f"SSE Event: {event}")


class Time:

    sleep = sleep

    class Timer:
        """
            A high-precision _timer for measuring elapsed time with customizable decimal precision.

            This _timer uses `perf_counter()` for maximum accuracy and supports runtime precision adjustment.
            Ideal for benchmarking src execution time or timing operations in performance-sensitive applications.

            Key Features:
            - Microsecond-level precision via `perf_counter()`.
            - Configurable decimal places (1 to 4) for output formatting.
            - Reset functionality to restart timing.
            - String-formatted output for direct use in logs or UI.

            Constraints:
            - Precision is capped at 4 decimal places to avoid floating-point noise.
            - Not thread-safe (use separate instances in multi-threaded contexts).

            Example:
            >>> _timer = Time.Timer(precision=2)
            >>> Time.sleep(0.01)
            >>> _timer.passed()
            '0.01'
            >>> _timer.reset()
            >>> print(_timer.passed())
            0.00
            """

        def __init__(self, precision: Literal[1, 2, 3, 4]):
            """
            Initialize a Timer instance with specified precision.

            Args:
                precision: Number of decimal places for time reporting (1-4).
                          Higher precision may include floating-point artifacts.

            Raises:
                ValueError: If precision is not in [1, 2, 3, 4].

            Example:
            >>> _timer = Time.Timer(3)  # Initialize with 3 decimal places
            """
            if not isinstance(precision, int) or precision not in [1, 2, 3, 4]:
                raise ValueError("Precision must be 1, 2, 3, or 4.")

            self._start_time = perf_counter()
            self._precision = precision

        @property
        def precision(self) -> Literal[1, 2, 3, 4]:
            """
            Get the current decimal precision for time reporting.

            Returns:
                Current precision (1-4).

            Example:
            >>> _timer = Time.Timer(2)
            >>> print(_timer.precision)
            2
            """
            return self._precision

        @precision.setter
        def precision(self, value: Literal[1, 2, 3, 4]):
            """
            Set the decimal precision for time reporting.

            Args:
                value: New precision (1-4).

            Raises:
                ValueError: If value is not in [1, 2, 3, 4].

            Example:
            >>> _timer = Time.Timer(2)
            >>> _timer.precision = 4
            """
            # 运行时验证 precision
            if not isinstance(value, int) or value not in [1, 2, 3, 4]:
                raise ValueError(f"{FILE_PATH} Time.Timer.precision.setter() failed error - Precision must be 1, 2, 3, or 4.")
            self._precision = value

        def passed(self) -> str:
            """
            Get the elapsed time since the _timer was started or last reset.

            Returns:
                Formatted string of elapsed time with specified precision (e.g., '1.23').
                Avoids scientific notation and trailing zeros after decimal.

            Example:
            >>> _timer = Time.Timer(3)
            >>> Time.sleep(0.0025)
            >>> _timer.passed()
            '0.005'
            """
            elapsed_time = perf_counter() - self._start_time
            return f"{elapsed_time:.{self._precision}f}"

        def reset(self):
            """
            Reset the _timer's start time to the current moment.

            Example:
            >>> _timer = Time.Timer(2)
            >>> Time.sleep(0.1)
            >>> _timer.reset()
            >>> print(_timer.passed())
            0.00
            """
            self._start_time = perf_counter()

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

            Example:
                >>> Time.f_time({"Y"})
                {'Y': 2026}
                >>> Time.f_time({"M","D"})
                {'M': 2, 'D': 4}
                >>> Time.f_time({"Y","D"})
                {'Y': 2026, 'D': 4}
            """
        _time = localtime()
        return_time = {}
        keys = {"Y": _time.tm_year, "M": _time.tm_mon, "D": _time.tm_mday,
                "h": _time.tm_hour, "m": _time.tm_min, "s": _time.tm_sec}
        had_keys = list(time_part)
        for t in ["Y", "M", "D", "h", "m", "s"]:
            if t in had_keys:
                return_time[t] = keys[t]
        return return_time
# ---------------------------------2026.2.4-------------------------------------
# Initially completed
