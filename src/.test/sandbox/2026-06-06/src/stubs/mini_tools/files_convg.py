"""Aggregate files into a single portable backup and unpack it later."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Iterator, Mapping, Optional, Sequence, Tuple

MAGIC_START: str
MAGIC_END: str
TREE_BEGIN: str
TREE_END: str
RECORD_BEGIN: str
RECORD_END: str

META_PREFIX: str
TREE_DATA_PREFIX: str
FILE_META_PREFIX: str
FILE_CHECK_PREFIX: str
PAYLOAD_PREFIX: str

VERSION: int
TREE_HEADER_FORMAT: str
B64_WRAP: int
CHUNK_SIZE: int


class BackupError(Exception): ...


def to_posix(path: str | Path) -> str: ...
def is_special_marker(node: str) -> bool: ...
def iter_tree_files(tree: Mapping[str, Sequence[str | Dict[str, Any]]]) -> Iterator[Tuple[str, str]]: ...
def root_prefix_id(root: str) -> str: ...
def relative_under_root(root: str, file_path: str) -> str: ...
def b64_encode_stream(src: Iterable[bytes], wrap: int = B64_WRAP) -> Iterator[str]: ...
def build_compact_file_tree(tree: Mapping[str, Sequence[str | Dict[str, Any]]]) -> Dict[str, Any]: ...
def has_file_tree_header(backup_file_path: str | Path) -> bool: ...
def read_file_tree_header(backup_file_path: str | Path, validate: bool = False) -> Optional[Dict[str, Any]]: ...
def inject_file_tree_header(
    backup_file_path: str | Path,
    tree: Mapping[str, Sequence[str | Dict[str, Any]]],
    validate: bool = True,
) -> None: ...
def aggregate_to_backup(
    tree: Mapping[str, Sequence[str | Dict[str, Any]]],
    output_backup_path: str | Path,
    progress_callback: Optional[Callable[[int], None]] = None,
    include_file_tree_header: bool = False,
    validate_file_tree_header: bool = True,
) -> None: ...
def unpack_from_backup(
    backup_file_path: str | Path,
    target_extraction_dir: str | Path,
    skip_errors: bool = False,
    progress_callback: Optional[Callable[[int], None]] = None,
) -> None: ...
