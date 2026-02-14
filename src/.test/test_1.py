from simple_import import change_sys_path
change_sys_path(to_runlib=True)
from files_manager.manager import return_full_tree
with open("C:/Users/Serge/Desktop/BrainBridge/dir_tree.txt","w",encoding="utf-8") as f:
    f.write(str(return_full_tree("C:/Users/Serge/Desktop/BrainBridge/")))