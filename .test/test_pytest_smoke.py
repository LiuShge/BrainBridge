from pathlib import Path
import importlib
import runpy


TEST_DIR = Path(__file__).resolve().parent


def _run_smoke(script_name: str) -> None:
    runpy.run_path(str(TEST_DIR / script_name), run_name="__main__")


def test_public_imports() -> None:
    from brainbridge import Converter, Logger, LogLevels, Operator, Request
    from brainbridge.lib.runtime.provider_converter import Converter as RuntimeConverter
    from brainbridge.lib.runtime.requests_core import Request as RuntimeRequest
    from brainbridge.lib.static.logger import Logger as StaticLogger
    from brainbridge.utils import Time

    assert Converter is RuntimeConverter
    assert Request is RuntimeRequest
    assert Logger is StaticLogger
    assert LogLevels.INFO.value == "INFO"
    assert hasattr(Operator, "HeadersBuilder")
    assert Time.__name__ == "Time"


def test_old_paths_are_gone() -> None:
    for removed_module in ("brainbridge.run_lib", "brainbridge.static_lib"):
        try:
            importlib.import_module(removed_module)
        except ImportError:
            continue
        raise AssertionError(f"{removed_module} should no longer be importable")


def test_smoke_test_1() -> None:
    _run_smoke("test_1.py")


def test_smoke_test_2() -> None:
    _run_smoke("test_2.py")


def test_smoke_test_5() -> None:
    _run_smoke("test_5.py")


def test_smoke_test_7() -> None:
    _run_smoke("test_7.py")
