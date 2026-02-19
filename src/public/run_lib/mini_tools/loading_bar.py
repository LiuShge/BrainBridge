from set_source_dir import _set_source_dir,_restore_sys_path
_set_source_dir()
from simple_import import change_sys_path
change_sys_path(to_runlib=True)
from mini_tools.timer import Time
_restore_sys_path()

from typing import Literal, Optional

def display_loading_bar(
        _timer: Time,
        *content: str,
        duration: int = 6,
        speed: Literal["high", "mid", "low"] = "mid",
        method: Literal["promote", "replace", "back_replace"] = "replace",
        background: Optional[str] = None,
        size: int = 32,
        chunk_size: int = 3,
):
    """
    Displays a customizable loading bar in the console.

    :param _timer: An instance of the Time class to control animation timing.
    :param content: Variable length argument list of strings to be used as the moving content of the loading bar.
    :param duration: The total duration for the loading bar animation in seconds.
    :param speed: The animation speed, affecting the update interval. Can be "high", "mid", or "low".
    :param method: The animation method. "promote" (a chunk slides across), "replace" (fills from left),
                   or "back_replace" (fills from left then scrolls content leftwards).
    :param background: Optional character/string to use for the background of the loading bar. Defaults to "░".
    :param size: The total length of the loading bar in characters.
    :param chunk_size: The size of the content chunk that moves or fills at each step.
    :return: None
    Example:
    >>> timer = Time()
    >>> display_loading_bar(timer, "=", ">", ".", duration=3, size=30, chunk_size=2, method="replace", speed="high")
        =>.=>.=>.=>.=>.=>.=>.=>.=>.=>.
    """
    speed_map = {"high": 0.1, "mid": 0.2, "low": 0.3}
    interval = speed_map.get(speed, 0.2)

    bg_char = background if background else "░"
    bg_pool = (bg_char * (size // len(bg_char) + 1))[:size]

    raw_content = "".join(content) if content else ">"
    content_pool = (raw_content * ((size + chunk_size + 10) // len(raw_content) + 2))

    total_steps = int(duration / interval)
    fill_steps = (size + chunk_size - 1) // chunk_size

    for i in range(total_steps + 1):
        cursor = i * chunk_size
        frame = ''
        if method == "replace":
            fill_len = min(cursor, size)
            frame = content_pool[:fill_len] + bg_pool[fill_len:]
            if i >= fill_steps:
                print(f"\r{content_pool[:size]}", end="", flush=True)
                break

        elif method == "promote":
            head = min(cursor, size)
            tail = max(0, cursor - chunk_size)
            train_segment = content_pool[tail:head]
            frame = bg_pool[:tail] + train_segment + bg_pool[head:]
            if tail >= size: break

        elif method == "back_replace":
            if cursor <= size:
                frame = content_pool[:cursor] + bg_pool[cursor:]
            else:
                start_idx = (cursor - size) % len(raw_content)
                frame = content_pool[start_idx: start_idx + size]

        print(f"\r{frame}", end="", flush=True)

        if i < total_steps:
            _timer.sleep(interval)

    print()