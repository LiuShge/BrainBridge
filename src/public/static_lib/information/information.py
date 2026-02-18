from os import path, listdir

from public.run_lib.files_manager.manager import read_json
from set_source_dir import _set_source_dir,_restore_sys_path
_set_source_dir()
from simple_import import change_sys_path
change_sys_path(to_runlib=True)
from files_manager.manager import read_json
_restore_sys_path()

def display():
      file_path = path.join(path.dirname(__file__),"config")
      for f in listdir(file_path):
            print(read_json(path.join(file_path,f)),end="\n")

if __name__ == "__main__":
      display()