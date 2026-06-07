from os import path, listdir

from brainbridge.run_lib.files_manager.manager import read_json

__all__ = ["display"]

def display():
    file_path = path.join(path.dirname(__file__), "config")
    for file_name in listdir(file_path):
        print(read_json(path.join(file_path, file_name)), end="\n")

if __name__ == "__main__":
    display()
