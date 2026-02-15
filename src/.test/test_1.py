from simple_import import change_sys_path
change_sys_path(to_runlib=True)
from files_manager.manager import return_full_tree, write_content_tofile

write_content_tofile("C:/Users/Serge/Desktop/BrainBridge/src/dir_tree.txt",str(return_full_tree("C:/Users/Serge/Desktop/BrainBridge/")),override=True)