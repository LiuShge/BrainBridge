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
