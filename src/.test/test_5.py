import contextlib
import io

from src.public.run_lib.mini_tools.decision_panel import DecisionPanelPage
from src.public.run_lib.terminial_core import keyboard


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

for line in rendered.getvalue().splitlines():
    assert len(line) <= 20
