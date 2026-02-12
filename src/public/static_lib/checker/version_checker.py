import importlib.util
from typing import Iterable, Dict

def _is_package_available(package_name: str) -> bool:
    """
    Determine whether a package can be imported without executing it.

    :param package_name: The module or package name to check.
    :return: True when the import specification exists on sys.path.
    Example:
    >>> _is_package_available("json")
    True
    """
    return importlib.util.find_spec(package_name) is not None

def check_packages(packages: Iterable[str]) -> Dict[str, bool]:
    """
    Check availability of multiple packages and report the status.

    :param packages: Iterable of module/package names to verify.
    :return: Mapping from package name to availability boolean.
    Example:
    >>> check_packages(["sys", "fake_pkg"])
    {'sys': True, 'fake_pkg': False}
    """
    return {name: _is_package_available(name) for name in packages}
