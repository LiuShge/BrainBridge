from time import perf_counter
from typing import Literal, Dict, Set


class Time:
    """
    A collection of utility functions and classes related to time measurement and formatting.
    This module centralizes high-precision timing mechanisms and system time utilities.
    """

    sleep = sleep

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

        Example:
        >>> timer = Time.Timer(precision=2)
        >>> Time.sleep(0.01)
        >>> timer.passed()
        '0.01'
        >>> timer.reset()
        >>> print(timer.passed())
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
            >>> timer = Time.Timer(3)  # Initialize with 3 decimal places
            """
            self._start_time = perf_counter()
            self._precision = precision

        @property
        def precision(self) -> Literal[1, 2, 3, 4]:
            """
            Get the current decimal precision for time reporting.

            Returns:
                Current precision (1-4).

            Example:
            >>> timer = Time.Timer(2)
            >>> print(timer.precision)
            2
            """
            ...

        @precision.setter
        def precision(self, value: Literal[1, 2, 3, 4]):
            """
            Set the decimal precision for time reporting.

            Args:
                value: New precision (1-4).

            Raises:
                ValueError: If value is not in [1, 2, 3, 4].

            Example:
            >>> timer = Time.Timer(2)
            >>> timer.precision = 4
            """
            ...

        def passed(self) -> str:
            """
            Get the elapsed time since the timer was started or last reset.

            Returns:
                Formatted string of elapsed time with specified precision (e.g., '1.23').

            Example:
            >>> timer = Time.Timer(3)
            >>> Time.sleep(0.0025)
            >>> timer.passed()
            '0.005'
            """
            ...

        def reset(self):
            """
            Reset the timer's start time to the current moment.

            Example:
            >>> timer = Time.Timer(2)
            >>> Time.sleep(0.1)
            >>> timer.reset()
            >>> print(timer.passed())
            0.00
            """
            ...

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
        ...