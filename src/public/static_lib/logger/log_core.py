from set_source_dir import _set_source_dir,_restore_sys_path
from sys import path as sys_path
_set_source_dir()
print(sys_path)
from simple_import import change_sys_path, restore_sys_path

change_sys_path(to_runlib=True)
from mini_tools.timer import Time
from files_manager.manager import write_content_tofile

restore_sys_path()
_restore_sys_path()
import json
from typing import TypedDict, Literal, List, Dict, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass


class LogLevels(Enum):
    """
    Enumeration of logging severity levels.
    """
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogPart(Enum):
    """
    Enumeration of components that can be included in a log entry.
    """
    TIME = "TIME"
    LEVEL = "LEVEL"
    TEXT = "TEXT"
    CONTEXT = "CONTEXT"


class LogFormat(TypedDict):
    """
    TypedDict defining the structure and ordering of log parts.
    """
    First: Optional[LogPart]
    Second: Optional[LogPart]
    Third: Optional[LogPart]
    Fourth: Optional[LogPart]


@dataclass(init=True, repr=True)
class LogInformation:
    """
    A data container for log-related information.
    :param time: An instance of Time for timestamping.
    :param level: Severity level of the log.
    :param text: Main message content (string or list of strings).
    :param context: Additional context or metadata.
    """
    time: Optional[Time]
    level: Optional[LogLevels]
    text: Union[str, List[str], None]
    context: Union[str, List[str], None] = None


class _Logger:
    """
    Internal base class providing static methods for constructing log structures.
    """

    @staticmethod
    def _json_log_builder(time: Optional[Time],
                          level: Optional[LogLevels],
                          text: Union[str, List[str], None],
                          context: Union[str, List[str], None] = None,
                          information: Optional[LogInformation] = None,
                          log_format: Optional[LogFormat] = None) -> str:
        """
        Builds a JSON string representation of the log entry.
        :param time: Time object for timestamp.
        :param level: Logging level.
        :param text: Log message content.
        :param context: Extra context.
        :param information: (Optional) LogInformation object containing data.
        :param log_format: (Optional) Custom ordering of log parts.
        :return: A JSON formatted string.
        Example:
        >>> log_json = _Logger._json_log_builder(None, LogLevels.INFO, "System started")
        >>> '"LEVEL": "INFO"' in log_json
        True
        """
        _log_data = _Logger._dict_log_builder(time, level, text, context, information, log_format)
        try:
            return json.dumps(_log_data, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Serialization failed: {e}") from e

    # noinspection PyTypedDict
    @staticmethod
    def _dict_log_builder(time: Optional[Time],
                          level: Optional[LogLevels],
                          text: Union[str, List[str], None],
                          context: Union[str, List[str], None] = None,
                          information: Optional[LogInformation] = None,
                          log_format: Optional[LogFormat] = None) -> Dict[str, Any]:
        """
        Constructs a dictionary containing log details based on specified format.
        :param time: Time object for timestamp.
        :param level: Logging level.
        :param text: Log message content.
        :param context: Extra context.
        :param information: (Optional) Pre-packaged LogInformation object.
        :param log_format: (Optional) Desired order of output parts.
        :return: A dictionary representing the log entry.
        Example:
        >>> data = _Logger._dict_log_builder(None, LogLevels.ERROR, "Crash")
        >>> data.get("LEVEL")
        'ERROR'
        """
        if information:
            time = information.time or time
            level = information.level or level
            text = information.text or text
            context = information.context or context

        if log_format is None:
            log_format = LogFormat(
                First=LogPart.TIME if time else None,
                Second=LogPart.LEVEL if level else None,
                Third=LogPart.TEXT if text else None,
                Fourth=LogPart.CONTEXT if context else None
            )

        _log_data = {}
        _slots: List[Literal["First", "Second", "Third", "Fourth"]] = ["First", "Second", "Third", "Fourth"]

        for _slot in _slots:
            _slot: str
            part = log_format.get(_slot)
            if not part:
                continue

            if part == LogPart.TIME and time:
                _t = time.f_time({"Y", "M", "D", "h", "m", "s"})
                _log_data["TIME"] = f"{_t['Y']}.{_t['M']:02d}.{_t['D']:02d}-{_t['h']:02d}:{_t['m']:02d}:{_t['s']:02d}"
            elif part == LogPart.LEVEL and level:
                _log_data["LEVEL"] = level.value
            elif part == LogPart.TEXT and text is not None:
                _log_data["TEXT"] = text
            elif part == LogPart.CONTEXT and context is not None:
                _log_data["CONTEXT"] = context

        return _log_data


class Logger(_Logger):
    """
    Main interface for logging operations, supporting JSON and formatted text outputs.
    """

    def __init__(self,
                 time: Optional[Time] = None,
                 level: Optional[LogLevels] = None,
                 text: Union[str, List[str], None] = None,
                 context: Union[str, List[str], None] = None,
                 information: Optional[LogInformation] = None,
                 log_format: Optional[LogFormat] = None):
        """
        Initialize the Logger instance.
        :param time: Time object for tracking when the log occurred.
        :param level: Severity of the log entry.
        :param text: Content of the log message.
        :param context: Additional execution context.
        :param information: (Optional) Pre-defined LogInformation object.
        :param log_format: (Optional) Formatting template for parts.
        Example:
        >>> logger = Logger(level=LogLevels.DEBUG, text="Init test")
        >>> isinstance(logger.text_log_builder(), dict)
        True
        """
        self.time = time
        self.level = level
        self.text = text
        self.context = context
        self.information = information
        self.log_format = log_format

    def json_log_builder(self) -> str:
        """
        Generate a JSON string from instance properties.
        :return: JSON string.
        """
        return _Logger._json_log_builder(self.time, self.level, self.text, self.context, self.information,
                                         self.log_format)

    def text_log_builder(self) -> Dict[str, Any]:
        """
        Generate a dictionary structure from instance properties.
        :return: Dictionary of log data.
        """
        return _Logger._dict_log_builder(self.time, self.level, self.text, self.context, self.information,
                                         self.log_format)

    def output_log(self, to_file: bool, display: bool, file_path: Optional[str] = None,
                   write_json: bool = True) -> None:
        """
        Distribute the log to a file and/or the standard output.
        :param to_file: If True, writes the log to the specified path.
        :param display: If True, prints the log to the console.
        :param file_path: Path to the target log file.
        :param write_json: If True and using non-jsonl files, enforces JSON format check.
        :return: None
        Example:
        >>> logger = Logger(level=LogLevels.INFO, text="Console Test")
        >>> logger.output_log(to_file=False, display=True)
        {'LEVEL': 'INFO', 'TEXT': 'Console Test'}
        """
        if to_file:
            if not file_path:
                raise ValueError("file_path must be provided if to_file is True.")

            if file_path.endswith(".jsonl"):
                write_content_tofile(file_path, self.json_log_builder(), "utf-8", override=False)
            else:
                if write_json:
                    raise ValueError(
                        f"File type warning: {file_path} is not a .jsonl file. Set write_json=False to override.")
                write_content_tofile(file_path, str(self.text_log_builder()).replace('\n', '  '), "utf-8",
                                     override=False)

        if display:
            print(self.text_log_builder())
