from typing import TypedDict, Literal, List, Dict, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass
from src.public.run_lib.mini_tools.timer import Time


class LogLevels(Enum):
    """Enumeration of logging severity levels."""
    DEBUG: str
    INFO: str
    WARNING: str
    ERROR: str
    CRITICAL: str


class LogPart(Enum):
    """Enumeration of components that can be included in a log entry."""
    TIME: str
    LEVEL: str
    TEXT: str
    CONTEXT: str


class LogFormat(TypedDict, total=False):
    """TypedDict defining the structure and ordering of log parts."""
    First: Optional[LogPart]
    Second: Optional[LogPart]
    Third: Optional[LogPart]
    Fourth: Optional[LogPart]


@dataclass
class LogInformation:
    """
    A data container for log-related information.
    """
    time: Optional[Time]
    level: Optional[LogLevels]
    text: Union[str, List[str], None]
    context: Union[str, List[str], None]

    def __init__(
            self,
            time: Optional[Time],
            level: Optional[LogLevels],
            text: Union[str, List[str], None],
            context: Union[str, List[str], None] = ...
    ) -> None: ...


class LogStructure(TypedDict):
    """Type definition representing the schema of a generated log entry."""
    TIME: Optional[str]
    LEVEL: Optional[str]
    TEXT: Optional[Union[str, List[str]]]
    CONTEXT: Optional[Union[str, List[str]]]


class _Logger:
    """Internal base class providing static methods for constructing log structures."""

    @staticmethod
    def _json_log_builder(
            time: Optional[Time],
            level: Optional[LogLevels],
            text: Union[str, List[str], None],
            context: Union[str, List[str], None] = ...,
            information: Optional[LogInformation] = ...,
            log_format: Optional[LogFormat] = ...
    ) -> str: ...

    @staticmethod
    def _dict_log_builder(
            time: Optional[Time],
            level: Optional[LogLevels],
            text: Union[str, List[str], None],
            context: Union[str, List[str], None] = ...,
            information: Optional[LogInformation] = ...,
            log_format: Optional[LogFormat] = ...
    ) -> Dict[str, Any]: ...


class Logger(_Logger):
    """Main interface for logging operations, supporting JSON and formatted text outputs."""
    time: Optional[Time]
    level: Optional[LogLevels]
    text: Union[str, List[str], None]
    context: Union[str, List[str], None]
    information: Optional[LogInformation]
    log_format: Optional[LogFormat]

    def __init__(
            self,
            time: Optional[Time] = ...,
            level: Optional[LogLevels] = ...,
            text: Union[str, List[str], None] = ...,
            context: Union[str, List[str], None] = ...,
            information: Optional[LogInformation] = ...,
            log_format: Optional[LogFormat] = ...
    ) -> None: ...

    def json_log_builder(self) -> str: ...

    def text_log_builder(self) -> Dict[str, Any]: ...

    def output_log(
            self,
            to_file: bool,
            display: bool,
            file_path: Optional[str] = ...,
            write_json: bool = ...
    ) -> None: ...
