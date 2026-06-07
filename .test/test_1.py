import tempfile
from os import path

from brainbridge.run_lib.files_manager.manager import (
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
    assert "run_lib" in tree_snapshot
