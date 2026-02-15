from typing import List, Literal, Optional, Union, Any
import sys
import importlib.util
import hashlib
from os import path

# 声明来自 set_source_dir 的外部函数（需要用户确保其在实际代码中存在）
def _set_source_dir() -> None: ...
def _restore_sys_path() -> None: ...

# 声明来自 simple_import 的外部函数
def change_sys_path(to_runlib: bool) -> None: ...

# 声明来自 files_manager.manager 的外部函数（* 对应 from files_manager.manager import *）
def valid_path(target_path: str, is_file: bool = True) -> None: ...
def return_path_of_dir_under_root_dir(dir_name: str) -> str: ...
def return_full_tree(*base_paths: str) -> Any: ... # Any 暂时保留，因为返回结构复杂
def read_file(file_path: str, line_by_line: bool = False, file_code: Literal['utf-8', 'auto'] = 'utf-8') -> Union[str, List[str]]: ...
def write_content_tofile(file_path: str, content:str, file_code: Literal['utf-8', 'auto'] = 'utf-8', trailing_newline: bool = True, override: bool = False) -> None: ...


class CheckTools:
    attitude: Literal["lenient", "strict"] = "lenient"
    display: bool = True

    @staticmethod
    def decision_making(content: str, is_fatal: bool = False) -> Optional[str]:
        """
        Handles decision-making based on the CheckTools attitude ('strict' or 'lenient').
        This method is exclusively for use within other checking methods.

        :param content: The message content for the decision.
        :param is_fatal: If True, raises a critical error, otherwise issues a warning.
        :return: The warning message string if not displaying, otherwise None.
        :raises RuntimeError: If attitude is 'strict' or if is_fatal is True.
        Example:
        >>> CheckTools.attitude = "lenient"
        >>> CheckTools.display = False
        >>> print(CheckTools.decision_making("Test warning", is_fatal=False))
        Warning : Test warning
        """
        ...

    @staticmethod
    def check_py_version() -> Optional[str]:
        """
        Checks the current Python version against the required version (3.14.0).
        Major version mismatch is treated as fatal; minor/micro range issues are warnings.

        :return: None if version is acceptable, or the result of decision_making.
        Example:
        >>> # Assuming current sys.version_info is (3, 13, 0)
        >>> # result = CheckTools.check_py_version()
        """
        ...

    @staticmethod
    def dependency_check(requirements: List[str]) -> Optional[List[str]]:
        """
        Checks if specified packages are installed by attempting to find their modules.

        :param requirements: A list of package names (strings) to check.
        :return: A list of missing package warning strings if display is off, otherwise None.
        Example:
        >>> missing = CheckTools.dependency_check(["requests", "non_existent_package"])
        >>> # If display is False, missing will contain a list of warnings.
        """
        ...

    @staticmethod
    def _get_file_hash(file_path: str) -> str:
        """
        Calculates the SHA256 hash of a file's content.

        :param file_path: The path to the file.
        :return: The hexadecimal SHA256 hash string.
        :raises FileNotFoundError: If the file does not exist.
        Example:
        >>> # Example requires creating a temporary file for testing
        """
        ...

    @staticmethod
    def check_code_hash(file_path: str, expected_hash: str) -> Union[bool, Optional[str]]:
        """
        Compares the calculated hash of a file against an expected hash value.

        :param file_path: The path to the file whose hash is to be checked.
        :param expected_hash: The expected SHA256 hash string.
        :return: True if hashes match, or the decision_making result string on failure.
        Example:
        >>> # result = CheckTools.check_code_hash("main.py", "expectedhash123")
        """
        ...

    @staticmethod
    def check_file_hash(file_path: str, expected_hash: str) -> Union[bool, Optional[str]]:
        """
        Validates the existence of a file and compares its hash against an expected value.

        :param file_path: The path to the file.
        :param expected_hash: The expected SHA256 hash string.
        :return: True if hashes match, or the decision_making result string on failure.
        :raises ValueError: If the path is invalid (checked via valid_path).
        Example:
        >>> # result = CheckTools.check_file_hash("config.json", "expectedhash456")
        """
        ...

    @staticmethod
    def _copy_file(file_path: str) -> str:
        """
        Reads the content of a file with automatic encoding detection.
        :param file_path: The path of the file to be read.
        :return: The content of the file as a string.
        Example:
        >>> # Assuming 'config.json' exists
        >>> content = CheckTools._copy_file("config.json")
        >>> print(type(content))
        <class 'str'>
        """
        ...

    @staticmethod
    def fix_code_file(fix_file_path: str, backup_path: Optional[str] = None) -> None:
        """
        Restores a missing or corrupted file from a backup directory.
        It searches the backup directory tree for a file with the same basename.

        :param fix_file_path: The target path of the file to be restored.
        :param backup_path: The directory path where backup files are stored.
                            Defaults to 'storage/backup' under root.
        :return: None
        :raises FileNotFoundError: If no matching backup file is found.

        Example:
        >>> CheckTools.fix_code_file("src/main.py")
        """
        ...

    @staticmethod
    def fix_conf_file(backup_path: str, target_conf: str) -> None:
        """
        Resets or restores a configuration file using the content found in the backup path.

        :param backup_path: The root directory containing the nested backup structure.
        :param target_conf: The absolute path of the configuration file to fix.
        :return: None
        Example:
        >>> # CheckTools.fix_conf_file("/path/to/backup", "config/user_conf.json")
        """
        ...

    @staticmethod
    def fix_backup_file(current_file: str, backup_path: str) -> None:
        """
        Updates the backup directory with the current, known-good version of a file.

        :param current_file: The path to the current, healthy file.
        :param backup_path: The exact path (including filename) in the backup location to write to.
        :return: None
        Example:
        >>> # CheckTools.fix_backup_file("src/main.py", "storage/backup/main.py")
        """
        ...
