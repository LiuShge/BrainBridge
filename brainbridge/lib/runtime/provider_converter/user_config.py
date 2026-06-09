from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict

from brainbridge.lib.runtime.files_manager.manager import read_json, return_path_of_dir_under_root_dir

__all__ = [
    "read_user_provider_config",
    "write_user_provider_config",
    "update_user_provider_config",
]

_ALLOWED_FILES = frozenset({"base_arg_match.json", "escape_table.json"})


def _validate_allowed_file_name(file_name: str) -> str:
    candidate = Path(file_name)

    if candidate.is_absolute():
        raise ValueError("absolute paths are not allowed")
    if candidate.name != file_name or len(candidate.parts) != 1:
        raise ValueError("path traversal is not allowed")
    if file_name not in _ALLOWED_FILES:
        raise ValueError(f"unsupported config file: {file_name}")

    return file_name


def _user_config_path(file_name: str) -> Path:
    safe_name = _validate_allowed_file_name(file_name)
    config_root = Path(return_path_of_dir_under_root_dir("config"))
    return config_root / "user_conf" / safe_name


def _ensure_serializable(data: Dict[str, Any]) -> str:
    if not isinstance(data, dict):
        raise TypeError("data must be a dict")
    try:
        return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise ValueError("data must be JSON serializable") from exc


def _backup_file(target_path: Path) -> None:
    if not target_path.exists():
        return
    backup_path = target_path.with_suffix(target_path.suffix + ".bak")
    shutil.copy2(target_path, backup_path)


def _write_json_file(target_path: Path, raw_json: str) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=target_path.parent,
        prefix=f"{target_path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        handle.write(raw_json)
        handle.write("\n")
        temp_name = handle.name

    try:
        json.loads(Path(temp_name).read_text(encoding="utf-8"))
        os.replace(temp_name, target_path)
    except Exception:
        Path(temp_name).unlink(missing_ok=True)
        raise

    read_json(str(target_path))


def _clear_converter_cache() -> None:
    from .converter import _ConfigEngine

    _ConfigEngine._CACHE.clear()


def read_user_provider_config(file_name: str) -> Dict[str, Any]:
    target_path = _user_config_path(file_name)
    return read_json(str(target_path)) if target_path.exists() else {}


def write_user_provider_config(file_name: str, data: Dict[str, Any], *, backup: bool = True) -> None:
    target_path = _user_config_path(file_name)
    raw_json = _ensure_serializable(data)

    if backup:
        _backup_file(target_path)

    _write_json_file(target_path, raw_json)
    _clear_converter_cache()


def update_user_provider_config(file_name: str, patch: Dict[str, Any], *, backup: bool = True) -> None:
    if not isinstance(patch, dict):
        raise TypeError("patch must be a dict")

    current = read_user_provider_config(file_name)
    merged = {**current, **patch}
    write_user_provider_config(file_name, merged, backup=backup)
