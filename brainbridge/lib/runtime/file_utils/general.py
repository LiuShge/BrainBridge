"""General file-management APIs for BrainBridge runtime."""

from __future__ import annotations

import json
from json import JSONDecodeError, loads
from os import listdir, path, scandir
from pathlib import Path
from typing import Any, Dict, List, Literal, Set, Union

from brainbridge.lib.runtime.file_utils.ignores import IgnoreSpec, normalize_ignores, should_ignore_name
from brainbridge.utils.chardet import detect

__all__ = [
    "return_path_of_dir_under_root_dir",
    "return_dir_member",
    "valid_path",
    "return_full_tree",
    "write_content_tofile",
    "read_file",
    "read_json",
    "write_json",
]


def return_path_of_dir_under_root_dir(dir_name: str) -> str:
    """
    Returns the absolute path of a specified directory located directly under the project's root directory.
    The project root is determined by walking upward until `pyproject.toml` is found.

    :param dir_name: The name of the directory to locate under the project root.
    :return: The absolute path of the specified directory.
    :raises ValueError: If the repository root cannot be found,
                        if the specified `dir_name` is not found under the root,
                        or if `dir_name` is not a directory.
    """
    current_file = Path(__file__).resolve()
    root_dir: Path | None = None

    for parent in current_file.parents:
        if (parent / "pyproject.toml").exists():
            root_dir = parent
            break

    if root_dir is None:
        raise ValueError(
            f"Unexpected file path: {current_file}. Could not locate repository root via 'pyproject.toml'."
        )

    target_dir = root_dir / dir_name
    if not target_dir.exists():
        raise ValueError(f'Cannot find "{dir_name}" under root directory.')
    if not target_dir.is_dir():
        raise ValueError(f"{dir_name} under root dir is not a directory.")
    return str(target_dir)


def return_dir_member(dir_path: str) -> Union[Dict[str, Literal["file", "dir"]], None]:
    """
    Returns a dictionary of members (files and subdirectories) within a given directory.
    If the provided path is a file, returns None.
    """
    if not path.isfile(dir_path) and not path.isdir(dir_path):
        raise ValueError(f"Invalid path: {dir_path}")
    if path.isfile(dir_path):
        return None

    member_list: Dict[str, Literal["file", "dir"]] = {}
    for member in listdir(dir_path):
        member_list[member] = "file" if path.isfile(path.join(dir_path, member)) else "dir"
    return member_list


def valid_path(target_path: str, is_file: bool = True) -> None:
    """
    Validates if a given path exists and is either a file or a directory.
    """
    if not path.exists(target_path):
        raise ValueError(f"Invalid path: {target_path}")
    if is_file and not path.isfile(target_path):
        raise ValueError(f"Path is not a file: {target_path}")
    if not is_file and not path.isdir(target_path):
        raise ValueError(f"Path is not a directory: {target_path}")


def return_full_tree(
    *base_paths: str,
    ignores: IgnoreSpec = None,
) -> Dict[str, List[Union[str, Dict[str, Any]]]]:
    """
    Return a nested tree structure for the provided directories.
    """
    result_tree: Dict[str, List[Union[str, Dict[str, Any]]]] = {}
    normalized_ignores = normalize_ignores(ignores)

    realpath = path.realpath
    join = path.join
    normpath = path.normpath

    def _fast_normalize(p: str) -> str:
        return normpath(p).replace("\\", "/")

    def _explore_recursive(current_dir: str, visited: Set[str]) -> List[Union[str, Dict[str, Any]]]:
        content_list: List[Union[str, Dict[str, Any]]] = []

        try:
            entries = sorted(scandir(current_dir), key=lambda entry: entry.name)

            for entry in entries:
                if entry.is_dir(follow_symlinks=True):
                    if should_ignore_name(entry.name, "dir", normalized_ignores):
                        continue

                    raw_path = entry.path
                    normalized_path = _fast_normalize(raw_path)
                    real_p = realpath(raw_path)
                    if real_p in visited:
                        content_list.append({normalized_path: [f"_loop_detected_at:{normalized_path}"]})
                        continue

                    new_visited = visited | {real_p}
                    content_list.append({normalized_path: _explore_recursive(raw_path, new_visited)})
                elif entry.is_file():
                    if should_ignore_name(entry.name, "file", normalized_ignores):
                        continue

                    raw_path = entry.path
                    normalized_path = _fast_normalize(raw_path)
                    content_list.append(normalized_path)

        except PermissionError:
            content_list.append(f"_permission_denied_for:{_fast_normalize(current_dir)}")
        except OSError as exc:
            content_list.append(f"_error_accessing:{_fast_normalize(current_dir)}:{exc}")

        return content_list

    for base_path_str in base_paths:
        valid_path(base_path_str, is_file=False)
        norm_base = _fast_normalize(base_path_str)
        result_tree[norm_base] = _explore_recursive(base_path_str, {realpath(base_path_str)})

    return result_tree


def _auto_file_code(file_path: str) -> str:
    """Detect the encoding of a given file."""
    with open(file_path, "rb") as f:
        detected = detect(f.read()).get("encoding")
        return detected or "utf-8"


def write_content_tofile(
    file_path: str,
    content: str,
    file_code: Literal["utf-8", "auto"] = "utf-8",
    trailing_newline: bool = True,
    override: bool = False,
) -> None:
    """
    Writes content to a specified file.
    """
    try:
        valid_path(file_path)
    except (FileNotFoundError, ValueError):
        if override:
            with open(file_path, "w"):
                pass
        else:
            raise
    if file_code == "auto":
        file_code = _auto_file_code(file_path)

    with open(file_path, "a" if not override else "w", encoding=file_code) as f:
        f.write(content)
        if trailing_newline:
            f.write("\n")


def read_file(
    file_path: str,
    line_by_line: bool = False,
    file_code: Literal["utf-8", "auto"] = "utf-8",
) -> Union[str, List[str]]:
    """
    Reads content from a specified file.
    """
    valid_path(file_path)
    if file_code == "auto":
        file_code = _auto_file_code(file_path)
    with open(file_path, "r", encoding=file_code) as f:
        if line_by_line:
            return [line for line in f]
        return str(f.read())


def read_json(
    file_path: str,
    file_code: Literal["utf-8", "auto"] = "utf-8",
    parse: bool = True,
) -> Union[str, Dict[str, Any]]:
    """
    Reads content from a JSON file and optionally parses it.
    """
    valid_path(file_path)
    if file_code == "auto":
        file_code = _auto_file_code(file_path)
    with open(file_path, "r", encoding=file_code) as f:
        content = f.read()
    if not parse:
        return content
    try:
        return loads(content)
    except JSONDecodeError as exc:
        raise ValueError(f"Invalid json file: {exc}") from exc


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
