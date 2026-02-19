from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Union, Iterable
import os
import time
import shutil
import unicodedata

from pynput import keyboard


ActionName = Literal["back", "continue", "decision"]
KeyName = Literal[
    "BackSpace", "Tab", "Esc", "Enter",
    "up", "down", "left", "right",
    "w", "a", "s", "d"
]
OptionItem = Dict[Literal["prompt", "output"], str]


def _get_pynput_key(key_str: str) -> Union[keyboard.Key, keyboard.KeyCode]:
    """
    Convert key name to pynput keyboard object.

    :param key_str: Key name, such as "Enter", "Esc", "w".
    :return: pynput Key or KeyCode.
    :raises ValueError: If unknown.
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


def _display_width(text: str) -> int:
    """
    Compute approximate terminal display width.

    :param text: Input text.
    :return: Display width.
    Example:
    >>> _display_width("abc")
    3
    """
    w = 0
    for ch in text:
        if unicodedata.combining(ch):
            continue
        east = unicodedata.east_asian_width(ch)
        w += 2 if east in ("W", "F") else 1
    return w


def _trim_to_width(text: str, max_width: int) -> str:
    """
    Trim text to fit into max_width (terminal columns).

    :param text: Input text.
    :param max_width: Max display width.
    :return: Trimmed text.
    Example:
    >>> _trim_to_width("abcdef", 4)
    'abcd'
    """
    if max_width <= 0:
        return ""
    cur = 0
    out: List[str] = []
    for ch in text:
        if unicodedata.combining(ch):
            out.append(ch)
            continue
        inc = 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
        if cur + inc > max_width:
            break
        out.append(ch)
        cur += inc
    return "".join(out)


def _pad_to_width(text: str, width: int) -> str:
    """
    Pad text with spaces to match exact display width.

    :param text: Input text.
    :param width: Target display width.
    :return: Padded text.
    Example:
    >>> _display_width(_pad_to_width("a", 3))
    3
    """
    trimmed = _trim_to_width(text, width)
    pad = max(0, width - _display_width(trimmed))
    return trimmed + (" " * pad)


@dataclass(frozen=True)
class PanelTheme:
    width_min: int = 40
    height_min: int = 10
    border_top_left: str = "╭"
    border_top_right: str = "╮"
    border_bottom_left: str = "╰"
    border_bottom_right: str = "╯"
    border_h: str = "─"
    border_v: str = "│"
    border_sep_left: str = "├"
    border_sep_right: str = "┤"
    pointer_left: str = "›"
    pointer_right: str = "‹"


class DecisionPanelPage:
    def __init__(
        self,
        *,
        title: str = "Decision Panel",
        prompt_text: str = "Make a selection",
        operation_tips: str = "",
        enter_key: Optional[Dict[ActionName, KeyName]] = None,
        clear_mode: Literal["system", "ansi", "none"] = "system",
        theme: Optional[PanelTheme] = None,
        refresh_interval: float = 0.06,
    ):
        """
        Create a reusable decision panel page.

        :param title: Panel title.
        :param prompt_text: Prompt line shown near confirmation hint.
        :param operation_tips: Tips shown at the bottom.
        :param enter_key: Key mapping for actions; missing actions will use defaults.
        :param clear_mode: "system" uses cls/clear; "ansi" uses escape codes; "none" does not clear.
        :param theme: Visual theme.
        :param refresh_interval: Main loop sleep interval.
        :return: None
        Example:
        >>> _page = DecisionPanelPage(operation_tips="Use arrows/WASD.", enter_key={"decision": "Enter"})
        >>> isinstance(_page, DecisionPanelPage)
        True
        """
        self._theme = theme or PanelTheme()
        self._title = title
        self._prompt_text = prompt_text
        self._operation_tips = operation_tips
        self._clear_mode = clear_mode
        self._refresh_interval = float(refresh_interval)

        self._options: List[OptionItem] = []
        self._selected_index: int = 0
        self._running: bool = False
        self._result: Optional[str] = None

        default_keys: Dict[ActionName, KeyName] = {"decision": "Enter", "back": "Esc", "continue": "Tab"}
        merged = {**default_keys, **(enter_key or {})}

        self._key_pynput: Dict[ActionName, keyboard.Key | keyboard.KeyCode | None] = {}
        self._key_display: Dict[ActionName, str] = {}
        for action in ("back", "continue", "decision"):
            action: Literal["back", "continue", "decision"]
            key_name = merged.get(action)
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

    def set_options(self, options: Iterable[OptionItem]) -> None:
        """
        Set selectable options.

        :param options: Iterable of option items.
        :return: None
        Example:
        >>> _page = DecisionPanelPage()
        >>> _page.set_options([{"prompt": "A", "output": "1"}])
        """
        self._options = list(options)
        self._selected_index = 0

    def set_tips(self, operation_tips: str) -> None:
        """
        Update bottom tips.

        :param operation_tips: Tips string.
        :return: None
        Example:
        >>> _page = DecisionPanelPage()
        >>> _page.set_tips("tips")
        """
        self._operation_tips = operation_tips

    def run_once(self) -> Optional[str]:
        """
        Run the page until user decides or goes back.

        :return: Selected output, or None.
        Example:
        >>> _page = DecisionPanelPage()
        >>> _page.set_options([{"prompt": "A", "output": "1"}])
        >>> # page.run_once()  # interactive
        """
        if not self._options:
            self._clear()
            return None

        self._result = None
        self._running = True
        self._draw()

        listener = keyboard.Listener(on_press=self._on_press)
        listener.start()

        while self._running:
            time.sleep(self._refresh_interval)

        listener.join()
        self._clear()
        return self._result

    def _clear(self) -> None:
        """
        Clear screen based on mode.

        :return: None
        Example:
        >>> _page = DecisionPanelPage(clear_mode="none")
        >>> _page._clear()
        """
        if self._clear_mode == "none":
            return
        if self._clear_mode == "ansi":
            print("\033[2J\033[H", end="", flush=True)
            return
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def _term_size() -> tuple[int, int]:
        """
        Get terminal size.

        :return: (columns, rows)
        Example:
        >>> cols, rows = DecisionPanelPage._term_size()
        >>> isinstance(cols, int) and isinstance(rows, int)
        True
        """
        sz = shutil.get_terminal_size(fallback=(90, 24))
        return int(sz.columns), int(sz.lines)

    def _on_press(self, key: keyboard.Key | keyboard.KeyCode) -> bool:
        """
        Handle key press.

        :param key: Pressed key.
        :return: False to stop listener, True to keep listening.
        Example:
        >>> _page = DecisionPanelPage()
        >>> _page.set_options([{"prompt": "A", "output": "1"}])
        >>> isinstance(page._on_press(keyboard.Key.up), bool)
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
        Render panel to terminal.

        :return: None
        Example:
        >>> _page = DecisionPanelPage(clear_mode="none")
        >>> _page.set_options([{"prompt": "A", "output": "1"}])
        >>> _page._draw()
        """
        self._clear()
        cols, rows = DecisionPanelPage._term_size()
        t = self._theme

        width = min(cols, max(t.width_min, cols))
        width = max(t.width_min, min(cols, width))
        inner_w = max(10, width - 2)

        available_rows = max(t.height_min, rows)
        available_rows = max(t.height_min, min(rows, available_rows))
        header_rows = 1
        sep_rows = 1
        footer_rows = 3
        usable_rows = max(1, available_rows - (header_rows + sep_rows + footer_rows))
        visible_opts = min(len(self._options), usable_rows)

        title = f" {self._title} "
        title = _trim_to_width(title, inner_w)
        left_pad = max(0, (inner_w - _display_width(title)) // 2)
        right_pad = max(0, inner_w - _display_width(title) - left_pad)
        print(f"{t.border_top_left}{t.border_h * left_pad}{title}{t.border_h * right_pad}{t.border_top_right}")

        start = 0
        if self._selected_index >= visible_opts:
            start = self._selected_index - visible_opts + 1
        end = min(len(self._options), start + visible_opts)

        for i in range(start, end):
            opt = self._options[i]
            idx = i + 1
            label = f"{idx:>2}. {opt['prompt']}"
            label_area = max(1, inner_w - 6)
            label = _pad_to_width(label, label_area)

            if i == self._selected_index:
                line = f" {t.pointer_left} {label} {t.pointer_right} "
            else:
                line = f"   {label}   "
            print(f"{t.border_v}{_pad_to_width(line, inner_w)}{t.border_v}")

        for _ in range(usable_rows - (end - start)):
            print(f"{t.border_v}{' ' * inner_w}{t.border_v}")

        print(f"{t.border_sep_left}{t.border_h * inner_w}{t.border_sep_right}")

        decision_key = self._key_display.get("decision", "N/A")
        back_key = self._key_display.get("back", "N/A")
        hint_1 = _pad_to_width(f"{self._prompt_text} (confirm: {decision_key})", inner_w)
        hint_2 = _pad_to_width(f"back: {back_key}    {self._operation_tips}", inner_w)

        print(f"{t.border_v}{hint_1}{t.border_v}")
        print(f"{t.border_v}{hint_2}{t.border_v}")
        print(f"{t.border_bottom_left}{t.border_h * inner_w}{t.border_bottom_right}")

if __name__ == "__main__":
    page = DecisionPanelPage(clear_mode="system", enter_key={"decision": "Enter", "back": "Esc"})

    page.set_options([{"prompt": "Page1 -> Go", "output": "go"}, {"prompt": "Exit", "output": "exit"}])
    v1 = page.run_once()
    if v1 == "go":
        page.set_tips("Now in page 2")
        page.set_options([{"prompt": "Do A", "output": "A"}, {"prompt": "Do B", "output": "B"}])
        v2 = page.run_once()
        print(v2)

