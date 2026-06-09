"""Structured logging APIs for BrainBridge."""

from pathlib import Path

from .log_core import Logger, LogLevels


def log_to_file(
    text: str,
    *,
    level: LogLevels = LogLevels.INFO,
    context: str | None = None,
    file_path: str,
    display: bool = False,
    write_json: bool = False,
) -> None:
    """Create a log entry and append it to the target file."""
    target_path = Path(file_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.touch(exist_ok=True)

    Logger(level=level, text=text, context=context).output_log(
        to_file=True,
        display=display,
        file_path=str(target_path),
        write_json=write_json,
    )


__all__ = ["Logger", "LogLevels", "log_to_file"]
