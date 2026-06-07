"""Aggregate files into a single portable backup and unpack it later.

This module provides functionalities to create and restore backups of directory trees.
Backup files are UTF-8 encoded and support both text and binary files via Base64 encoding.
The current `.bb` format is a line-oriented container with JSON metadata records and an
optional compact file-tree header at the top for quick inspection.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Dict, Iterable, Iterator, Mapping, Optional, Sequence, Tuple
import logging

from src.public.run_lib.files_manager.manager import valid_path

logger = logging.getLogger(__name__)

__all__ = [
    "MAGIC_START",
    "MAGIC_END",
    "TREE_BEGIN",
    "TREE_END",
    "RECORD_BEGIN",
    "RECORD_END",
    "META_PREFIX",
    "TREE_DATA_PREFIX",
    "FILE_META_PREFIX",
    "FILE_CHECK_PREFIX",
    "PAYLOAD_PREFIX",
    "VERSION",
    "TREE_HEADER_FORMAT",
    "B64_WRAP",
    "CHUNK_SIZE",
    "BackupError",
    "to_posix",
    "is_special_marker",
    "iter_tree_files",
    "root_prefix_id",
    "relative_under_root",
    "b64_encode_stream",
    "build_compact_file_tree",
    "has_file_tree_header",
    "read_file_tree_header",
    "inject_file_tree_header",
    "aggregate_to_backup",
    "unpack_from_backup",
]

MAGIC_START = "BBPACK/3"
MAGIC_END = "BBPACK_END"
TREE_BEGIN = "TREE_BEGIN"
TREE_END = "TREE_END"
RECORD_BEGIN = "FILE_BEGIN"
RECORD_END = "FILE_END"

META_PREFIX = "META "
TREE_DATA_PREFIX = "TREE_DATA "
FILE_META_PREFIX = "FILE_META "
FILE_CHECK_PREFIX = "FILE_CHECK "
PAYLOAD_PREFIX = "FILE_DATA "

VERSION = 3
TREE_HEADER_FORMAT = "compact-tree-v1"
B64_WRAP = 76
CHUNK_SIZE = 1024 * 1024


class BackupError(Exception):
    """Custom exception for backup-related errors."""


def to_posix(path: str | Path) -> str:
    """Convert a filesystem path to POSIX style for stable backup storage."""
    return Path(path).as_posix()


def is_special_marker(node: str) -> bool:
    """Check if a node string is a special marker."""
    return node.startswith(("_loop_detected", "_permission_denied", "_error_accessing"))


def iter_tree_files(tree: Mapping[str, Sequence[str | Dict[str, Any]]]) -> Iterator[Tuple[str, str]]:
    """Flatten a manager.return_full_tree-like structure into (_root, file_path) pairs."""

    def _walk(root: str, node: str | Dict[str, Any]) -> Iterator[Tuple[str, str]]:
        if isinstance(node, str):
            if not is_special_marker(node):
                yield root, node
            return

        for children in node.values():
            if isinstance(children, list):
                for child in children:
                    yield from _walk(root, child)

    for root, contents in tree.items():
        for item in contents:
            yield from _walk(root, item)


def root_prefix_id(root: str) -> str:
    """Create a stable identifier for a root prefix using SHA256."""
    root_posix = to_posix(root)
    return hashlib.sha256(root_posix.encode("utf-8")).hexdigest()[:16]


def relative_under_root(root: str, file_path: str) -> str:
    """Compute a POSIX relative path under the given root."""
    root_path = Path(root).resolve()
    file_path_resolved = Path(file_path).resolve()
    try:
        return file_path_resolved.relative_to(root_path).as_posix()
    except ValueError:
        return file_path_resolved.name


def b64_encode_stream(src: Iterable[bytes], wrap: int = B64_WRAP) -> Iterator[str]:
    """Base64 encode a bytes stream and yield wrapped text lines."""
    buf = b""
    for chunk in src:
        buf += chunk
        take = (len(buf) // 3) * 3
        if take:
            out = base64.b64encode(buf[:take]).decode("ascii")
            for i in range(0, len(out), wrap):
                yield out[i:i + wrap]
            buf = buf[take:]
    if buf:
        out = base64.b64encode(buf).decode("ascii")
        for i in range(0, len(out), wrap):
            yield out[i:i + wrap]


def build_compact_file_tree(tree: Mapping[str, Sequence[str | Dict[str, Any]]]) -> Dict[str, Any]:
    """Build a concise relative-path file tree header for a backup."""

    def _compact_marker(root: str, marker: str) -> str:
        if ":" not in marker:
            return marker
        prefix, raw_path = marker.split(":", 1)
        if not raw_path:
            return marker
        return f"{prefix}:{relative_under_root(root, raw_path)}"

    def _compact_nodes(root: str, nodes: Sequence[str | Dict[str, Any]], counts: Dict[str, int]) -> list[Any]:
        compact_nodes: list[Any] = []
        for node in nodes:
            if isinstance(node, str):
                if is_special_marker(node):
                    counts["marker_count"] += 1
                    compact_nodes.append(_compact_marker(root, node))
                else:
                    counts["file_count"] += 1
                    compact_nodes.append(relative_under_root(root, node))
                continue

            for dir_path, children in node.items():
                compact_nodes.append({
                    relative_under_root(root, dir_path): _compact_nodes(root, children, counts)
                })
        return compact_nodes

    roots: list[Dict[str, Any]] = []
    total_file_count = 0

    for root, contents in tree.items():
        counts = {"file_count": 0, "marker_count": 0}
        compact_tree = _compact_nodes(root, contents, counts)
        total_file_count += counts["file_count"]
        roots.append({
            "root_id": root_prefix_id(root),
            "root_posix": to_posix(root),
            "file_count": counts["file_count"],
            "marker_count": counts["marker_count"],
            "tree": compact_tree,
        })

    return {
        "format": TREE_HEADER_FORMAT,
        "version": 1,
        "total_file_count": total_file_count,
        "roots": roots,
    }


def has_file_tree_header(backup_file_path: str | Path) -> bool:
    """Return True if the backup contains an embedded file-tree header."""
    scan = _scan_backup_structure(backup_file_path, decode_tree=False, collect_records=False)
    return scan["tree_meta"] is not None


def read_file_tree_header(backup_file_path: str | Path, validate: bool = False) -> Optional[Dict[str, Any]]:
    """Read the embedded file-tree header from a backup."""
    scan = _scan_backup_structure(backup_file_path, decode_tree=True, collect_records=validate)
    tree_header = scan["tree_header"]
    if tree_header is None:
        return None
    if validate:
        _validate_tree_header_against_records(tree_header, scan["records"])
    return tree_header


def inject_file_tree_header(
    backup_file_path: str | Path,
    tree: Mapping[str, Sequence[str | Dict[str, Any]]],
    validate: bool = True,
) -> None:
    """Insert or replace the top-level file-tree header in an existing `.bb` backup."""
    backup_path = Path(backup_file_path)
    valid_path(str(backup_path), is_file=True)

    header_payload = build_compact_file_tree(tree)
    if validate:
        scan = _scan_backup_structure(backup_path, decode_tree=False, collect_records=True)
        _validate_tree_header_against_records(header_payload, scan["records"])

    tree_lines = _build_tree_header_lines(header_payload)
    temp_file = tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        newline="\n",
        delete=False,
        dir=str(backup_path.parent),
        prefix=f"{backup_path.name}.",
        suffix=".tmp",
    )

    inserted = False
    skipping_tree_block = False

    try:
        with backup_path.open("r", encoding="utf-8", errors="replace") as src, temp_file as dst:
            for raw_line in src:
                stripped = raw_line.rstrip("\n")

                if skipping_tree_block:
                    if stripped == TREE_END:
                        skipping_tree_block = False
                    continue

                if stripped.startswith(META_PREFIX):
                    payload = _parse_json_payload(stripped, META_PREFIX)
                    if payload.get("kind") == "tree_header":
                        continue
                    dst.write(raw_line)
                    continue

                if stripped == TREE_BEGIN:
                    skipping_tree_block = True
                    continue

                if not inserted and stripped in {RECORD_BEGIN, MAGIC_END}:
                    for header_line in tree_lines:
                        dst.write(header_line)
                    inserted = True

                dst.write(raw_line)

        os.replace(temp_file.name, backup_path)
    except Exception:
        try:
            os.unlink(temp_file.name)
        except OSError:
            pass
        raise


def aggregate_to_backup(
    tree: Mapping[str, Sequence[str | Dict[str, Any]]],
    output_backup_path: str | Path,
    progress_callback: Optional[Callable[[int], None]] = None,
    include_file_tree_header: bool = False,
    validate_file_tree_header: bool = True,
) -> None:
    """Aggregate files from a tree into a single UTF-8 `.bb` backup file."""
    output_path = Path(output_backup_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    roots_meta = {
        root_prefix_id(root): to_posix(root)
        for root in tree.keys()
    }

    tree_header: Optional[Dict[str, Any]] = None
    if include_file_tree_header:
        tree_header = build_compact_file_tree(tree)
        if validate_file_tree_header:
            expected_records = [
                {
                    "root_id": root_prefix_id(root),
                    "rel": relative_under_root(root, file_path),
                }
                for root, file_path in iter_tree_files(tree)
                if os.path.isfile(file_path)
            ]
            _validate_tree_header_against_records(tree_header, expected_records)

    file_count = 0
    with output_path.open("w", encoding="utf-8", newline="\n") as backup_file:
        backup_file.write(f"{MAGIC_START}\n")
        _write_json_line(
            backup_file,
            META_PREFIX,
            {"kind": "backup", "version": VERSION, "b64_wrap": B64_WRAP, "chunk_size": CHUNK_SIZE},
        )
        for rid, rposix in sorted(roots_meta.items()):
            _write_json_line(
                backup_file,
                META_PREFIX,
                {"kind": "root", "root_id": rid, "root_posix": rposix},
            )

        if tree_header is not None:
            for header_line in _build_tree_header_lines(tree_header):
                backup_file.write(header_line)

        for root, file_path in iter_tree_files(tree):
            if not os.path.isfile(file_path):
                logger.warning("Skipping non-file node: %s", file_path)
                continue

            rid = root_prefix_id(root)
            rel_path = relative_under_root(root, file_path)
            full_path = to_posix(file_path)
            sha256 = hashlib.sha256()
            size = 0

            def read_chunks() -> Iterator[bytes]:
                nonlocal size
                with open(file_path, "rb") as src_file:
                    while True:
                        chunk = src_file.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        size += len(chunk)
                        sha256.update(chunk)
                        yield chunk

            backup_file.write(f"{RECORD_BEGIN}\n")
            _write_json_line(
                backup_file,
                FILE_META_PREFIX,
                {
                    "root_id": rid,
                    "rel": rel_path,
                    "src_full_posix": full_path,
                    "encoding": "b64",
                },
            )

            for b64_line in b64_encode_stream(read_chunks()):
                backup_file.write(f"{PAYLOAD_PREFIX}{b64_line}\n")

            _write_json_line(
                backup_file,
                FILE_CHECK_PREFIX,
                {"size": size, "sha256": sha256.hexdigest()},
            )
            backup_file.write(f"{RECORD_END}\n")

            file_count += 1
            if progress_callback:
                progress_callback(file_count)

        backup_file.write(f"{MAGIC_END}\n")


def unpack_from_backup(
    backup_file_path: str | Path,
    target_extraction_dir: str | Path,
    skip_errors: bool = False,
    progress_callback: Optional[Callable[[int], None]] = None,
) -> None:
    """Unpack a backup file into a target directory with streaming and verification."""
    valid_path(str(backup_file_path), is_file=True)
    target_base = Path(target_extraction_dir)
    target_base.mkdir(parents=True, exist_ok=True)

    root_map: Dict[str, str] = {}
    file_count = 0

    current_meta: Optional[Dict[str, Any]] = None
    current_check: Optional[Dict[str, Any]] = None
    current_out_file: Optional[Any] = None
    current_sha: Optional[hashlib._Hash] = None
    current_size = 0
    inside_tree = False

    def _handle_record_error(message: str) -> None:
        if skip_errors:
            logger.warning(message)
            return
        raise BackupError(message)

    def _close_current_file(verify: bool = True) -> None:
        nonlocal current_meta, current_check, current_out_file, current_sha, current_size

        if current_out_file is not None:
            current_out_file.close()

        if verify and current_meta is not None and current_check is not None and current_sha is not None:
            expected_sha = str(current_check["sha256"])
            expected_size = int(current_check["size"])
            if current_sha.hexdigest() != expected_sha:
                _handle_record_error(f"Checksum mismatch for {current_meta['rel']}")
            if current_size != expected_size:
                _handle_record_error(f"Size mismatch for {current_meta['rel']}")

        current_meta = None
        current_check = None
        current_out_file = None
        current_sha = None
        current_size = 0

    with open(backup_file_path, "r", encoding="utf-8", errors="replace") as backup_file:
        first_line = backup_file.readline().strip()
        if first_line != MAGIC_START:
            raise BackupError(f"Unsupported backup format marker: {first_line!r}")

        for raw_line in backup_file:
            line = raw_line.rstrip("\n")
            if not line:
                continue

            if inside_tree:
                if line == TREE_END:
                    inside_tree = False
                continue

            if line.startswith(META_PREFIX):
                meta = _parse_json_payload(line, META_PREFIX)
                if meta.get("kind") == "root":
                    root_map[str(meta["root_id"])] = str(meta["root_posix"])
                continue

            if line == TREE_BEGIN:
                inside_tree = True
                continue

            if line == RECORD_BEGIN:
                _close_current_file(verify=False)
                continue

            if line.startswith(FILE_META_PREFIX):
                current_meta = _parse_json_payload(line, FILE_META_PREFIX)
                current_check = None
                current_sha = hashlib.sha256()
                current_size = 0

                root_id = str(current_meta["root_id"])
                root_posix = root_map.get(root_id)
                if root_posix is None:
                    raise BackupError(f"Unknown root_id in backup record: {root_id}")

                out_path = _build_output_path(target_base, root_posix, str(current_meta["rel"]))
                out_path.parent.mkdir(parents=True, exist_ok=True)
                current_out_file = open(out_path, "wb")
                continue

            if line.startswith(PAYLOAD_PREFIX):
                if current_out_file is None or current_sha is None:
                    raise BackupError("Encountered payload without an open file record.")
                b64_data = line[len(PAYLOAD_PREFIX):]
                chunk = base64.b64decode(b64_data, validate=True)
                current_out_file.write(chunk)
                current_sha.update(chunk)
                current_size += len(chunk)
                continue

            if line.startswith(FILE_CHECK_PREFIX):
                current_check = _parse_json_payload(line, FILE_CHECK_PREFIX)
                continue

            if line == RECORD_END:
                _close_current_file(verify=True)
                file_count += 1
                if progress_callback:
                    progress_callback(file_count)
                continue

            if line == MAGIC_END:
                _close_current_file(verify=False)
                return

            raise BackupError(f"Unexpected backup line: {line}")

    raise BackupError("Backup ended without BBPACK_END marker.")


def _write_json_line(handle: Any, prefix: str, payload: Mapping[str, Any]) -> None:
    handle.write(f"{prefix}{json.dumps(payload, ensure_ascii=False, separators=(',', ':'))}\n")


def _parse_json_payload(line: str, prefix: str) -> Dict[str, Any]:
    if not line.startswith(prefix):
        raise BackupError(f"Expected prefix {prefix!r}, got: {line!r}")
    try:
        payload = json.loads(line[len(prefix):])
    except json.JSONDecodeError as exc:
        raise BackupError(f"Invalid JSON metadata line: {line!r}") from exc
    if not isinstance(payload, dict):
        raise BackupError(f"Expected dict metadata payload, got: {type(payload).__name__}")
    return payload


def _build_tree_header_lines(tree_header: Mapping[str, Any]) -> list[str]:
    tree_bytes = json.dumps(tree_header, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    tree_sha256 = hashlib.sha256(tree_bytes).hexdigest()
    tree_data_lines = list(b64_encode_stream([tree_bytes]))

    lines = [
        f"{META_PREFIX}{json.dumps({'kind': 'tree_header', 'format': TREE_HEADER_FORMAT, 'line_count': len(tree_data_lines), 'sha256': tree_sha256}, ensure_ascii=False, separators=(',', ':'))}\n",
        f"{TREE_BEGIN}\n",
    ]
    lines.extend(f"{TREE_DATA_PREFIX}{tree_line}\n" for tree_line in tree_data_lines)
    lines.append(f"{TREE_END}\n")
    return lines


def _scan_backup_structure(
    backup_file_path: str | Path,
    *,
    decode_tree: bool,
    collect_records: bool,
) -> Dict[str, Any]:
    valid_path(str(backup_file_path), is_file=True)
    roots: Dict[str, str] = {}
    tree_meta: Optional[Dict[str, Any]] = None
    tree_lines: list[str] = []
    tree_header: Optional[Dict[str, Any]] = None
    records: list[Dict[str, Any]] = []
    current_record_meta: Optional[Dict[str, Any]] = None
    inside_tree = False
    saw_end = False

    with open(backup_file_path, "r", encoding="utf-8", errors="replace") as backup_file:
        first_line = backup_file.readline().strip()
        if first_line != MAGIC_START:
            raise BackupError(f"Unsupported backup format marker: {first_line!r}")

        for raw_line in backup_file:
            line = raw_line.rstrip("\n")
            if not line:
                continue

            if inside_tree:
                if line == TREE_END:
                    inside_tree = False
                    continue
                if line.startswith(TREE_DATA_PREFIX):
                    if decode_tree:
                        tree_lines.append(line[len(TREE_DATA_PREFIX):])
                    continue
                raise BackupError(f"Unexpected tree header line: {line}")

            if line.startswith(META_PREFIX):
                meta = _parse_json_payload(line, META_PREFIX)
                if meta.get("kind") == "root":
                    roots[str(meta["root_id"])] = str(meta["root_posix"])
                elif meta.get("kind") == "tree_header":
                    tree_meta = meta
                continue

            if line == TREE_BEGIN:
                inside_tree = True
                continue

            if line == RECORD_BEGIN:
                current_record_meta = None
                continue

            if line.startswith(FILE_META_PREFIX):
                current_record_meta = _parse_json_payload(line, FILE_META_PREFIX)
                continue

            if line == RECORD_END:
                if collect_records and current_record_meta is not None:
                    records.append(current_record_meta)
                current_record_meta = None
                continue

            if line == MAGIC_END:
                saw_end = True
                break

        if not saw_end:
            raise BackupError("Backup ended without BBPACK_END marker.")

    if decode_tree and tree_meta is not None:
        tree_bytes = base64.b64decode("".join(tree_lines), validate=True)
        tree_sha256 = hashlib.sha256(tree_bytes).hexdigest()
        if tree_sha256 != str(tree_meta["sha256"]):
            raise BackupError("Embedded tree header checksum mismatch.")
        if int(tree_meta["line_count"]) != len(tree_lines):
            raise BackupError("Embedded tree header line count mismatch.")
        tree_header = json.loads(tree_bytes.decode("utf-8"))

    return {
        "roots": roots,
        "tree_meta": tree_meta,
        "tree_header": tree_header,
        "records": records,
    }


def _flatten_tree_header_files(tree_header: Mapping[str, Any]) -> list[Dict[str, str]]:
    flattened: list[Dict[str, str]] = []

    def _walk(root_id: str, nodes: Sequence[Any]) -> None:
        for node in nodes:
            if isinstance(node, str):
                if not is_special_marker(node):
                    flattened.append({"root_id": root_id, "rel": node})
                continue
            if isinstance(node, dict):
                for children in node.values():
                    if isinstance(children, list):
                        _walk(root_id, children)

    for root_entry in tree_header.get("roots", []):
        root_id = str(root_entry["root_id"])
        _walk(root_id, root_entry.get("tree", []))

    return flattened


def _validate_tree_header_against_records(
    tree_header: Mapping[str, Any],
    records: Sequence[Mapping[str, Any]],
) -> None:
    tree_files = {
        (str(item["root_id"]), str(item["rel"]))
        for item in _flatten_tree_header_files(tree_header)
    }
    record_files = {
        (str(item["root_id"]), str(item["rel"]))
        for item in records
    }

    missing = sorted(record_files - tree_files)
    extra = sorted(tree_files - record_files)
    if missing or extra:
        raise BackupError(
            f"Embedded tree header does not match backup records. "
            f"missing={len(missing)} extra={len(extra)}"
        )


def _sanitize_root(root_posix: str) -> Path:
    root_clean = root_posix.replace(":", "").lstrip("/\\")
    return Path(root_clean)


def _build_output_path(target_base: Path, root_posix: str, rel_path: str) -> Path:
    rel = PurePosixPath(rel_path)
    if rel.is_absolute() or ".." in rel.parts:
        raise BackupError(f"Unsafe relative path in backup: {rel_path}")

    root_base = (target_base / _sanitize_root(root_posix)).resolve()
    out_path = (root_base / Path(*rel.parts)).resolve()
    if os.path.commonpath([str(root_base), str(out_path)]) != str(root_base):
        raise BackupError(f"Backup extraction escaped target root: {rel_path}")
    return out_path
