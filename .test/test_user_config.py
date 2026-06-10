from __future__ import annotations

import json
from pathlib import Path

from brainbridge.lib.runtime.file_utils import return_path_of_dir_under_root_dir
from brainbridge.lib.runtime.provider_converter import (
    read_user_provider_config,
    update_user_provider_config,
    write_user_provider_config,
)
from brainbridge.lib.static.checker.checker import CheckTools


CONFIG_ROOT = Path(return_path_of_dir_under_root_dir("config"))
USER_CONF = CONFIG_ROOT / "user_conf"
SYS_CONF = CONFIG_ROOT / "sys_conf"


def _snapshot(paths: list[Path]) -> dict[Path, str | None]:
    return {file_path: file_path.read_text(encoding="utf-8") if file_path.exists() else None for file_path in paths}


def _restore(snapshot: dict[Path, str | None]) -> None:
    for file_path, content in snapshot.items():
        if content is None:
            file_path.unlink(missing_ok=True)
        else:
            file_path.write_text(content, encoding="utf-8")


def test_user_conf_writes_and_guards() -> None:
    managed_paths = [
        USER_CONF / "base_arg_match.json",
        USER_CONF / "escape_table.json",
        USER_CONF / "base_arg_match.json.bak",
        USER_CONF / "escape_table.json.bak",
    ]
    sys_paths = [
        SYS_CONF / "base_arg_match.json",
        SYS_CONF / "escape_table.json",
    ]
    managed_snapshot = _snapshot(managed_paths)
    sys_snapshot = _snapshot(sys_paths)

    try:
        base_payload = {"based_args": ["messages", "model"], "demo": {"input": {"messages": "messages", "model": "model"}}}
        escape_payload = {"demo": {"input": {"messages": ["dict"], "model": "str"}}}

        write_user_provider_config("base_arg_match.json", base_payload)
        write_user_provider_config("escape_table.json", escape_payload)

        assert read_user_provider_config("base_arg_match.json") == base_payload
        assert read_user_provider_config("escape_table.json") == escape_payload

        update_user_provider_config("base_arg_match.json", {"extra": {"input": {"messages": "messages", "model": "model"}}})
        updated_base = read_user_provider_config("base_arg_match.json")
        assert updated_base["extra"]["input"]["messages"] == "messages"

        assert json.loads((USER_CONF / "base_arg_match.json").read_text(encoding="utf-8")) == updated_base
        assert json.loads((USER_CONF / "escape_table.json").read_text(encoding="utf-8")) == escape_payload

        for bad_name in ("sys_conf/base_arg_match.json", "../escape_table.json", "/tmp/base_arg_match.json", "unknown.json"):
            try:
                write_user_provider_config(bad_name, {})
            except ValueError:
                pass
            else:
                raise AssertionError(f"{bad_name!r} should be rejected")

        assert _snapshot(sys_paths) == sys_snapshot
    finally:
        _restore(managed_snapshot)


def test_fix_code_file_requires_explicit_backup_path() -> None:
    try:
        CheckTools.fix_code_file("brainbridge/__init__.py")
    except ValueError as exc:
        assert "backup_path must be provided explicitly" in str(exc)
    else:
        raise AssertionError("fix_code_file should require an explicit backup_path")
