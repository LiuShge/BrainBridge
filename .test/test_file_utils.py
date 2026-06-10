import tempfile
from pathlib import Path

from brainbridge.lib.runtime.file_utils import (
    aggregate_to_backup,
    has_file_tree_header,
    inject_file_tree_header,
    normalize_ignores,
    read_file_tree_header,
    return_full_tree,
    unpack_from_backup,
)


def _make_tree(root: Path) -> None:
    nested = root / "nested"
    nested.mkdir(parents=True)
    hidden_dir = root / ".git"
    hidden_dir.mkdir()
    cache_dir = root / "__pycache__"
    cache_dir.mkdir()

    (root / "keep.txt").write_text("keep", encoding="utf-8")
    (nested / "keep2.txt").write_text("keep2", encoding="utf-8")
    (root / "drop.pyc").write_text("drop pyc", encoding="utf-8")
    (root / "drop.log").write_text("drop log", encoding="utf-8")
    (hidden_dir / "ignored.txt").write_text("ignored", encoding="utf-8")
    (cache_dir / "ignored.pyc").write_text("ignored pyc", encoding="utf-8")


def test_normalize_ignores_variants() -> None:
    assert normalize_ignores(None) == {"dir": [], "file": []}
    assert normalize_ignores(".pyc") == {"dir": [], "file": [".pyc"]}
    assert normalize_ignores([".pyc", ".log"]) == {"dir": [], "file": [".pyc", ".log"]}
    assert normalize_ignores({"dir": [".git"], "file": [".pyc"]}) == {"dir": [".git"], "file": [".pyc"]}
    assert normalize_ignores({"dir": [".git"]}) == {"dir": [".git"], "file": []}
    assert normalize_ignores({"file": [".pyc"]}) == {"dir": [], "file": [".pyc"]}

    try:
        normalize_ignores({"bad": [".pyc"]})
    except ValueError:
        pass
    else:
        raise AssertionError("unexpected success for unsupported ignore key")

    try:
        normalize_ignores({"file": [".pyc", 1]})
    except TypeError:
        pass
    else:
        raise AssertionError("unexpected success for non-str ignore word")


def test_return_full_tree_ignores() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir) / "source"
        _make_tree(root)

        baseline = str(return_full_tree(str(root)))
        assert "keep.txt" in baseline
        assert "drop.pyc" in baseline
        assert "drop.log" in baseline
        assert ".git" in baseline
        assert "__pycache__" in baseline

        file_ignored = str(return_full_tree(str(root), ignores=".pyc"))
        assert "drop.pyc" not in file_ignored
        assert "drop.log" in file_ignored
        assert ".git" in file_ignored
        assert "__pycache__" in file_ignored

        list_ignored = str(return_full_tree(str(root), ignores=[".pyc", ".log"]))
        assert "drop.pyc" not in list_ignored
        assert "drop.log" not in list_ignored
        assert ".git" in list_ignored
        assert "__pycache__" in list_ignored

        dir_and_file_ignored = str(
            return_full_tree(
                str(root),
                ignores={"dir": [".git", "__pycache__"], "file": [".pyc"]},
            )
        )
        assert ".git" not in dir_and_file_ignored
        assert "__pycache__" not in dir_and_file_ignored
        assert "drop.pyc" not in dir_and_file_ignored
        assert "drop.log" in dir_and_file_ignored
        assert "keep.txt" in dir_and_file_ignored
        assert "keep2.txt" in dir_and_file_ignored


def test_bb_ignores_and_header_consistency() -> None:
    ignores = {"dir": [".git", "__pycache__"], "file": [".pyc", ".log"]}

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        root = tmp_path / "source"
        _make_tree(root)
        tree = return_full_tree(str(root))

        backup_with_header = tmp_path / "with-header.bb"
        aggregate_to_backup(tree, backup_with_header, include_file_tree_header=True, ignores=ignores)
        assert has_file_tree_header(backup_with_header) is True

        tree_header = read_file_tree_header(backup_with_header, validate=True)
        assert tree_header is not None
        assert tree_header["total_file_count"] == 2
        header_text = str(tree_header)
        assert "drop.pyc" not in header_text
        assert "drop.log" not in header_text
        assert ".git" not in header_text
        assert "__pycache__" not in header_text

        restore_dir = tmp_path / "restored"
        unpack_from_backup(backup_with_header, restore_dir)
        assert any(p.name == "keep.txt" for p in restore_dir.rglob("keep.txt"))
        assert any(p.name == "keep2.txt" for p in restore_dir.rglob("keep2.txt"))
        assert not list(restore_dir.rglob("*.pyc"))
        assert not list(restore_dir.rglob("*.log"))
        assert not any(p.name == ".git" for p in restore_dir.rglob("*"))
        assert not any(p.name == "__pycache__" for p in restore_dir.rglob("*"))

        backup_without_header = tmp_path / "without-header.bb"
        aggregate_to_backup(tree, backup_without_header, include_file_tree_header=False, ignores=ignores)
        assert has_file_tree_header(backup_without_header) is False

        inject_file_tree_header(backup_without_header, tree, validate=True, ignores=ignores)
        assert has_file_tree_header(backup_without_header) is True
        injected_header = read_file_tree_header(backup_without_header, validate=True)
        assert injected_header is not None
        assert injected_header["total_file_count"] == 2
