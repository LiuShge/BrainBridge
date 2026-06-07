"""A tiny pynput-like keyboard surface backed by terminal raw input."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import os
import sys
import threading
import time
from typing import Callable, Optional, Union

__all__ = ["Key", "KeyCode", "KeyInput", "stdin_is_interactive", "Listener"]


class Key(Enum):
    backspace = "backspace"
    tab = "tab"
    esc = "esc"
    enter = "enter"
    up = "up"
    down = "down"
    left = "left"
    right = "right"


@dataclass(frozen=True)
class KeyCode:
    char: str

    @classmethod
    def from_char(cls, char: str) -> "KeyCode":
        if not char:
            raise ValueError("char must not be empty")
        return cls(char=char[0].lower())


KeyInput = Union[Key, KeyCode]


def stdin_is_interactive() -> bool:
    """Return True when stdin is attached to an interactive TTY."""
    return hasattr(sys.stdin, "isatty") and bool(sys.stdin.isatty())


class Listener:
    def __init__(self, on_press: Optional[Callable[[KeyInput], bool]] = None):
        self._on_press = on_press
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def join(self) -> None:
        self._thread.join()

    def stop(self) -> None:
        self._stop_event.set()

    def _run(self) -> None:
        reader = _RawKeyReader()
        with reader:
            while not self._stop_event.is_set():
                key = reader.read_key(timeout=0.10)
                if key is None:
                    continue
                should_continue = True
                if self._on_press is not None:
                    should_continue = bool(self._on_press(key))
                if not should_continue:
                    self.stop()
                    break


class _RawKeyReader:
    def __init__(self) -> None:
        self._stdin = sys.stdin
        self._active = False
        self._is_tty = hasattr(self._stdin, "isatty") and self._stdin.isatty()
        self._fd = self._stdin.fileno() if self._is_tty and hasattr(self._stdin, "fileno") else None
        self._restore_state = None

    def __enter__(self) -> "_RawKeyReader":
        if not self._is_tty:
            return self
        if os.name == "nt":
            self._active = True
            return self
        import termios
        import tty

        assert self._fd is not None
        self._restore_state = termios.tcgetattr(self._fd)
        tty.setraw(self._fd)
        self._active = True
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if not self._active or not self._is_tty:
            return
        if os.name != "nt" and self._restore_state is not None:
            import termios

            assert self._fd is not None
            termios.tcsetattr(self._fd, termios.TCSADRAIN, self._restore_state)
        self._active = False

    def read_key(self, timeout: float = 0.10) -> Optional[KeyInput]:
        if not self._is_tty:
            time.sleep(timeout)
            return None
        if os.name == "nt":
            return self._read_key_windows(timeout)
        return self._read_key_posix(timeout)

    @staticmethod
    def _decode_single_char(char: str) -> Optional[KeyInput]:
        if not char:
            return None
        if char in ("\r", "\n"):
            return Key.enter
        if char == "\t":
            return Key.tab
        if char == "\x1b":
            return Key.esc
        if char in ("\x08", "\x7f"):
            return Key.backspace
        if char.isprintable():
            return KeyCode.from_char(char)
        return None

    def _read_key_windows(self, timeout: float) -> Optional[KeyInput]:
        import msvcrt

        deadline = time.time() + timeout
        while time.time() < deadline:
            if not msvcrt.kbhit():
                time.sleep(0.01)
                continue
            char = msvcrt.getwch()
            if char in ("\x00", "\xe0"):
                special = msvcrt.getwch()
                mapping = {"H": Key.up, "P": Key.down, "K": Key.left, "M": Key.right}
                return mapping.get(special)
            return self._decode_single_char(char)
        return None

    def _read_key_posix(self, timeout: float) -> Optional[KeyInput]:
        import select

        if self._fd is None:
            time.sleep(timeout)
            return None
        ready, _, _ = select.select([self._stdin], [], [], timeout)
        if not ready:
            return None

        char = self._stdin.read(1)
        if char != "\x1b":
            return self._decode_single_char(char)

        ready, _, _ = select.select([self._stdin], [], [], 0.01)
        if not ready:
            return Key.esc
        second = self._stdin.read(1)
        if second != "[":
            return Key.esc

        ready, _, _ = select.select([self._stdin], [], [], 0.01)
        if not ready:
            return Key.esc
        third = self._stdin.read(1)
        mapping = {"A": Key.up, "B": Key.down, "C": Key.right, "D": Key.left}
        return mapping.get(third, Key.esc)
