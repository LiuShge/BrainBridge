import os
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

    def _find_path(_base_path: Union[List[str], Tuple[str]]) -> dict[str, str]:
        """
        Recursively searches for 'run_lib' and 'static_lib' directories using BFS strategy.

        Features:
        - Breadth-First Search (BFS) with depth control to avoid infinite recursion.
        - Early termination when both directories are found.
        - Skips directories with permission issues.
        - Ensures absolute paths for returned results.

        Args:
            _base_path: A list or tuple of base directory paths to start the search.

        Returns:
            Dict[str, str]: A dictionary with keys 'run_lib' and 'static_lib' mapping to their absolute paths.

        Raises:
            ValueError: If either 'run_lib' or 'static_lib' is not found within the search depth limit.
            FileNotFoundError: If any base path in `_base_path` does not exist.

        Example:
            >>> _find_path(["/project/src"])
            {'run_lib': '/project/src/public/run_lib', 'static_lib': '/project/src/public/static_lib'}
        """
        return_dict = {"run_lib": "", "static_lib": ""}
        search_queue = list(_base_path)  # Use a queue for BFS
        visited_dirs = set()  # Track visited directories to avoid cycles
        complexity = 0

        while search_queue and complexity <= 8:
            next_level_queue = []
            for current_path in search_queue:
                # Validate path existence and type
                try:
                    if not os.path.isdir(current_path):
                        raise FileNotFoundError(f"Directory not found: {current_path}")
                    if current_path in visited_dirs:
                        continue
                    visited_dirs.add(current_path)
                except (PermissionError, OSError) as _e:
                    continue  # Skip inaccessible directories

                # Check items in the current directory
                try:
                    items = os.listdir(current_path)
                except (PermissionError, OSError):
                    continue

                for item in items:
                    item_path = os.path.join(current_path, item)
                    if not os.path.isdir(item_path):
                        continue  # Skip files

                    # Check for target directories
                    if "run_lib" in item and not return_dict["run_lib"]:
                        return_dict["run_lib"] = os.path.abspath(item_path)
                    elif "static_lib" in item and not return_dict["static_lib"]:
                        return_dict["static_lib"] = os.path.abspath(item_path)
                    else:
                        next_level_queue.append(item_path)  # Add subdirectory to queue

            search_queue = next_level_queue  # Move to next level
            complexity += 1

            # Early exit if both targets are found
            if all(return_dict.values()):
                break

        # Validate results
        if not all(return_dict.values()):
            missing = [k for k, v in return_dict.items() if not v]
            raise ValueError(f"Failed to find directories: {', '.join(missing)} within search depth limit.")

        return return_dict

    # --- Main Logic ---
    file_path = path.dirname(path.abspath(__file__))  # Get absolute path of current file
    path_index = file_path.find("src")

    if path_index == -1:
        raise ValueError(f"Unexpected file path: {file_path}. Expected to contain 'src'.")

    base_path = path.join(file_path[:path_index])  # Project root (one level above 'src')
    try:
        found_paths = _find_path([str(base_path)])
        return {
            "run_lib": found_paths["run_lib"],
            "static_lib": found_paths["static_lib"]
        }
    except Exception as e:
        raise ValueError(f"Path resolution failed: {str(e)}") from e

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
