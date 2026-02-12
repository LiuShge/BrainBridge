from os import path, listdir
from typing import Dict, Literal, List, Union, Any, Set
from json import loads, JSONDecodeError
from chardet import detect


def return_path_of_dir_under_root_dir(dir_name: str) -> str:
    """
    Returns the absolute path of a specified directory located directly under the project's root directory.
    The project root is determined by searching for the 'src' directory in the current file's path.

    :param dir_name: The name of the directory to locate under the project root.
    :return: The absolute path of the specified directory.
    :raises ValueError: If 'src' is not found in the current file's path,
                        if the specified `dir_name` is not found under the root,
                        or if `dir_name` is not a directory.
    Example:
    >>> import tempfile, os
    >>> # Mock a project structure for testing
    >>> with tempfile.TemporaryDirectory() as tmpdir:
    ...     mock_root = os.path.join(tmpdir, "BrainBridge")
    ...     mock_src = os.path.join(mock_root, "src")
    ...     mock_target_dir = os.path.join(mock_root, "config")
    ...     os.makedirs(mock_src)
    ...     os.makedirs(mock_target_dir)
    ...     # Temporarily change __file__ for testing
    ...     original_file = __file__
    ...     global __file__
    ...     __file__ = os.path.join(mock_src, "some_module", "manager.py")
    ...     try:
    ...         result = return_path_of_dir_under_root_dir("config")
    ...         print(result == mock_target_dir)
    ...     finally:
    ...         __file__ = original_file # Restore original __file__
    True
    """
    _unparse_path = path.dirname(__file__)
    _src_index = _unparse_path.find("src")
    if _src_index == -1:
        raise ValueError(
            f"Unexpected file path: {_unparse_path}. Expected to contain 'src', try to put this file under dir-\"src\"")
    _base_path = str(_unparse_path[:_src_index])
    if dir_name not in listdir(_base_path):
        raise ValueError(
            f"Cannot find \"{dir_name}\" under root directory: \"BrainBridge\", found: {listdir(_base_path)}.")
    if not path.isdir(path.join(_base_path, dir_name)):
        raise ValueError(f"{dir_name} under dir-\"BrainBridge\" is not a directory.")
    return path.join(_base_path, dir_name)

def return_dir_member(dir_path: str) -> Union[Dict[str, Literal['file', 'dir']], None]:
    """
    Returns a dictionary of members (files and subdirectories) within a given directory.
    If the provided path is a file, returns None.

    :param dir_path: The path to the directory to inspect.
    :return: A dictionary where keys are member names and values are 'file' or 'dir',
             or None if `dir_path` points to a file.
    :raises ValueError: If `dir_path` is an invalid or non-existent path.
    Example:
    >>> import tempfile, os
    >>> with tempfile.TemporaryDirectory() as tmpdir:
    ...     subdir = os.path.join(tmpdir, "subdir")
    ...     file1 = os.path.join(tmpdir, "file1.txt")
    ...     os.makedirs(subdir)
    ...     with open(file1, "w") as f: pass
    ...     members = return_dir_member(tmpdir)
    ...     print(members == {'subdir': 'dir', 'file1.txt': 'file'})
    True
    >>> print(return_dir_member(file1) is None)
    True
    >>> try:
    ...     return_dir_member("/non_existent_path")
    ... except ValueError as e:
    ...     print(e)
    Invalid path: /non_existent_path
    """
    if not path.isfile(dir_path) and not path.isdir(dir_path):
        raise ValueError(f"Invalid path: {dir_path}")
    elif path.isfile(dir_path):
        return None
    _member_list = {}
    for _m in listdir(dir_path):
        _member_list[_m] = 'file' if path.isfile(path.join(dir_path, _m)) else 'dir'
    return _member_list


def _valid_path(target_path: str, is_file: bool = True) -> None:
    """
    Validates if a given path exists and is either a file or a directory.

    :param target_path: The path to validate.
    :param is_file: If True, validates if the path is a file. If False, validates if it's a directory.
    :raises ValueError: If the path is invalid or does not match the expected type.
    Example:
    >>> import tempfile
    >>> with tempfile.NamedTemporaryFile() as tmp_file:
    ...     _valid_path(tmp_file.name, is_file=True)
    >>> try:
    ...     _valid_path("/non_existent_path", is_file=True)
    ... except ValueError as e:
    ...     print(e)
    Invalid path: /non_existent_path
    """
    if not path.exists(target_path):
        raise ValueError(f"Invalid path: {target_path}")
    if is_file and not path.isfile(target_path):
        raise ValueError(f"Path is not a file: {target_path}")
    if not is_file and not path.isdir(target_path):
        raise ValueError(f"Path is not a directory: {target_path}")


def return_full_free(*base_paths: str) -> Dict[str, List[Union[str, Dict[str, List[Any]]]]]:
    """
    Recursively traverses one or more base directories and returns a flattened list
    of their full file and directory paths. Directories are represented as
    dictionaries with an empty list value. Handles symbolic links to prevent
    infinite loops.

    :param base_paths: One or more root directory paths to start the traversal from.
    :return: A dictionary where keys are the base paths, and values are lists
             containing strings (for files) or dictionaries (for directories with empty lists).
    :raises ValueError: If any of the base_paths are invalid or not directories.

    Example:
    >>> import tempfile, os, shutil
    >>> with tempfile.TemporaryDirectory() as tmpdir:
    ...     dir1_path = os.path.join(tmpdir, "dir1")
    ...     subdir1_path = os.path.join(dir1_path, "subdir1")
    ...     file1_path = os.path.join(dir1_path, "file1.txt")
    ...     file2_path = os.path.join(subdir1_path, "file2.txt")
    ...     os.makedirs(subdir1_path)
    ...     with open(file1_path, "w") as f: f.write("content")
    ...     with open(file2_path, "w") as f: f.write("content")
    ...     tree = return_full_free(dir1_path)
    ...     # Expected output will be a flat list containing dir1_path, file1_path, subdir1_path, file2_path
    ...     expected_items = {dir1_path, file1_path, subdir1_path, file2_path}
    ...     # Note: The order in the list might vary based on os.listdir() and set behavior
    ...     returned_set = set()
    ...     for item in tree[dir1_path]:
    ...         if isinstance(item, dict):
    ...             for k in item:
    ...                 returned_set.add(k)
    ...         else:
    ...             returned_set.add(item)
    ...     print(returned_set == expected_items)
    True

    >>> # Example with a symbolic link loop
    >>> with tempfile.TemporaryDirectory() as temp_root:
    ...     dir_a = os.path.join(temp_root, "dir_a")
    ...     dir_b = os.path.join(temp_root, "dir_b")
    ...     link_path = os.path.join(dir_b, "link_to_dir_a")
    ...     os.makedirs(dir_a, exist_ok=True)
    ...     os.makedirs(dir_b, exist_ok=True)
    ...     # Create a file in dir_a to make it non-empty
    ...     with open(os.path.join(dir_a, "test_file_in_a.txt"), "w") as f: f.write("content")
    ...     os.symlink(os.path.join("..", "dir_a"), link_path, target_is_directory=True)
    ...     loop_tree = return_full_free(temp_root)
    ...     # Check if the symlink_to_dir_a is present as a directory marker
    ...     # And that dir_a is also present, but link_to_dir_a's contents are not re-traversed.
    ...     all_paths_in_output = set()
    ...     for item in loop_tree[temp_root]:
    ...         if isinstance(item, dict):
    ...             for k in item:
    ...                 all_paths_in_output.add(k)
    ...         else:
    ...             all_paths_in_output.add(item)
    ...     # Expecting temp_root, dir_a, dir_b, link_path (as dir), test_file_in_a.txt
    ...     expected_paths = {temp_root, dir_a, dir_b, link_path, os.path.join(dir_a, "test_file_in_a.txt")}
    ...     print(all_paths_in_output == expected_paths)
    True
    """
    result_tree: Dict[str, List[Union[str, Dict[str, List[Any]]]]] = {}

    for base_path_str in base_paths:
        _valid_path(base_path_str, is_file=False)

        current_base_path_list: List[Union[str, Dict[str, List[Any]]]] = []
        result_tree[base_path_str] = current_base_path_list

        # Use a queue for breadth-first traversal
        directories_to_explore: List[str] = []
        visited_real_paths: Set[str] = set()

        # Add the base path itself to the list as a directory marker
        current_base_path_list.append({base_path_str: []})

        # Add the real path of the base directory to visited set
        visited_real_paths.add(path.realpath(base_path_str))

        # Start exploration from the base path
        directories_to_explore.append(base_path_str)

        while directories_to_explore:
            current_directory = directories_to_explore.pop(0)  # BFS: pop from left

            try:
                for item_name in listdir(current_directory):
                    item_full_path = path.join(current_directory, item_name)
                    item_real_path = path.realpath(item_full_path)

                    if path.isdir(item_full_path):
                        # Always add the directory (or symlink to dir) to the result list
                        current_base_path_list.append({item_full_path: []})

                        # Only add to queue for exploration if its real path hasn't been visited
                        if item_real_path not in visited_real_paths:
                            visited_real_paths.add(item_real_path)
                            directories_to_explore.append(item_full_path)
                    elif path.isfile(item_full_path):
                        # Add to the result list as a file path
                        current_base_path_list.append(item_full_path)
                    # Other file system objects (like symlinks to files, pipes, sockets) are ignored for this output format
            except PermissionError:
                current_base_path_list.append(f"_permission_denied_for:{current_directory}")
            except OSError as e:
                current_base_path_list.append(f"_error_accessing:{current_directory}:{e}")

    return result_tree

def _auto_file_code(file_path: str) -> str:
    """
    Detects the encoding of a given file.

    :param file_path: The path to the file.
    :return: A string representing the detected file encoding (e.g., 'utf-8').
    Example:
    >>> import tempfile, os
    >>> with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
    ...     tmp_file.write("你好世界".encode("utf-8"))
    ...     tmp_file_path = tmp_file.name
    12
    >>> encoding = _auto_file_code(tmp_file_path)
    >>> print(encoding.lower())
    utf-8
    >>> os.remove(tmp_file_path)
    """
    with open(file_path, 'rb') as f:
        return detect(f.read())['encoding']

def write_content_tofile(file_path: str, content:str, file_code: Literal['utf-8', 'auto'] = 'utf-8', trailing_newline: bool = True, override: bool = False) -> None:
    """
    Writes content to a specified file.

    :param file_path: The path to the file to write to.
    :param content: The string content to write.
    :param file_code: The encoding to use ('utf-8' or 'auto' to detect existing encoding).
    :param trailing_newline: If True, appends a newline character at the end of the content.
    :param override: If True, overwrites the file; otherwise, appends to it.
    :raises ValueError: If `file_path` is invalid or points to a directory.
    Example:
    >>> import tempfile, os
    >>> with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
    ...     tmp_file_path = tmp_file.name
    >>> write_content_tofile(tmp_file_path, "First line", override=True)
    >>> with open(tmp_file_path, 'r') as _f: print(_f.read().strip())
    First line
    >>> write_content_tofile(tmp_file_path, "Second line", override=False, trailing_newline=False)
    >>> with open(tmp_file_path, 'r') as _f: print(_f.read().strip())
    First line
    Second line
    >>> os.remove(tmp_file_path)
    """
    _valid_path(file_path)
    if file_code == 'auto':
            file_code = _auto_file_code(file_path)
    with open(file_path, 'a' if not override else 'w', encoding=file_code) as f:
        f.write(content)
        if trailing_newline:
            f.write('\n')

def read_file(file_path: str, line_by_line: bool = False, file_code: Literal['utf-8', 'auto'] = 'utf-8') -> Union[str, List[str]]:
    """
    Reads content from a specified file.

    :param file_path: The path to the file to read from.
    :param line_by_line: If True, returns a list of strings (each line). If False, returns the entire content as a single string.
    :param file_code: The encoding to use ('utf-8' or 'auto' to detect existing encoding).
    :return: A string or a list of strings containing the file's content.
    :raises ValueError: If `file_path` is invalid or points to a directory.
    Example:
    >>> import tempfile, os
    >>> with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
    ...     tmp_file.write("Line 1\\nLine 2\\nLine 3")
    ...     tmp_file_path = tmp_file.name
    20
    >>> content_single = read_file(tmp_file_path)
    >>> print(content_single.strip())
    Line 1
    Line 2
    Line 3
    >>> os.remove(tmp_file_path)
    """
    _valid_path(file_path)
    if file_code == 'auto':
        file_code = _auto_file_code(file_path)
    with open(file_path, 'r', encoding=file_code) as f:
        if line_by_line:
            _all = []
            for line in f:
                _all.append(line)
            return _all
        else:
            return str(f.read())

def read_json(file_path: str, file_code: Literal['utf-8', 'auto'] = 'utf-8', parse: bool = True) -> Union[str, Dict[str, Any]]:
    """
    Reads content from a JSON file and optionally parses it.

    :param file_path: The path to the JSON file to read.
    :param file_code: The encoding to use ('utf-8' or 'auto' to detect existing encoding).
    :param parse: If True, parses the file content as JSON and returns a dictionary.
                  If False, returns the raw file content as a string.
    :return: A dictionary if `parse` is True, or a string if `parse` is False.
    :raises ValueError: If `file_path` is invalid, points to a directory, or if JSON parsing fails.
    Example:
    >>> import tempfile, os, json
    >>> test_data = {"key": "value", "number": 123}
    >>> with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
    ...     json.dump(test_data, tmp_file)
    ...     tmp_file_path = tmp_file.name
    >>> parsed_json = read_json(tmp_file_path)
    >>> print(parsed_json == test_data)
    True
    >>> raw_content = read_json(tmp_file_path, parse=False)
    >>> print(isinstance(raw_content, str))
    True
    >>> os.remove(tmp_file_path)

    >>> # Example of invalid JSON
    >>> with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file_bad:
    ...     tmp_file_bad.write("{invalid json}")
    ...     tmp_file_bad_path = tmp_file_bad.name
    14
    >>> try:
    ...     read_json(tmp_file_bad_path)
    ... except ValueError as _e:
    ...     print(e.__class__.__name__ == "ValueError")
    True
    >>> os.remove(tmp_file_bad_path)
    """
    _valid_path(file_path)
    if file_code == "auto":
        file_code = _auto_file_code(file_path)
    with open(file_path, 'r', encoding=file_code) as f:
        _content = f.read()
    if parse:
        try:
            return loads(_content)
        except JSONDecodeError as e:
            raise ValueError(f"Invalid json file: {e}") from e
    else:
        return _content

