from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Union, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from pynput import keyboard

ActionName = Literal["back", "continue", "decision"]
KeyName = Literal[
    "BackSpace", "Tab", "Esc", "Enter",
    "up", "down", "left", "right",
    "w", "a", "s", "d"
]
OptionItem = Dict[Literal["prompt", "output"], str]

def _get_pynput_key(key_str: str) -> Union[keyboard.Key, keyboard.KeyCode]: ...
def _display_width(text: str) -> int: ...
def _trim_to_width(text: str, max_width: int) -> str: ...
def _pad_to_width(text: str, width: int) -> str: ...

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
    ) -> None: ...

    def set_options(self, options: Iterable[OptionItem]) -> None: ...
    def set_tips(self, operation_tips: str) -> None: ...
    def run_once(self) -> Optional[str]: ...

    def _clear(self) -> None: ...
    def _term_size(self) -> tuple[int, int]: ...
    def _on_press(self, key: Union[keyboard.Key, keyboard.KeyCode]) -> bool: ...
    def _draw(self) -> None: ...
