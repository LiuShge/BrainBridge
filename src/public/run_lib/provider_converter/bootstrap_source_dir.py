from os import path
from sys import path as sys_path
from typing import Optional, List

_RAW_SYS_PATH:Optional[List[str]] = None

def _set_source_dir():

    global _RAW_SYS_PATH
    if _RAW_SYS_PATH is None:
        _RAW_SYS_PATH = sys_path.copy()

    def _find_src() -> str:
        _file_path = path.dirname(__file__)
        _source_index = _file_path.find("src")
        if _source_index == -1:
            raise RuntimeError(f"Unexpected file path: {_file_path}. Expected to contain 'src'.")
        _source_path = path.join(str(_file_path[:_source_index]),"src")
        return _source_path

    sys_path.append(_find_src())

def _restore_sys_path():

    global _RAW_SYS_PATH

    if _RAW_SYS_PATH is None:
        raise RuntimeError(
            "Cannot restore sys.path: Initial state was not cached. "
            "Ensure `change_sys_path()` is called first or manually cache sys.path."
        )
    sys_path[:] = _RAW_SYS_PATH
