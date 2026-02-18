from typing import Literal, Dict, Set
from time import perf_counter, localtime, sleep


class Time:
    """
    A collection of utility functions and classes related to time measurement and formatting.
    This module centralizes high-precision timing mechanisms and system time utilities.
    """

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
            self._precision: Literal[1,2,3,4] = precision

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
            if not isinstance(value, int) or value not in [1, 2, 3, 4]:
                raise ValueError("Precision must be 1, 2, 3, or 4.")
            self._precision = value

        def passed(self) -> str:
            """
            Get the elapsed time since the _timer was started or last reset.

            Returns:
                Formatted string of elapsed time with specified precision (e.g., '1.23').

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
            Format a time component (year/month/day/hour/minute/second) based on the current system time.

            This is a utility method for consistent time formatting, primarily used by custom loggers.
            It returns a dictionary containing only the requested time parts.

            Args:
                time_part: Set of single-character literals indicating requested time parts
                           ("Y" for year, "M" for month, "D" for day, "h" for hour, "m" for minute, "s" for second).

            Returns:
                A dictionary mapping the requested time identifiers to their integer values.

            Example:
                >>> Time.f_time({"Y"})
                {'Y': 2026}
                >>> Time.f_time({"M","D"})
                {'M': 2, 'D': 4}
                >>> Time.f_time({"Y","D"})
                {'Y': 2026, 'D': 4}
            """
        _time = localtime()
        return_time: Dict[Literal["Y", "M", "D", "h", "m", "s"], int] = {}
        keys = {"Y": _time.tm_year, "M": _time.tm_mon, "D": _time.tm_mday,
                "h": _time.tm_hour, "m": _time.tm_min, "s": _time.tm_sec}

        for t in ["Y", "M", "D", "h", "m", "s"]:
            if t in time_part:
                return_time[t] = keys[t]
        return return_time