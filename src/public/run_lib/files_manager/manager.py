from os import path, listdir, scandir
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
            f"Cannot find \"{dir_name}\" under root directory, found: {listdir(_base_path)}.")
    if not path.isdir(path.join(_base_path, dir_name)):
        raise ValueError(f"{dir_name} under root dir is not a directory.")
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


def valid_path(target_path: str, is_file: bool = True) -> None:
    """
    Validates if a given path exists and is either a file or a directory.

    :param target_path: The path to validate.
    :param is_file: If True, validates if the path is a file. If False, validates if it's a directory.
    :raises ValueError: If the path is invalid or does not match the expected type.
    Example:
    >>> import tempfile
    >>> with tempfile.NamedTemporaryFile() as tmp_file:
    ...     valid_path(tmp_file.name, is_file=True)
    >>> try:
    ...     valid_path("/non_existent_path", is_file=True)
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

def return_full_tree(*base_paths: str) -> Dict[str, List[Union[str, Dict[str, Any]]]]:
    """
    Highly optimized recursive traversal using os.scandir to minimize system calls.
    Provides a nested tree structure with normalized forward-slash paths.

    Key Optimizations:
    - Uses `os.scandir` to retrieve directory entries and metadata in a single pass.
    - Minimizes redundant `os.path` calls and string manipulations.
    - Prevents infinite recursion from symbolic links using a real-path cache.

    :param base_paths: One or more root directory paths to start the traversal from.
    :return: A dictionary where keys are the normalized base paths, and values are
             nested lists of file paths and subdirectory dictionaries.
    :raises ValueError: If any of the base_paths are invalid or not directories.
    """
    result_tree: Dict[str, List[Union[str, Dict[str, Any]]]] = {}

    _realpath = path.realpath
    _join = path.join
    _normpath = path.normpath

    def _fast_normalize(p: str) -> str:
        """
        Internal helper for rapid path normalization.
        """
        return _normpath(p).replace("\\", "/")

    def _explore_recursive(current_dir: str, visited: Set[str]) -> List[Union[str, Dict[str, Any]]]:
        """
        Optimized internal recursion using scandir entries.
        """
        content_list: List[Union[str, Dict[str, Any]]] = []

        try:
            # Entry contains both name and path, plus cached is_dir/is_file status
            # Sorting entries by name to maintain consistent output
            entries = sorted(scandir(current_dir), key=lambda e: e.name)

            for entry in entries:
                raw_path = entry.path
                normalized_path = _fast_normalize(raw_path)

                if entry.is_dir(follow_symlinks=True):
                    # Realpath is only checked for directories to prevent loops
                    real_p = _realpath(raw_path)
                    if real_p in visited:
                        content_list.append({normalized_path: [f"_loop_detected_at:{normalized_path}"]})
                        continue

                    # Create a new visited set for this branch to allow same dir
                    # to appear in different branches but not in the same lineage
                    new_visited = visited | {real_p}
                    content_list.append({
                        normalized_path: _explore_recursive(raw_path, new_visited)
                    })
                elif entry.is_file():
                    content_list.append(normalized_path)

        except PermissionError:
            content_list.append(f"_permission_denied_for:{_fast_normalize(current_dir)}")
        except OSError as e:
            content_list.append(f"_error_accessing:{_fast_normalize(current_dir)}:{e}")

        return content_list

    for base_path_str in base_paths:
        valid_path(base_path_str, is_file=False)
        norm_base = _fast_normalize(base_path_str)
        # Initialize visited with the starting directory's real path
        result_tree[norm_base] = _explore_recursive(base_path_str, {_realpath(base_path_str)})

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
        return str(detect(f.read())['encoding'])

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
    try:
        valid_path(file_path)
    except (FileNotFoundError, ValueError) as e:
        if override:
            with open(file_path,"w") as f: f.close()
        else:
            raise
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
    valid_path(file_path)
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
    valid_path(file_path)
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
