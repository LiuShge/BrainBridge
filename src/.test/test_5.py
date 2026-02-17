from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Dict, Literal, Union
import os
import time
from pynput import keyboard
from set_source_dir import _set_source_dir, _restore_sys_path
_set_source_dir()
from simple_import import change_sys_path
change_sys_path(to_runlib=True)
from mini_tools.timer import Time
_restore_sys_path()


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


KeyName = Literal[
    "BackSpace", "Tab", "Esc", "Enter",
    "up", "down", "left", "right",
    "w", "a", "s", "d"
]
ActionName = Literal["back", "continue", "decision"]
OptionItem = Dict[Literal["prompt", "output"], str]


def _clear_console() -> None:
    """
    Clear the console screen.

    Example:
    >>> _clear_console()
    """
    os.system("cls" if os.name == "nt" else "clear")


def _get_pynput_key(key_str: str) -> Union[keyboard.Key, keyboard.KeyCode]:
    """
    Convert a string representation of a key to a pynput keyboard object.

    :param key_str: Key name, such as "Enter", "Esc", "w".
    :return: A pynput Key or KeyCode.
    :raises ValueError: If key_str is unknown.
    Example:
    >>> _get_pynput_key("Enter") == keyboard.Key.enter
    True
    >>> _get_pynput_key("w") == keyboard.KeyCode.from_char("w")
    True
    """
    key_map: Dict[str, keyboard.Key] = {
        "BackSpace": keyboard.Key.backspace,
        "Tab": keyboard.Key.tab,
        "Esc": keyboard.Key.esc,
        "Enter": keyboard.Key.enter,
        "up": keyboard.Key.up,
        "down": keyboard.Key.down,
        "left": keyboard.Key.left,
        "right": keyboard.Key.right,
    }
    if key_str in key_map:
        return key_map[key_str]
    if len(key_str) == 1:
        return keyboard.KeyCode.from_char(key_str.lower())
    raise ValueError(f"Unknown key string: {key_str}")


def _safe_trim(text: str, max_len: int) -> str:
    """
    Trim text to max_len characters.

    :param text: Input text.
    :param max_len: Maximum length.
    :return: Trimmed text.
    Example:
    >>> _safe_trim("abcdef", 4)
    'abcd'
    """
    if max_len <= 0:
        return ""
    return text if len(text) <= max_len else text[:max_len - 1] + "…"


@dataclass(frozen=True)
class _PanelTheme:
    width: int = 84
    top: str = "╭"
    top_right: str = "╮"
    bottom: str = "╰"
    bottom_right: str = "╯"
    h: str = "─"
    v: str = "│"
    sep_left: str = "├"
    sep_right: str = "┤"
    pointer_left: str = "›"
    pointer_right: str = "‹"


class _DecisionPanel:
    def __init__(
        self,
        options: List[OptionItem],
        operation_tips: str,
        prompt_text: str,
        enter_key: Dict[ActionName, KeyName],
        theme: _PanelTheme | None = None,
        refresh_interval: float = 0.08,
    ):
        """
        Create a decision panel instance.

        :param options: Option items with "prompt" and "output".
        :param operation_tips: Tips text shown at bottom.
        :param prompt_text: Prompt text shown near decision hint.
        :param enter_key: Mapping for "back"/"continue"/"decision".
        :param theme: Panel theme configuration.
        :param refresh_interval: Main loop sleep interval.
        :return: None
        Example:
        >>> _opts = [{"prompt": "A", "output": "1"}]
        >>> _panel = _DecisionPanel(_opts, "tips", "Select", {"decision": "Enter", "back": "Esc", "continue": "Tab"})
        >>> isinstance(_panel, _DecisionPanel)
        True
        """
        self._options = options
        self._operation_tips = operation_tips
        self._prompt_text = prompt_text
        self._theme = theme or _PanelTheme()
        self._refresh_interval = float(refresh_interval)

        self._selected_index = 0
        self._running = True
        self._result: str | None = None

        self._key_pynput: Dict[ActionName, keyboard.Key | keyboard.KeyCode | None] = {}
        self._key_display: Dict[ActionName, str] = {}
        for action in ("back", "continue", "decision"):
            key_name = enter_key.get(action)
            if key_name is None:
                self._key_pynput[action] = None
                self._key_display[action] = "N/A"
                continue
            try:
                self._key_pynput[action] = _get_pynput_key(key_name)
                self._key_display[action] = key_name
            except ValueError:
                self._key_pynput[action] = None
                self._key_display[action] = "N/A"

    def run(self) -> str | None:
        """
        Run the interactive panel and return selection output.

        :return: Selected output string, or None if back/exit.
        Example:
        >>> _opts = [{"prompt": "A", "output": "1"}]
        >>> _panel = _DecisionPanel(_opts, "tips", "Select", {"decision": "Enter", "back": "Esc", "continue": "Tab"})
        >>> # _panel.run()  # interactive
        """
        if not self._options:
            _clear_console()
            return None

        self._draw()

        listener = keyboard.Listener(on_press=self._on_press)
        listener.start()

        while self._running:
            time.sleep(self._refresh_interval)

        listener.join()
        _clear_console()
        return self._result

    def _on_press(self, key: keyboard.Key | keyboard.KeyCode) -> bool:
        """
        Handle key press events.

        :param key: Pressed key object.
        :return: False to stop listener, True to continue.
        Example:
        >>> _opts = [{"prompt": "A", "output": "1"}]
        >>> _panel = _DecisionPanel(_opts, "tips", "Select", {"decision": "Enter", "back": "Esc", "continue": "Tab"})
        >>> isinstance(_panel._on_press(keyboard.Key.up), bool)
        True
        """
        if not self._options:
            self._result = None
            self._running = False
            return False

        n = len(self._options)

        def is_char(ch: str) -> bool:
            return hasattr(key, "char") and getattr(key, "char") and str(getattr(key, "char")).lower() == ch

        moved = False

        if key == keyboard.Key.up or key == keyboard.Key.left or is_char("w") or is_char("a"):
            self._selected_index = (self._selected_index - 1 + n) % n
            moved = True
        elif key == keyboard.Key.down or key == keyboard.Key.right or is_char("s") or is_char("d"):
            self._selected_index = (self._selected_index + 1) % n
            moved = True
        elif self._key_pynput.get("decision") is not None and key == self._key_pynput["decision"]:
            self._result = self._options[self._selected_index]["output"]
            self._running = False
            return False
        elif self._key_pynput.get("back") is not None and key == self._key_pynput["back"]:
            self._result = None
            self._running = False
            return False

        if moved:
            self._draw()

        return True

    def _draw(self) -> None:
        """
        Draw panel frame.

        :return: None
        Example:
        >>> _opts = [{"prompt": "A", "output": "1"}]
        >>> _panel = _DecisionPanel(_opts, "tips", "Select", {"decision": "Enter", "back": "Esc", "continue": "Tab"})
        >>> _panel._draw()
        """
        _clear_console()
        t = self._theme
        inner_w = max(10, t.width - 2)

        title = " Decision Panel "
        title = _safe_trim(title, inner_w)
        left_pad = (inner_w - len(title)) // 2
        right_pad = inner_w - len(title) - left_pad

        print(f"{t.top}{t.h * left_pad}{title}{t.h * right_pad}{t.top_right}")

        max_lines = max(6, len(self._options))
        for i in range(max_lines):
            if i < len(self._options):
                opt = self._options[i]
                idx = i + 1
                label = f"{idx:>2}. {opt['prompt']}"
                label = _safe_trim(label, inner_w - 4)
                if i == self._selected_index:
                    line = f" {t.pointer_left} {label:<{inner_w - 4}} {t.pointer_right} "
                else:
                    line = f"   {label:<{inner_w - 4}}   "
            else:
                line = " " * inner_w
            print(f"{t.v}{line:<{inner_w}}{t.v}")

        print(f"{t.sep_left}{t.h * inner_w}{t.sep_right}")

        decision_key = self._key_display.get("decision", "N/A")
        back_key = self._key_display.get("back", "N/A")
        hint_1 = _safe_trim(f"{self._prompt_text} (confirm: {decision_key})", inner_w)
        hint_2 = _safe_trim(f"back: {back_key}    {self._operation_tips}", inner_w)

        print(f"{t.v}{hint_1:<{inner_w}}{t.v}")
        print(f"{t.v}{hint_2:<{inner_w}}{t.v}")

        print(f"{t.bottom}{t.h * inner_w}{t.bottom_right}")


def decision_panel(
    *option_prompt: OptionItem,
    operation_tips: str,
    enter_key: Dict[ActionName, KeyName],
    prompt_text: str = "Make a selection",
    panel_width: int = 84,
) -> str | None:
    """
    Display an interactive decision panel in console.

    :param option_prompt: Options, each dict contains "prompt" and "output".
    :param operation_tips: Tips text shown at bottom.
    :param enter_key: Key mapping for actions.
    :param prompt_text: Prompt text shown near confirm hint.
    :param panel_width: Panel width in characters.
    :return: Selected output, or None if back.
    Example:
    >>> _opts = [{"prompt": "Open", "output": "open"}, {"prompt": "Exit", "output": "exit"}]
    >>> _keys = {"decision": "Enter", "back": "Esc", "continue": "Tab"}
    >>> # decision_panel(*_opts, operation_tips="Use arrows/WASD.", enter_key=_keys)
    """
    default_keys: Dict[ActionName, KeyName] = {"decision": "Enter", "back": "Esc", "continue": "Tab"}
    merged_keys: Dict[ActionName, KeyName] = {**default_keys, **enter_key}

    options = list(option_prompt)
    panel = _DecisionPanel(
        options=options,
        operation_tips=operation_tips,
        prompt_text=prompt_text,
        enter_key=merged_keys,
        theme=_PanelTheme(width=int(panel_width)),
    )
    return panel.run()


prompt = [
    {"prompt": "test", "output": "Nothing"},
    {"prompt": "test again", "output": "Nothing, too."},
]

selected = decision_panel(
    prompt[0],
    prompt[1],
    operation_tips="this is a test",
    enter_key={"decision": "Enter"},
    prompt_text="Choose one",
)
print(selected)
