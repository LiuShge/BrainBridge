"""Common file-management APIs for BrainBridge runtime."""

import json
from typing import Any

from .manager import (
    read_file,
    read_json,
    return_dir_member,
    return_full_tree,
    return_path_of_dir_under_root_dir,
    valid_path,
    write_content_tofile,
)


def write_json(
    file_path: str,
    data: Any,
    *,
    ensure_ascii: bool = False,
    indent: int | None = None,
    override: bool = True,
    trailing_newline: bool = False,
) -> None:
    """Serialize ``data`` as JSON and write it with the existing file helper."""
    content = json.dumps(data, ensure_ascii=ensure_ascii, indent=indent)
    write_content_tofile(
        file_path=file_path,
        content=content,
        file_code="utf-8",
        trailing_newline=trailing_newline,
        override=override,
    )

__all__ = [
    "read_file",
    "read_json",
    "return_dir_member",
    "return_full_tree",
    "return_path_of_dir_under_root_dir",
    "valid_path",
    "write_content_tofile",
    "write_json",
]
