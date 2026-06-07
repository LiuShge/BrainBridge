import tempfile
from pathlib import Path

from src.public.run_lib.files_manager.manager import read_file, return_full_tree
from src.public.run_lib.mini_tools.files_convg import (
    aggregate_to_backup,
    has_file_tree_header,
    inject_file_tree_header,
    read_file_tree_header,
    unpack_from_backup,
)


with tempfile.TemporaryDirectory() as tmpdir:
    tmp_path = Path(tmpdir)
    source_root = tmp_path / "source tree"
    nested_dir = source_root / "nested folder"
    nested_dir.mkdir(parents=True)

    text_file = source_root / "alpha file.txt"
    binary_file = nested_dir / "beta.bin"

    text_file.write_text("hello tree header", encoding="utf-8")
    binary_file.write_bytes(b"\x00\x01\x02\x03")

    tree = return_full_tree(str(source_root))

    backup_with_header = tmp_path / "with-header.bb"
    aggregate_to_backup(tree, backup_with_header, include_file_tree_header=True)
    assert has_file_tree_header(backup_with_header) is True

    tree_header = read_file_tree_header(backup_with_header, validate=True)
    assert tree_header is not None
    assert tree_header["total_file_count"] == 2

    restore_dir = tmp_path / "restored"
    unpack_from_backup(backup_with_header, restore_dir)

    restored_text = next(restore_dir.rglob("alpha file.txt"))
    restored_binary = next(restore_dir.rglob("beta.bin"))
    assert read_file(str(restored_text)) == "hello tree header"
    assert restored_binary.read_bytes() == b"\x00\x01\x02\x03"

    backup_without_header = tmp_path / "without-header.bb"
    aggregate_to_backup(tree, backup_without_header, include_file_tree_header=False)
    assert has_file_tree_header(backup_without_header) is False

    inject_file_tree_header(backup_without_header, tree, validate=True)
    assert has_file_tree_header(backup_without_header) is True
    assert read_file_tree_header(backup_without_header, validate=True) is not None
