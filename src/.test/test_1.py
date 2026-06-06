from os import path

from bootstrap_paths import change_sys_path
change_sys_path(to_runlib=True)
from files_manager.manager import (
    return_full_tree,
    write_content_tofile,
    return_path_of_dir_under_root_dir,
)

src_dir = return_path_of_dir_under_root_dir("src")
write_content_tofile(
    path.join(src_dir, "dir_tree.txt"),
    str(return_full_tree(src_dir)),
    override=True,
)
