from typing import Literal, Optional
from mini_tools.timer import Time

def display_loading_bar(
    _timer: Time,
    *content: str,
    duration: int = 6,
    speed: Literal["high", "mid", "low"] = "mid",
    method: Literal["promote", "replace", "back_replace"] = "replace",
    background: Optional[str] = None,
    size: int = 32,
    chunk_size: int = 3,
) -> None: ...
