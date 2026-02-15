from typing import List, Literal, Optional, Union, Any
import sys
import importlib.util
import hashlib
from os import path

from set_source_dir import _set_source_dir, _restore_sys_path

_set_source_dir()
from simple_import import change_sys_path

change_sys_path(to_runlib=True)
from files_manager.manager import *

_restore_sys_path()


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
        if CheckTools.attitude == "strict":
            raise RuntimeError(content)

        if is_fatal:
            raise RuntimeError(f"Error : {content}")
        else:
            msg = f"Warning : {content}"
            if CheckTools.display:
                print(msg)
                return None
            return msg

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
        python_v = sys.version_info
        py_v_need = (3, 14, 0, 'final', 0)

        if python_v.major != py_v_need[0]:
            return CheckTools.decision_making(
                f"Critical Python version error, expected major {py_v_need[0]}",
                is_fatal=True
            )

        is_out_of_range = (
                python_v.minor not in range(py_v_need[1] - 2, py_v_need[1] + 9) or
                python_v.micro not in range(0, py_v_need[2] + 9)
        )

        if is_out_of_range:
            warning_msg = f"Python version {python_v.major}.{python_v.minor} is not in recommended range."
            return CheckTools.decision_making(warning_msg, is_fatal=False)

        return None

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
        missing_logs = []

        for package in requirements:
            spec = importlib.util.find_spec(package)
            if spec is None:
                msg = f"Dependency '{package}' is not installed."
                res = CheckTools.decision_making(msg, is_fatal=False)
                if res:
                    missing_logs.append(res)

        return missing_logs if not CheckTools.display and missing_logs else None

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
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except FileNotFoundError as e:
            raise

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
        current_hash = CheckTools._get_file_hash(file_path)
        if current_hash == expected_hash:
            return True

        msg = f"Code integrity check failed for {file_path}. Hash mismatch."
        return CheckTools.decision_making(msg, is_fatal=False)

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
        valid_path(file_path)
        current_hash = CheckTools._get_file_hash(file_path)
        if current_hash == expected_hash:
            return True

        msg = f"File hash mismatch: {file_path}"
        return CheckTools.decision_making(msg, is_fatal=False)

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
        try:
            content = read_file(file_path, file_code='auto')
            return str(content)
        except Exception as e:
            raise RuntimeError(f"Failed to read file for backup/copy: {file_path}") from e

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
        if backup_path is None:
            backup_path = path.join(return_path_of_dir_under_root_dir("storage"), "backup")

        try:
            valid_path(fix_file_path)
        except (ValueError, OSError):
            with open(fix_file_path, 'w', encoding='utf-8') as f:
                pass

        valid_path(backup_path, is_file=False)
        fix_file_name = path.basename(fix_file_path)
        file_tree = return_full_tree(backup_path)

        found_backup_full_path: Optional[str] = None

        def _find_file_in_tree(data: Any) -> bool:
            """
            Internal helper to recursively search for the filename in the nested tree.
            """
            nonlocal found_backup_full_path
            if isinstance(data, list):
                for item in data:
                    if _find_file_in_tree(item):
                        return True
            elif isinstance(data, dict):
                for folder_path, contents in data.items():
                    if path.basename(folder_path) == fix_file_name:
                        found_backup_full_path = folder_path
                        return True
                    if _find_file_in_tree(contents):
                        return True
            elif isinstance(data, str):
                if path.basename(data) == fix_file_name:
                    found_backup_full_path = data
                    return True
            return False

        if _find_file_in_tree(file_tree):
            backup_content = CheckTools._copy_file(found_backup_full_path)
            write_content_tofile(fix_file_path, str(backup_content), override=True)
            if CheckTools.display:
                print(f"Successfully restored {fix_file_path} from {found_backup_full_path}")
        else:
            raise FileNotFoundError(f"No suitable backup file for '{fix_file_name}' was found in {backup_path}")

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
        CheckTools.fix_code_file(target_conf, backup_path)

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
        write_content_tofile(backup_path, CheckTools._copy_file(current_file), "auto", override=True)
