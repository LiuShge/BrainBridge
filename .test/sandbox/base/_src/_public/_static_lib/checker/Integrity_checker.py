from os import path

file_path = path.dirname(path.abspath(__file__))  # Get absolute path of current file
path_index = file_path.find("BrainBridge")
if path_index == -1:
    raise ValueError(f"Unexpected file path: {file_path}. Expected to contain 'src'.")
base_path = path.join(file_path[:path_index])