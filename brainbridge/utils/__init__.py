"""Common utility APIs for BrainBridge."""

from importlib import import_module

__all__ = [
    "DecisionPanelPage",
    "PanelTheme",
    "Time",
    "detect",
    "display_loading_bar",
]


def __getattr__(name: str):
    if name == "detect":
        return getattr(import_module("brainbridge.utils.chardet"), name)
    if name in {"DecisionPanelPage", "PanelTheme"}:
        return getattr(import_module("brainbridge.utils.decision_panel"), name)
    if name == "display_loading_bar":
        return getattr(import_module("brainbridge.utils.loading_bar"), name)
    if name == "Time":
        return getattr(import_module("brainbridge.utils.timer"), name)
    raise AttributeError(f"module 'brainbridge.utils' has no attribute {name!r}")
