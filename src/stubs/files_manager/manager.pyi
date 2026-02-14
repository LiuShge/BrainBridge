from typing import Dict, Literal, List, Union, Any

def return_path_of_dir_under_root_dir(dir_name: str) -> str:
    """
        Returns the absolute path of a specified directory located directly under the project's root directory.
        The project root is determined by searching for the 'src' directory in the current file's path.

        :param dir_name: The name of the directory to locate under the project root.
        :return: The absolute path of the specified directory.
        :raises ValueError: If 'src' is not found in the current file's path,
                            if the specified `dir_name` is not found under the root,
                            or if `dir_name` is not a directory.
    """
    pass

def return_dir_member(dir_path: str) -> Union[Dict[str, Literal['file', 'dir']], None]:
    """
        Returns a dictionary of members (files and subdirectories) within a given directory.
        If the provided path is a file, returns None.

        :param dir_path: The path to the directory to inspect.
        :return: A dictionary where keys are member names and values are 'file' or 'dir',
                 or None if `dir_path` points to a file.
        :raises ValueError: If `dir_path` is an invalid or non-existent path.
    """
    pass

def _valid_path(target_path: str, is_file: bool = True) -> None:
    """
        Validates if a given path exists and is either a file or a directory.

        :param target_path: The path to validate.
        :param is_file: If True, validates if the path is a file. If False, validates if it's a directory.
        :raises ValueError: If the path is invalid or does not match the expected type.
    """
    pass

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
    """
    pass

def _auto_file_code(file_path: str) -> str:
    """
    Detects the encoding of a given file.

    :param file_path: The path to the file.
    :return: A string representing the detected file encoding (e.g., 'utf-8').
    """
    pass

def write_content_tofile(file_path: str, content:str, file_code: Literal['utf-8', 'auto'] = 'utf-8', trailing_newline: bool = True, override: bool = False) -> None:
    """
        Writes content to a specified file.

        :param file_path: The path to the file to write to.
        :param content: The string content to write.
        :param file_code: The encoding to use ('utf-8' or 'auto' to detect existing encoding).
        :param trailing_newline: If True, appends a newline character at the end of the content.
        :param override: If True, overwrites the file; otherwise, appends to it.
        :raises ValueError: If `file_path` is invalid or points to a directory.
    """
    pass

def read_file(file_path: str, line_by_line: bool = False, file_code: Literal['utf-8', 'auto'] = 'utf-8') -> Union[str, List[str]]:
    """
        Reads content from a specified file.

        :param file_path: The path to the file to read from.
        :param line_by_line: If True, returns a list of strings (each line). If False, returns the entire content as a single string.
        :param file_code: The encoding to use ('utf-8' or 'auto' to detect existing encoding).
        :return: A string or a list of strings containing the file's content.
        :raises ValueError: If `file_path` is invalid or points to a directory.
    """
    pass

def read_json(file_path: str, file_code: Literal['utf-8', 'auto'] = 'utf-8', parse: bool = True) -> Union[str, Dict[str, Any]]:
    """
        Reads content from a JSON file and optionally parses it.

        :param file_path: The path to the JSON file to read.
        :param file_code: The encoding to use ('utf-8' or 'auto' to detect existing encoding).
        :param parse: If True, parses the file content as JSON and returns a dictionary.
                      If False, returns the raw file content as a string.
        :return: A dictionary if `parse` is True, or a string if `parse` is False.
        :raises ValueError: If `file_path` is invalid, points to a directory, or if JSON parsing fails.
    """
    pass
