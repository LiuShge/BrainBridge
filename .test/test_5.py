import contextlib
import io
import importlib

from brainbridge.utils.decision_panel import DecisionPanelPage
from brainbridge.lib.runtime.terminal_core import keyboard


assert keyboard.decode_escape_sequence("\x1b[A") == keyboard.Key.up
assert keyboard.decode_escape_sequence("\x1b[B") == keyboard.Key.down
assert keyboard.decode_escape_sequence("\x1b[C") == keyboard.Key.right
assert keyboard.decode_escape_sequence("\x1b[D") == keyboard.Key.left
assert keyboard.decode_escape_sequence("\x1bOA") == keyboard.Key.up
assert keyboard.decode_escape_sequence("\x1bOB") == keyboard.Key.down
assert keyboard.decode_escape_sequence("\x1bOC") == keyboard.Key.right
assert keyboard.decode_escape_sequence("\x1bOD") == keyboard.Key.left
assert keyboard.decode_escape_sequence("\x1b[3~") == keyboard.Key.delete
assert keyboard.decode_escape_sequence("\x1b[H") == keyboard.Key.home
assert keyboard.decode_escape_sequence("\x1b[F") == keyboard.Key.end
assert keyboard.decode_escape_sequence("\x1bOH") == keyboard.Key.home
assert keyboard.decode_escape_sequence("\x1bOF") == keyboard.Key.end
assert keyboard.decode_escape_sequence("\x1b[1~") == keyboard.Key.home
assert keyboard.decode_escape_sequence("\x1b[4~") == keyboard.Key.end
assert keyboard.decode_escape_sequence("\x1b[5~") == keyboard.Key.page_up
assert keyboard.decode_escape_sequence("\x1b[6~") == keyboard.Key.page_down
assert keyboard.decode_escape_sequence("\x1b[2~") == keyboard.Key.insert
assert keyboard.decode_single_char("\x01") == keyboard.Key.ctrl_a
assert keyboard.decode_single_char("\x03") == keyboard.Key.ctrl_c
assert keyboard.decode_single_char("\x04") == keyboard.Key.ctrl_d
assert keyboard.decode_single_char("\x05") == keyboard.Key.ctrl_e
assert keyboard.decode_single_char("\x0b") == keyboard.Key.ctrl_k
assert keyboard.decode_single_char("\x15") == keyboard.Key.ctrl_u
assert keyboard.decode_single_char("\x7f") == keyboard.Key.backspace
assert "decode_escape_sequence" in keyboard.__all__
assert "decode_single_char" in keyboard.__all__
assert "_RawKeyReader" not in keyboard.__all__
try:
    importlib.import_module("brainbridge.run_lib.terminal_core")
except ImportError:
    pass
else:
    raise AssertionError("brainbridge.run_lib.terminal_core should no longer be importable")

page = DecisionPanelPage(operation_tips="Use arrow keys or WASD.", clear_mode="none")
page.set_options([
    {"prompt": "Alpha", "output": "A"},
    {"prompt": "Beta", "output": "B"},
])
page._draw = lambda: None  # type: ignore[method-assign]

assert page._on_press(keyboard.Key.down) is True
assert page._on_press(keyboard.KeyCode.from_char("w")) is True
assert page._on_press(keyboard.Key.enter) is False
assert page._result == "A"

page = DecisionPanelPage(operation_tips="Use arrow keys or WASD.", clear_mode="none")
page.set_options([
    {"prompt": "Alpha", "output": "A"},
    {"prompt": "Beta", "output": "B"},
])
page._draw = lambda: None  # type: ignore[method-assign]
assert page._on_press(keyboard.Key.down) is True
assert page._on_press(keyboard.Key.tab) is False
assert page._result == "B"

layout_page = DecisionPanelPage(operation_tips="Use arrow keys or WASD.", clear_mode="none")
layout_page.set_options([
    {"prompt": "Alpha", "output": "A"},
    {"prompt": "Beta", "output": "B"},
])
original_term_size = DecisionPanelPage._term_size
DecisionPanelPage._term_size = staticmethod(lambda: (20, 6))
try:
    rendered = io.StringIO()
    with contextlib.redirect_stdout(rendered):
        layout_page._draw()
finally:
    DecisionPanelPage._term_size = original_term_size

rendered_text = rendered.getvalue()
for line in rendered_text.splitlines():
    assert len(line) <= 20

assert "\r\n" in rendered_text
assert "input:" not in rendered_text
assert "\033[7m" not in rendered_text

input_page = DecisionPanelPage(
    operation_tips="Use arrow keys or WASD.",
    clear_mode="none",
    enable_input_box=True,
)
input_page.set_options([
    {"prompt": "Alpha", "output": "A"},
    {"prompt": "Beta", "output": "B"},
])
input_page._input_text = "hello"
input_page._input_cursor = len(input_page._input_text)
original_term_size = DecisionPanelPage._term_size
DecisionPanelPage._term_size = staticmethod(lambda: (30, 8))
try:
    rendered = io.StringIO()
    with contextlib.redirect_stdout(rendered):
        input_page._draw()
finally:
    DecisionPanelPage._term_size = original_term_size

input_rendered_text = rendered.getvalue()
assert "input: hello|" in input_rendered_text

highlight_render_page = DecisionPanelPage(
    operation_tips="Use arrow keys or WASD.",
    clear_mode="none",
    highlight_current=True,
)
highlight_render_page.set_options([
    {"prompt": "Alpha", "output": "A"},
    {"prompt": "Beta", "output": "B"},
])
original_term_size = DecisionPanelPage._term_size
DecisionPanelPage._term_size = staticmethod(lambda: (30, 8))
try:
    rendered = io.StringIO()
    with contextlib.redirect_stdout(rendered):
        highlight_render_page._draw()
finally:
    DecisionPanelPage._term_size = original_term_size

assert "\033[7m" in rendered.getvalue()

highlight_page = DecisionPanelPage(
    operation_tips="Use arrow keys or WASD.",
    clear_mode="none",
    enable_input_box=True,
    highlight_current=True,
    input_return_mode="dict",
    input_clear_keys={"delete"},
)
highlight_page.set_options([
    {"prompt": "Alpha", "output": "A"},
    {"prompt": "Beta", "output": "B"},
])
highlight_page._draw = lambda: None  # type: ignore[method-assign]
assert highlight_page._on_press(keyboard.KeyCode.from_char("x")) is True
assert highlight_page._input_text == "x"
assert highlight_page._on_press(keyboard.Key.delete) is True
assert highlight_page._input_text == ""
assert highlight_page._on_press(keyboard.Key.enter) is False
assert highlight_page._result == {"selection": "A", "input": ""}

tab_page = DecisionPanelPage(
    operation_tips="Use arrow keys or WASD.",
    clear_mode="none",
    enable_input_box=True,
    input_return_mode="dict",
)
tab_page.set_options([
    {"prompt": "Alpha", "output": "A"},
    {"prompt": "Beta", "output": "B"},
])
tab_page._draw = lambda: None  # type: ignore[method-assign]
assert tab_page._on_press(keyboard.Key.tab) is False
assert tab_page._result == {"selection": "A", "input": ""}

esc_page = DecisionPanelPage(
    operation_tips="Use arrow keys or WASD.",
    clear_mode="none",
    enable_input_box=True,
)
esc_page.set_options([
    {"prompt": "Alpha", "output": "A"},
    {"prompt": "Beta", "output": "B"},
])
esc_page._draw = lambda: None  # type: ignore[method-assign]
assert esc_page._on_press(keyboard.Key.esc) is False
assert esc_page._result is None
