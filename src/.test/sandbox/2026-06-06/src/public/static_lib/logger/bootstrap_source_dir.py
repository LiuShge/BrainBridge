from pathlib import Path
from sys import path as sys_path
from typing import Optional, List

_RAW_SYS_PATH:Optional[List[str]] = None

def _set_source_dir():

    global _RAW_SYS_PATH
    if _RAW_SYS_PATH is None:
        _RAW_SYS_PATH = sys_path.copy()

    def _find_src() -> str:
        current_file = Path(__file__).resolve()
        for parent in current_file.parents:
            if parent.name == "src":
                return str(parent)
        raise RuntimeError(f"Unexpected file path: {current_file}. Expected to contain a 'src' directory.")

    source_path = _find_src()
    if source_path not in sys_path:
        sys_path.append(source_path)

def _restore_sys_path():

    global _RAW_SYS_PATH

    if _RAW_SYS_PATH is None:
        raise RuntimeError(
            "Cannot restore sys.path: Initial state was not cached. "
            "Ensure `change_sys_path()` is called first or manually cache sys.path."
        )
    sys_path[:] = _RAW_SYS_PATH
