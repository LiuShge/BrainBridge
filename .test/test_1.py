import tempfile
from os import path

from brainbridge.lib.runtime.files_manager.manager import (
    return_full_tree,
    return_path_of_dir_under_root_dir,
)

package_dir = return_path_of_dir_under_root_dir("brainbridge")

with tempfile.TemporaryDirectory() as tmpdir:
    output_path = path.join(tmpdir, "dir_tree.txt")
    tree_snapshot = str(return_full_tree(package_dir))
    with open(output_path, "w", encoding="utf-8") as file_obj:
        file_obj.write(tree_snapshot)
    assert path.exists(output_path)
    assert "lib" in tree_snapshot
    assert "utils" in tree_snapshot
    assert "run_lib" not in tree_snapshot
    assert "static_lib" not in tree_snapshot
