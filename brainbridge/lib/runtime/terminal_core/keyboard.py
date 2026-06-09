"""A tiny pynput-like keyboard surface backed by terminal raw input."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import os
import sys
import threading
import time
from typing import Callable, Optional, Union

__all__ = [
    "Key",
    "KeyCode",
    "KeyInput",
    "decode_escape_sequence",
    "decode_single_char",
    "stdin_is_interactive",
    "Listener",
]


class Key(Enum):
    backspace = "backspace"
    delete = "delete"
    home = "home"
    end = "end"
    page_up = "page_up"
    page_down = "page_down"
    insert = "insert"
    tab = "tab"
    esc = "esc"
    enter = "enter"
    ctrl_a = "ctrl_a"
    ctrl_c = "ctrl_c"
    ctrl_d = "ctrl_d"
    ctrl_e = "ctrl_e"
    ctrl_k = "ctrl_k"
    ctrl_u = "ctrl_u"
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


def decode_single_char(char: str) -> Optional[KeyInput]:
    """Decode a single terminal character into a public key object."""
    if not char:
        return None
    control_map = {
        "\x01": Key.ctrl_a,
        "\x03": Key.ctrl_c,
        "\x04": Key.ctrl_d,
        "\x05": Key.ctrl_e,
        "\x08": Key.backspace,
        "\x0b": Key.ctrl_k,
        "\x09": Key.tab,
        "\x0d": Key.enter,
        "\x0a": Key.enter,
        "\x15": Key.ctrl_u,
        "\x1b": Key.esc,
        "\x7f": Key.backspace,
    }
    if char in control_map:
        return control_map[char]
    if char.isprintable():
        return KeyCode.from_char(char)
    return None


def decode_escape_sequence(sequence: str) -> Optional[KeyInput]:
    """Decode a terminal escape sequence into a public key object."""
    mapping = {
        "\x1b[A": Key.up,
        "\x1b[B": Key.down,
        "\x1b[C": Key.right,
        "\x1b[D": Key.left,
        "\x1bOA": Key.up,
        "\x1bOB": Key.down,
        "\x1bOC": Key.right,
        "\x1bOD": Key.left,
        "\x1b[3~": Key.delete,
        "\x1b[H": Key.home,
        "\x1b[F": Key.end,
        "\x1bOH": Key.home,
        "\x1bOF": Key.end,
        "\x1b[1~": Key.home,
        "\x1b[4~": Key.end,
        "\x1b[5~": Key.page_up,
        "\x1b[6~": Key.page_down,
        "\x1b[2~": Key.insert,
    }
    return mapping.get(sequence)


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
    _ESCAPE_SEQUENCE_TIMEOUT = 0.08

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
                mapping = {
                    "H": Key.up,
                    "P": Key.down,
                    "K": Key.left,
                    "M": Key.right,
                    "S": Key.delete,
                    "G": Key.home,
                    "O": Key.end,
                    "I": Key.page_up,
                    "Q": Key.page_down,
                    "R": Key.insert,
                }
                return mapping.get(special)
            return decode_single_char(char)
        return None

    def _read_posix_char(self, timeout: float) -> str:
        import select

        if self._fd is None:
            time.sleep(timeout)
            return ""

        ready, _, _ = select.select([self._fd], [], [], timeout)
        if not ready:
            return ""

        data = os.read(self._fd, 1)
        if not data:
            return ""
        return data.decode(errors="replace")

    def _read_key_posix(self, timeout: float) -> Optional[KeyInput]:
        if self._fd is None:
            time.sleep(timeout)
            return None

        char = self._read_posix_char(timeout)
        if not char:
            return None
        if char != "\x1b":
            return decode_single_char(char)

        sequence = char
        for _ in range(3):
            next_char = self._read_posix_char(self._ESCAPE_SEQUENCE_TIMEOUT)
            if not next_char:
                break
            sequence += next_char
            decoded = decode_escape_sequence(sequence)
            if decoded is not None:
                return decoded

        return decode_escape_sequence(sequence) or Key.esc
