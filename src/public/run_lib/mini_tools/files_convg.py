"""Aggregate files into a single portable backup and unpack it later.

Created by: Gemini 2.5 flash;
            GPT 5.2;
            Mistral Large 3 675B;

This module provides functionalities to create and restore backups of directory trees.
Backup files are UTF-8 encoded and support both text and binary files via Base64 encoding.
The format is line-oriented for headers and chunk-oriented for payloads, ensuring efficient
memory usage during large file operations.

Key Features:
- Cross-platform path handling (POSIX-style paths).
- Streaming encoding/decoding for minimal memory footprint.
- Integrity verification using SHA256 and size checks.
- Support for nested directory structures and symlink loop detection.
- Configurable chunk size and base64 line wrapping for flexibility.

Example Usage:
    >>> # Create a backup
    >>> tree = {"/tmp/src": ["/tmp/src/f1.bin"]}
    >>> aggregate_to_backup(tree, "backup.txt")

    >>> # Restore from backup
    >>> unpack_from_backup("backup.txt", "restored_dir")
"""

from __future__ import annotations

import base64
import hashlib
import os
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, Mapping, Sequence, Optional, Tuple
import logging

from files_manager.manager import valid_path

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Delimiters and Prefixes (Unique unicode markers to avoid collisions)
_OPEN_FOLDER_DELIMITER = "╒════[BACKUP_START]═══╕"
_CLOSE_FOLDER_DELIMITER = "╘════[BACKUP_END]═══╛"
_RECORD_BEGIN = "»[RECORD_BEGIN]«"
_RECORD_END = "»[RECORD_END]«"
_HEADER_PREFIX = "»[HEADER]«"
_PAYLOAD_PREFIX = "»[PAYLOAD]«"
_META_PREFIX = "»[META]«"

# Configuration
VERSION = 2
B64_WRAP = 76  # Base64 line wrap length
CHUNK_SIZE = 1024 * 1024  # 1MB chunks for memory efficiency

class BackupError(Exception):
    """Custom exception for backup-related errors."""
    pass

def to_posix(path: str | Path) -> str:
    """
    Convert a filesystem path to POSIX style for stable backup storage.

    Args:
        path: Input path string or Path object.

    Returns:
        POSIX-style path string.

    Example:
        >>> to_posix(r"C:\\a\\b\\c.txt")
        'C:/a/b/c.txt'
    """
    return Path(path).as_posix()

def is_special_marker(node: str) -> bool:
    """
    Check if a node string is a special marker (e.g., permission denied, loop detected).

    Args:
        node: Node string from the tree.

    Returns:
        True if the node is a special marker, otherwise False.

    Example:
        >>> is_special_marker("_permission_denied_for:/x")
        True
    """
    return node.startswith(("_loop_detected", "_permission_denied", "_error_accessing"))

def iter_tree_files(tree: Mapping[str, Sequence[str | Dict[str, Any]]]) -> Iterator[Tuple[str, str]]:
    """
    Flatten a manager.return_full_tree-like structure into (_root, file_path) pairs.

    Args:
        tree: Tree mapping (root_path -> nested list of file paths and dict subtrees).

    Yields:
        Tuples of (root_path, file_path) for each file node.

    Example:
        >>> t = {"/r": ["/r/a.txt", {"/r/d": ["/r/d/b.txt"]}]}
        >>> list(iter_tree_files(t))
        [('/r', '/r/a.txt'), ('/r', '/r/d/b.txt')]
    """
    def _walk(_root: str, node: str | Dict[str, Any]) -> Iterator[Tuple[str, str]]:
        if isinstance(node, str):
            if not is_special_marker(node):
                yield _root, node
            return

        for children in node.values():
            if isinstance(children, list):
                for child in children:
                    yield from _walk(_root, child)

    for root, contents in tree.items():
        for item in contents:
            yield from _walk(root, item)

def root_prefix_id(root: str) -> str:
    """
    Create a stable identifier for a root prefix using SHA256.

    Args:
        root: Root directory path.

    Returns:
        Short hex identifier (16 chars).

    Example:
        >>> len(root_prefix_id("/any/root"))
        16
    """
    root_posix = to_posix(root)
    return hashlib.sha256(root_posix.encode("utf-8")).hexdigest()[:16]

def relative_under_root(root: str, file_path: str) -> str:
    """
    Compute a POSIX relative path under the given root, falling back to basename if needed.

    Args:
        root: Root directory path.
        file_path: Absolute file path.

    Returns:
        Relative POSIX path under root.

    Example:
        >>> relative_under_root("/r", "/r/a/b.txt")
        'a/b.txt'
    """
    try:
        root_path = Path(root).resolve()
        file_path_resolved = Path(file_path).resolve()
        return file_path_resolved.relative_to(root_path).as_posix()
    except (ValueError, RuntimeError) as e:
        logger.warning(f"Could not relativize {file_path} under {root}: {e}")
        return Path(file_path).name

def b64_encode_stream(src: Iterable[bytes], wrap: int = B64_WRAP) -> Iterator[str]:
    """
    Base64 encode a bytes stream and yield wrapped text lines.

    Args:
        src: Iterable yielding bytes.
        wrap: Line wrap length for base64 output.

    Yields:
        Base64 text lines.

    Example:
        >>> list(b64_encode_stream([b"hello"]))
        ['aGVsbG8=']
    """
    buf = b""
    for chunk in src:
        buf += chunk
        take = (len(buf) // 3) * 3
        if take:
            out = base64.b64encode(buf[:take]).decode("ascii")
            for i in range(0, len(out), wrap):
                yield out[i : i + wrap]
            buf = buf[take:]
    if buf:
        out = base64.b64encode(buf).decode("ascii")
        for i in range(0, len(out), wrap):
            yield out[i : i + wrap]

def aggregate_to_backup(
    tree: Mapping[str, Sequence[str | Dict[str, Any]]],
    output_backup_path: str | Path,
    progress_callback: Optional[callable] = None,
) -> None:
    """
    Aggregate files from a tree into a single UTF-8 backup file.

    Args:
        tree: Tree mapping as produced by manager.return_full_tree.
        output_backup_path: Path to the output backup file.
        progress_callback: Optional callback for progress updates (called with current file count).

    Raises:
        BackupError: If file operations fail.

    Example:
        >>> _tree = {"/tmp/src": ["/tmp/src/f1.bin"]}
        >>> aggregate_to_backup(_tree, "backup.txt")
    """
    output_path = Path(output_backup_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    roots_meta = {
        root_prefix_id(root): to_posix(root)
        for root in tree.keys()
    }

    file_count = 0
    try:
        with output_path.open("w", encoding="utf-8", newline="\n") as backup_file:
            # Write header
            backup_file.write(f"{_OPEN_FOLDER_DELIMITER}\n")
            backup_file.write(f"{_META_PREFIX} version={VERSION}\n")
            for rid, rposix in sorted(roots_meta.items()):
                backup_file.write(f"{_META_PREFIX} root_id={rid} root_posix={rposix}\n")

            # Process files
            for root, file_path in iter_tree_files(tree):
                if not os.path.isfile(file_path):
                    logger.warning(f"Skipping non-file: {file_path}")
                    continue

                rid = root_prefix_id(root)
                rel_path = to_posix(relative_under_root(root, file_path))
                full_path = to_posix(file_path)

                sha256 = hashlib.sha256()
                size = 0

                def read_chunks() -> Iterator[bytes]:
                    nonlocal size
                    try:
                        with open(file_path, "rb") as src_file:
                            while chunk := src_file.read(CHUNK_SIZE):
                                size += len(chunk)
                                sha256.update(chunk)
                                yield chunk
                    except OSError as _e:
                        logger.error(f"Failed to read {file_path}: {_e}")
                        raise BackupError(f"File read error: {file_path}") from _e

                # Write record
                backup_file.write(f"{_RECORD_BEGIN}\n")
                backup_file.write(
                    f"{_HEADER_PREFIX} root_id={rid} rel={rel_path} "
                    f"src_full_posix={full_path} encoding=b64\n"
                )

                for b64_line in b64_encode_stream(read_chunks()):
                    backup_file.write(f"{_PAYLOAD_PREFIX} {b64_line}\n")

                backup_file.write(
                    f"{_HEADER_PREFIX} size={size} sha256={sha256.hexdigest()}\n"
                )
                backup_file.write(f"{_RECORD_END}\n")

                file_count += 1
                if progress_callback:
                    progress_callback(file_count)

            # Write footer
            backup_file.write(f"{_CLOSE_FOLDER_DELIMITER}\n")

    except (IOError, OSError) as e:
        logger.error(f"Backup failed: {e}")
        raise BackupError(f"Backup creation error: {e}") from e

def unpack_from_backup(
    backup_file_path: str | Path,
    target_extraction_dir: str | Path,
    skip_errors: bool = False,
    progress_callback: Optional[callable] = None,
) -> None:
    """
    Unpack a backup file into a target directory with streaming and verification.

    Args:
        backup_file_path: Path to the backup file.
        target_extraction_dir: Directory to extract files into.
        skip_errors: If True, skip files with errors (e.g., checksum mismatch).
        progress_callback: Optional callback for progress updates (called with current file count).

    Raises:
        BackupError: If verification fails and `skip_errors` is False.

    Example:
        >>> unpack_from_backup("backup.txt", "restored_dir")
    """
    valid_path(str(backup_file_path), is_file=True)
    target_base = Path(target_extraction_dir)
    target_base.mkdir(parents=True, exist_ok=True)

    root_map: Dict[str, str] = {}
    file_count = 0

    # State tracking for current record
    current_out_file: Optional[Any] = None
    current_sha: Optional[Any] = None
    expected_sha: Optional[str] = None
    expected_size: int = 0
    actual_size: int = 0

    def close_current_file() -> None:
        nonlocal current_out_file, current_sha, actual_size
        if current_out_file:
            current_out_file.close()
            if expected_sha and current_sha.hexdigest() != expected_sha:
                msg = f"Checksum mismatch for file in backup!"
                if skip_errors:
                    logger.warning(msg)
                else:
                    raise BackupError(msg)
            if expected_size != actual_size:
                msg = f"Size mismatch for file in backup!"
                if skip_errors:
                    logger.warning(msg)
                else:
                    raise BackupError(msg)
        current_out_file = None
        current_sha = None

    def sanitize_root(root_posix: str) -> Path:
        """Sanitize root path for cross-platform compatibility."""
        root_clean = root_posix.lstrip("/")
        if len(root_clean) >= 2 and root_clean[1] == ":":  # Handle Windows drive
            root_clean = root_clean[0] + root_clean[2:]
        return Path(root_clean)

    try:
        with open(backup_file_path, "r", encoding="utf-8", errors="replace") as backup_file:
            for raw_line in backup_file:
                line = raw_line.strip()
                if not line:
                    continue

                # Handle Metadata
                if line.startswith(_META_PREFIX):
                    if "root_id=" in line and "root_posix=" in line:
                        parts = line[len(_META_PREFIX):].strip().split(" root_posix=")
                        rid = parts[0].split("root_id=")[1].strip()
                        root_map[rid] = parts[1].strip()
                    continue

                # Record Boundaries
                if line == _RECORD_BEGIN:
                    close_current_file()
                    continue
                if line == _RECORD_END:
                    close_current_file()
                    file_count += 1
                    if progress_callback:
                        progress_callback(file_count)
                    continue

                # Headers (File Info and Integrity)
                if line.startswith(_HEADER_PREFIX):
                    kv = dict(item.split("=", 1) for item in line[len(_HEADER_PREFIX):].strip().split() if "=" in item)

                    if "root_id" in kv and "rel" in kv:
                        root_path_str = root_map.get(kv["root_id"], f"unknown_{kv['root_id']}")
                        out_path = target_base / sanitize_root(root_path_str) / Path(kv["rel"])
                        out_path.parent.mkdir(parents=True, exist_ok=True)
                        current_out_file = open(out_path, "wb")
                        current_sha = hashlib.sha256()
                        actual_size = 0

                    if "sha256" in kv:
                        expected_sha = kv["sha256"]
                        expected_size = int(kv.get("size", 0))
                    continue

                # Payload (Streaming Decode)
                if line.startswith(_PAYLOAD_PREFIX) and current_out_file:
                    b64_data = line[len(_PAYLOAD_PREFIX):].strip()
                    chunk = base64.b64decode(b64_data)
                    current_out_file.write(chunk)
                    current_sha.update(chunk)
                    actual_size += len(chunk)

    except (IOError, OSError) as e:
        logger.error(f"Backup extraction failed: {e}")
        raise BackupError(f"Extraction error: {e}") from e
    finally:
        close_current_file()
