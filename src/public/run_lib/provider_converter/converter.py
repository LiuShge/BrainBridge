from __future__ import annotations

from os import path
from typing import Any, Dict, List, Literal, Mapping, Optional, Tuple
from set_source_dir import _set_source_dir,_restore_sys_path
_set_source_dir()   # let simple_import can be import

from simple_import import change_sys_path, restore_sys_path
change_sys_path(to_runlib=True) # let libs under run_lib can be import
from files_manager.manager import *

restore_sys_path()
_restore_sys_path()

class _ConfigEngine:
    """
    Configuration loading engine responsible for merging user_conf and sys_conf, and validating configuration consistency.

    This engine provides a centralized mechanism to load, merge, and validate configuration files
    from both system and user directories. User configurations take precedence over system configurations.
    All configurations are cached to improve performance.
    """
    _CACHE: Dict[str, Any] = {}

    @staticmethod
    def _load_and_merge(file_name: str) -> Dict[str, Any]:
        """
        Merge system configuration and user configuration for a given file name.

        User configuration takes precedence over system configuration when keys overlap.

        :param file_name: Name of the configuration file to load and merge.

        :return: Dictionary containing the merged configuration.

        Example:
        >>> merged_config = _ConfigEngine._load_and_merge("base_arg_match.json")
        >>> isinstance(merged_config, dict)
        True
        """
        sys_path = path.join(return_path_of_dir_under_root_dir("config"), "sys_conf", file_name)
        user_path = path.join(return_path_of_dir_under_root_dir("config"), "user_conf", file_name)

        sys_cfg = read_json(sys_path) if path.exists(sys_path) else {}
        user_cfg = read_json(user_path) if path.exists(user_path) else {}

        merged = {**sys_cfg, **user_cfg}
        return merged

    @staticmethod
    def _verify_config(base_match: Dict[str, Any], escape_table: Dict[str, Any]) -> bool:
        """
        Internal function to validate configuration meets custom conditions.

        Validation criteria:
        1. The based_args list must match the system standard.
        2. Each item in based_args must have a corresponding value in the Provider's input mapping.
        3. The target value of the mapping must be a key defined in escape_table's input.

        :param base_match: Base argument mapping configuration dictionary.
        :param escape_table: Escape table configuration dictionary containing provider definitions.

        :return: True if configuration passes validation, False otherwise.

        Example:
        >>> _base_match = {"based_args": ["messages", "model"], "provider1": {"input": {"messages": "content"}}}
        >>> _escape_table = {"provider1": {"input": {"content": "str"}}}
        >>> is_valid = _ConfigEngine._verify_config(_base_match, _escape_table)
        >>> isinstance(is_valid, bool)
        True
        """
        sys_path = path.join(return_path_of_dir_under_root_dir("config"), "sys_conf", "base_arg_match.json")
        sys_cfg = read_json(sys_path) if path.exists(sys_path) else {}
        standard_args = sys_cfg["based_args"] if "based_args" in sys_cfg.keys() \
            else ["messages", "model", "stream", "max_tokens", "usage"]
        if base_match.get("based_args") != standard_args:
            return False

        for provider, config in base_match.items():
            if provider == "based_args": continue

            input_mapping = config.get("input", {})
            escape_input = escape_table.get(provider, {}).get("input", {})

            for arg in standard_args:
                if arg not in input_mapping:
                    return False

                target_key = input_mapping[arg]
                if target_key and target_key not in escape_input:
                    if target_key != "":
                        return False
        return True

    @classmethod
    def get_configs(cls) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Get validated configurations for base_arg_match and escape_table.

        This method loads and merges configurations from both system and user directories,
        validates them, and caches the results. If validation fails, it falls back to
        system-only configurations to ensure program stability.

        Returns:
            Tuple containing:
            - base_match: Validated base argument mapping configuration.
            - escape_table: Validated escape table configuration.

        Example:
        >>> __base_match, __escape_table = _ConfigEngine.get_configs()
        >>> isinstance(__base_match, dict) and isinstance(__escape_table, dict)
        True
        """
        if "base_match" not in cls._CACHE:
            base_match = cls._load_and_merge("base_arg_match.json")
            escape_table = cls._load_and_merge("escape_table.json")

            if not cls._verify_config(base_match, escape_table):
                base_match = read_json(
                    path.join(return_path_of_dir_under_root_dir("config"), "sys_conf", "base_arg_match.json"))
                escape_table = read_json(
                    path.join(return_path_of_dir_under_root_dir("config"), "sys_conf", "escape_table.json"))

            cls._CACHE["base_match"] = base_match
            cls._CACHE["escape_table"] = escape_table

        return cls._CACHE["base_match"], cls._CACHE["escape_table"]


class Converter:
    """
    Argument converter for transforming generic request arguments into provider-specific format.

    This class handles the conversion of standardized API arguments to provider-specific
    parameter names and performs type validation against the provider's requirements.
    Essential arguments are enforced to ensure proper API calls.
    """
    _TYPE_MAPPING: Dict[str, type] = {
        "str": str, "int": int, "float": float, "bool": bool,
        "list": list, "dict": dict, "none": type(None),
    }
    _ESSENTIAL_ARGS: tuple[str, ...] = ("model", "messages")

    def __init__(self, provider: str, **kwargs: Any) -> None:
        """
        Initialize a Converter instance for a specific provider.

        :param provider: Name of the provider to convert arguments for.
        :param **kwargs: Arguments to be converted and validated.

        :raises ValueError: If provider is unsupported, essential arguments are missing,
                           or argument types don't match provider requirements.

        Example:
        >>> converter = Converter("openai", model="gpt-4", messages=[{"role": "user", "content": "Hello"}])
        >>> converter.provider
        'openai'
        """
        base_match, escape_table = _ConfigEngine.get_configs()

        if provider not in escape_table:
            raise ValueError(f'Unsupported provider: "{provider}"')

        selected_provider_role = escape_table[provider]

        kwargs = Converter._generic_arg_replace(provider, kwargs, base_match)

        for key, value in kwargs.items():
            if key not in selected_provider_role.get("input", {}):
                continue
            is_allowed = Converter.parse_types(selected_provider_role["input"][key], value)
            if is_allowed is False:
                raise ValueError(f"Type of arg '{key}' mismatch for {provider}")

        self.provider = provider
        self.information: Dict[str, Any] = kwargs

    @staticmethod
    def parse_types(str_type: Any, _object: Any) -> Optional[bool]:
        """
        Validate that an object matches the specified type definition.

        Supports type definitions as strings (e.g., "str|int|none", "list[str]"),
        dictionaries for dict types, and lists for list types. Multiple types
        can be specified using pipe notation.

        :param str_type: Type definition to validate against (string, list, or dict).
        :param _object: Object to validate against the type definition.

        :return: True if object matches type, False if not, None for ambiguous cases.

        Example:
        >>> Converter.parse_types("str|int", 42)
        True
        >>> Converter.parse_types("str", 42)
        False
        >>> Converter.parse_types("none", None)
        True
        """
        if isinstance(str_type, list):
            if not isinstance(_object, list): return False
            if all(isinstance(item, str) for item in str_type):
                str_type = "|".join(str_type)
            else:
                return isinstance(_object, list)

        if isinstance(str_type, str):
            str_type = str_type.lower().replace(" ", "")
            type_names = [t.strip() for t in str_type.split("|")]
            valid_types = [Converter._TYPE_MAPPING[n] for n in type_names if n in Converter._TYPE_MAPPING]
            if "none" in type_names: valid_types.append(type(None))
            return isinstance(_object, tuple(valid_types)) if valid_types else True

        if isinstance(str_type, dict): return isinstance(_object, dict)
        return isinstance(_object, type(_object))

    @staticmethod
    def _generic_arg_replace(provider: str, kwargs: Mapping[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Replace generic argument names with provider-specific names using mapping configuration.

        :param provider: Name of the provider to get the mapping configuration for.
        :param kwargs: Dictionary of generic argument names and their values.
        :param config: Configuration dictionary containing provider mappings.

        :return: Dictionary with provider-specific argument names.

        Example:
        >>> _config = {"openai": {"input": {"messages": "messages", "model": "model"}}, "based_args": ["messages"]}
        >>> result = Converter._generic_arg_replace("openai", {"messages": [], "model": "gpt-4"}, _config)
        >>> "messages" in result
        True
        """
        provider_map = config.get(provider, {}).get("input", {})

        for essential_arg in Converter._ESSENTIAL_ARGS:
            if essential_arg not in kwargs:
                raise ValueError(f"Missing essential arg: '{essential_arg}'")

        translated_info: Dict[str, Any] = {}
        for key, value in kwargs.items():
            target_key = provider_map.get(key, key)
            if not isinstance(target_key, str):
                raise ValueError(f"Mapping for {key} must be a string")
            translated_info[target_key] = value

        based_args = config.get("based_args", [])
        if "stream" in based_args and "stream" not in kwargs:
            stream_key = provider_map.get("stream", "stream")
            translated_info[stream_key] = True

        return translated_info


class Operator:
    """
    Utility class for building HTTP headers and unwrapping API responses.

    This class provides nested classes for specific operations:
    - HeadersBuilder: Constructs HTTP request headers.
    - ResponseUnwarp: Parses and extracts data from provider responses.
    """

    class HeadersBuilder:
        """
        Builder class for constructing HTTP headers with authentication.

        Provides static methods to generate standardized headers for API requests,
        including Bearer token authentication and optional Accept headers.
        """

        @staticmethod
        def builder(api_token: str, include_accept: bool = False) -> Dict[str, str]:
            """
            Build HTTP headers with Bearer token authentication.

            :param api_token: API token for Bearer authentication.
            :param include_accept: If True, include Accept header for JSON responses.

            :return: Dictionary of HTTP headers.

            Example:
            >>> headers = Operator.HeadersBuilder.builder("sk-12345", include_accept=True)
            >>> "Authorization" in headers
            True
            >>> headers["Content-Type"]
            'application/json'
            """
            header = {"Content-Type": "application/json", "Authorization": f"Bearer {api_token}"}
            if include_accept: header["Accept"] = "application/json"
            return header

    class ResponseUnwarp:
        """
        Response parser for extracting data from various provider API response formats.

        This class provides utilities to navigate nested response structures and extract
        relevant information such as text content, usage statistics, and metadata.
        Supports both regular and streaming response formats.
        """
        _METADATA_FIELDS: frozenset[str] = frozenset(
            {"role", "index", "finish_reason", "object", "id", "created", "model", "logprobs"})

        @staticmethod
        def _get_nested_value(data: Any, path_str: str) -> Any:
            """
            Navigate through nested data structure using a path string.

            :param data: Nested data structure (dict, list, or other).
            :param path_str: Path string separated by '/' with optional '*' for array traversal.

            :return: Value found at the specified path, or None if path is invalid.

            Example:
            >>> _data = {"a": {"b": {"c": 42}}}
            >>> result = Operator.ResponseUnwarp._get_nested_value(_data, "a/b/c")
            >>> result
            42
            """
            if not path_str or data is None: return None
            parts = path_str.split('/')
            current = data
            for i, part in enumerate(parts):
                if part.startswith('*'):
                    key = part[1:]
                    target_list = current.get(key) if isinstance(current, dict) else current
                    if not isinstance(target_list, list): return None
                    remaining_path = "/".join(parts[i + 1:])
                    if not remaining_path: return target_list
                    results = [Operator.ResponseUnwarp._get_nested_value(item, remaining_path) for item in target_list]
                    return [r for r in results if r is not None]
                else:
                    if isinstance(current, dict):
                        current = current.get(part)
                    else:
                        return None
            return current

        @staticmethod
        def _deep_extract_text(obj: Any, content_keys: List[str] | None = None) -> List[str]:
            """
            Recursively extract text content from nested data structures.

            :param obj: Object to extract text from (str, list, dict, or other).
            :param content_keys: List of keys to look for in dictionaries for text content.

            :return: List of extracted text strings.

            Example:
            >>> data = {"content": {"text": "Hello"}}
            >>> result = Operator.ResponseUnwarp._deep_extract_text(data)
            >>> len(result) > 0
            True
            """
            if content_keys is None: content_keys = ["content", "text", "refusal"]
            texts = []
            if isinstance(obj, str):
                if obj.strip(): texts.append(obj)
            elif isinstance(obj, list):
                for item in obj: texts.extend(Operator.ResponseUnwarp._deep_extract_text(item, content_keys))
            elif isinstance(obj, dict):
                for key in content_keys:
                    if key in obj:
                        val = obj[key]
                        if val is None: continue
                        if isinstance(val, dict):
                            sub_keys = [k for k in val.keys() if k not in Operator.ResponseUnwarp._METADATA_FIELDS]
                            texts.extend(Operator.ResponseUnwarp._deep_extract_text(val, sub_keys))
                        else:
                            if str(val).strip(): texts.append(str(val))
            return texts

        @staticmethod
        def unwarp(provider: str, response: Any) -> Dict[
            Literal['response_text', 'response_usage', 'response_information', 'raw_response'], Any]:
            """
            Unwrap and parse provider response into standardized format.

            This method extracts response text, usage information, and metadata from
            provider-specific response formats based on configuration mappings.

            :param provider: Name of the provider that generated the response.
            :param response: Response data from the provider API.

            :return: Dictionary with keys:
                    - response_text: Extracted text content.
                    - response_usage: Usage statistics (tokens, etc.).
                    - response_information: Additional metadata.
                    - raw_response: Original response data.

            Example:
            >>> _response = {"choices": [{"message": {"content": "Hello"}}], "usage": {"total_tokens": 10}}
            >>> _result = Operator.ResponseUnwarp.unwarp("openai", _response)
            >>> "response_text" in _result
            True
            """
            base_match, _ = _ConfigEngine.get_configs()

            if provider not in base_match:
                raise ValueError(f"Provider {provider} mapping not defined")

            is_stream = isinstance(response, dict) and response.get("object") == "chat.completion.chunk"
            output_conf = base_match[provider].get("stream.output" if is_stream else "output", {})

            result = {"response_text": None, "response_usage": {}, "response_information": {}, "raw_response": response}

            for arg_name in base_match.get("based_args", []):
                path_formula = output_conf.get(arg_name)
                if not path_formula: continue
                extracted = Operator.ResponseUnwarp._get_nested_value(response, path_formula)

                if arg_name == "messages":
                    text_list = Operator.ResponseUnwarp._deep_extract_text(extracted)
                    result["response_text"] = "\n".join(text_list) if text_list else None
                elif arg_name == "usage":
                    result["response_usage"] = extracted if isinstance(extracted, dict) else {}
                else:
                    result["response_information"][arg_name] = extracted
            return result
