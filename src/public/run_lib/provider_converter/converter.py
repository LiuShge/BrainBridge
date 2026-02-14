from simple_import import change_sys_path, restore_sys_path
from typing import Any
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


if __name__ == "__main__":
    x = Converter(provider="openai_response",model = 'gpt-5.1-codex-mini',input = [{"role":"user","content":"非常详细的讲解python"}],stream=True,max_output_tokens=1000)
    print(x.information)
    headers = {"Content-Type": "application/json","Authorization": "Bearer sk-*******"}
    import json
    change_sys_path(to_runlib=True)
    from requests_core.request_core import Request
    restore_sys_path()
    y = Request()
    z = y.request_sse(method="POST",url="https://www.easycodex.cn/v1/responses", json=x.information, headers=headers,timeout=100)
    for i in z:
        print(json.loads(i['data'])['delta'].encode('latin-1').decode('utf-8') if 'delta' in json.loads(i['data']).keys() else '',end='')