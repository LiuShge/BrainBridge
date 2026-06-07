import os
from pathlib import Path
from os import path
from typing import Dict, Literal, Union, List, Tuple, Optional
from sys import path as sys_path

def packages_path() -> Dict[Literal['run_lib', 'static_lib'], str]:
    r"""
    Dynamically finds the absolute paths of `run_lib` and `static_lib` directories in the project.

    :return: Dictionary with keys 'run_lib' and 'static_lib', values are their absolute paths.
    :raises ValueError: If required directories are not found or path is invalid.

    Example:
    >>> paths = packages_path()
    >>> print(paths)
    {'run_lib': 'C:\\Users\\Serge\\Desktop\\BrainBridge\\src\\public\\run_lib', 'static_lib': 'C:\\Users\\Serge\\Desktop\\BrainBridge\\src\\public\\static_lib'}
    """

    current_file = Path(__file__).resolve()
    for parent in current_file.parents:
        if parent.name == "src":
            project_root = parent.parent
            run_lib = project_root / "src" / "public" / "run_lib"
            static_lib = project_root / "src" / "public" / "static_lib"
            if not run_lib.is_dir() or not static_lib.is_dir():
                missing = []
                if not run_lib.is_dir():
                    missing.append("run_lib")
                if not static_lib.is_dir():
                    missing.append("static_lib")
                raise ValueError(f"Failed to find directories: {', '.join(missing)}")
            return {
                "run_lib": str(run_lib),
                "static_lib": str(static_lib),
            }

    raise ValueError(f"Unexpected file path: {current_file}. Expected to contain a 'src' directory.")

_INITIAL_SYS_PATH: Optional[List[str]] = None

def change_sys_path(to_runlib: bool = False, to_staticlib: bool = False) -> None:
    """
    Dynamically appends the path of `run_lib` or `static_lib` to `sys.path`.

    Args:
        to_runlib: If True, appends the `run_lib` path.
        to_staticlib: If True, appends the `static_lib` path.

    Raises:
        ValueError: If both `to_runlib` and `to_staticlib` are True/False, or path resolution fails.

    Example:
        >>> change_sys_path(to_runlib=True)  # Appends run_lib to sys.path
        >>> change_sys_path(to_staticlib=True)  # Appends static_lib to sys.path
    """
    global _INITIAL_SYS_PATH
    if _INITIAL_SYS_PATH is None:
        _INITIAL_SYS_PATH = sys_path.copy()
    if to_runlib == to_staticlib:
        raise ValueError(
            "Must specify exactly one of `to_runlib` or `to_staticlib` as True."
        )

    try:
        target_path = (
            packages_path()["run_lib"] if to_runlib
            else packages_path()["static_lib"]
        )
    except KeyError as e:
        raise ValueError(f"Failed to resolve path: {str(e)}") from e
    except Exception as e:
        raise ValueError(f"Unexpected error during path resolution: {str(e)}") from e

    if target_path not in sys_path:
        sys_path.append(target_path)

def restore_sys_path() -> None:
    """
    Restores `sys.path` to its initial state when the program started.

    This function is typically used after calling `change_sys_path()` to clean up
    dynamically appended paths. The initial `sys.path` is cached on first call.

    Raises:
        RuntimeError: If called before `sys.path` is cached (i.e., before `change_sys_path()`).

    Example:
        >>> change_sys_path(to_runlib=True)  # Adds run_lib to sys.path
        >>> restore_sys_path()  # Restores sys.path to its initial state
    """
    global _INITIAL_SYS_PATH
    if _INITIAL_SYS_PATH is None:
        raise RuntimeError(
            "Cannot restore sys.path: Initial state was not cached. "
            "Ensure `change_sys_path()` is called first or manually cache sys.path."
        )
    sys_path[:] = _INITIAL_SYS_PATH


if __name__ == "__main__":
    change_sys_path(to_runlib=True)
    import requests_core.request_core
    print(requests_core.request_core.Request.request_sse)
    change_sys_path(to_staticlib=True)
    print(packages_path()["run_lib"] in sys_path and packages_path()["static_lib"] in sys_path)
    restore_sys_path()
    print(packages_path()["run_lib"] in sys_path and packages_path()["static_lib"] in sys_path)
