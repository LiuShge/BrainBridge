from simple_import import change_sys_path, restore_sys_path
from typing import Any, Dict, Union
from os import path

change_sys_path(to_runlib=True)
from files_manager.manager import *

restore_sys_path()


class Converter:
    """A converter class for validating and storing provider-specific configuration parameters."""

    def __init__(self, provider: str, **kwargs):
        """
        Initialize a Converter instance with specified provider and configuration parameters.

        :param provider: The name of the provider to use for configuration mapping.
        :param kwargs: Additional configuration parameter names and values.

        Example:
        >>> conv = Converter("openai_completion", temperature=0.7, max_completion_tokens=100)
        >>> print(conv.provider)
        openai_completion
        """
        config_path = path.join(return_path_of_dir_under_root_dir("config"), "sys_conf", "escape_table.json")
        supported_provider_roles = read_json(config_path)

        if provider not in supported_provider_roles:
            raise ValueError(f'The provider passed in is not supported: "{provider}"')

        selected_provider_role = supported_provider_roles[provider]

        kwargs = Converter._generic_arg_replace(provider, kwargs)

        for key, value in kwargs.items():
            if key not in selected_provider_role["input"]:
                raise ValueError(f'Unsupported parameter: "{key}"')

            _allow_type = Converter.parse_types(selected_provider_role["input"][key], value)

            if _allow_type is False:
                raise ValueError(
                    f"Type of arg '{key}' not matching: expected {selected_provider_role['input'][key]}, got {type(value).__name__}"
                )
            elif _allow_type is None:
                print(f"Warning: Unknown type definition '{selected_provider_role['input'][key]}'")

        self.provider = provider
        self.information = kwargs

    @staticmethod
    def parse_types(str_type: str, _object: Any) -> bool | None:
        """
        Parse a type string and check if the object matches any of the specified types.

        Supports type strings in the following formats:
        - Single type: "str", "int", "list", "dict", "bool", "float", "None"
        - Multiple types separated by pipe: "str|list", "int|float|str"

        :param str_type: Type string to parse, e.g., "str", "int|float", "list|dict|None".
        :param _object: The Python object to check against the parsed types.

        Returns:
            - bool: True if object matches at least one type, False if matches none.
            - None: if str_type contains unsupported types.

        Example:
            >>> Converter.parse_types("str", "hello")
            True
            >>> Converter.parse_types("int | float", 42)
            True
            >>> Converter.parse_types("str | list", "hello")
            True
            >>> Converter.parse_types("int", "hello")
            False
            >>> Converter.parse_types("unknown", 42) is None
            True
        """
        str_type = str_type.lower().replace(" ", "")
        type_mapping = {
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
            "none": type(None),
        }
        type_names = [t.strip() for t in str_type.split("|")]
        valid_types = []
        for name in type_names:
            if name not in type_mapping:
                return None
            valid_types.append(type_mapping[name])
        return isinstance(_object, tuple(valid_types))

    @staticmethod
    def _generic_arg_replace(provider: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert generic argument names to provider-specific ones based on mapping rules,
        and perform basic validation.

        This method supports loading mapping configurations from 'base_arg_match.json'.

        :param provider: Name of the service provider (e.g., 'openai', 'anthropic').
        :param kwargs: Keyword arguments representing generic parameters.
        :return: A dictionary with translated and validated provider-specific arguments.

        Example:
        >>> result = Converter._generic_arg_replace("openai", model="gpt-3.5-turbo", input="Hello")
        >>> print(result)
        {'model': 'gpt-3.5-turbo', 'messages': 'Hello'}
        """
        # 1. Locate configuration directory and load mapping file
        config_dir = return_path_of_dir_under_root_dir("config")
        config_path = path.join(config_dir, "sys_conf", "base_arg_match.json")
        generic_args: Dict[str, Union[Dict[str, str], list]] = read_json(config_path)
        if provider not in generic_args:
            raise ValueError(f"Unsupported provider: \"{provider}\"")
        # 2. Retrieve provider-specific mappings and global base argument definitions
        provider_map: Dict[str, str] = generic_args[provider]
        based_args: list = generic_args.get("based_args", [])
        # 3. Validate required core arguments
        for essential_arg in ["model", "input"]:
            if essential_arg not in kwargs:
                raise ValueError(
                    f"Provider '{provider}' is missing required argument: '{essential_arg}'"
                )
        # 4. Translate and construct final parameter set
        translated_info: Dict[str, Any] = {}
        for key, value in kwargs.items():
            target_key = provider_map.get(key, key)
            translated_info[target_key] = value
        # 5. Auto-fill default values for standard base arguments if needed
        if "stream" in based_args and "stream" not in kwargs:
            translated_info[provider_map.get("stream", "stream")] = True
        return translated_info
