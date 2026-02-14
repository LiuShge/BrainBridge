from typing import List, Optional, Union

FILE_PATH = str(__file__)

class Converter:
    """
    A utility class to construct and validate payloads for API requests, with support for multimodal content.

    This class ensures that the input data (e.g., messages, model parameters) adheres to the expected format
    and structure, converting it into a validated payload ready for API transmission.

    Key Features:
    - Supports both single and batch message validation.
    - Validates multimodal content (e.g., text, images).
    - Handles optional parameters like `temperature`, `max_tokens`, `top_p`, `seed`, and `n`.
    - Ensures strict type and value constraints for all parameters.

    Example:
    >>> converter = Converter(
    ...     model="gpt-4o",
    ...     content={"role": "user", "content": "Hello, world!"},
    ...     temperature=0.7,
    ...     max_tokens=100
    ... )
    >>> print(converter.payload)
    {'model': 'gpt-4o', 'messages': [{'role': 'user', 'content': 'Hello, world!'}], 'temperature': 0.7, 'max_tokens': 100, 'stream': False}
    """

    def __init__(
        self,
        model: str,
        content: Union[List[dict], dict],
        stream: bool = False,
        temperature: Optional[Union[float, int]] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[Union[float, int]] = None,
        seed: Optional[int] = None,
        n: Optional[int] = None
    ):
        """
        Initialize a Converter instance to construct and validate a payload for API requests.

        :param model: Name of the model to use (e.g., "gpt-4o").
        :param content: Input message(s) to process. Can be a single dictionary or a list of dictionaries.
                       Each dictionary must include `role` and `content` keys.
                       - `role`: Must be one of ['system', 'user', 'assistant', 'tool', 'function'].
                       - `content`: Can be a string (text) or a list of multimodal parts (e.g., text + images).
        :param stream: Whether to enable streaming mode. Defaults to False.
        :param temperature: Sampling temperature (0-2). Higher values make output more random.
                            If None, the API default is used.
        :param max_tokens: Maximum number of tokens to generate. If None, the API default is used.
        :param top_p: Nucleus sampling probability (0-1). If None, the API default is used.
        :param seed: Random seed for reproducibility. If None, no seed is set.
        :param n: Number of responses to generate. Must be a positive integer. If None, the API default is used.

        :raises ValueError: If any parameter fails validation (e.g., invalid `role`, `content`, or value ranges).
        :raises TypeError: If `content` is neither a dictionary nor a list of dictionaries.

        Example:
        >>> converter = Converter(
        ...     model="gpt-4o",
        ...     content=[
        ...         {"role": "system", "content": "You are a helpful assistant."},
        ...         {"role": "user", "content": "What is the weather today?"}
        ...     ],
        ...     temperature=0.5,
        ...     max_tokens=50
        ... )
        >>> print(len(converter.payload["messages"]))
        2
        """
        payload = dict()
        payload['model'] = model
        messages_list = []

        def _validate_single_message_dict(message_dict: dict) -> dict:
            """
            Validate a single message dictionary, including its `role` and `content` fields.

            Supports multimodal content (e.g., text + images) if `content` is a list.

            :param message_dict: Dictionary containing `role` and `content` keys.
            :return: The validated message dictionary.
            :raises ValueError: If the message dictionary is invalid or contains unsupported content types.
            """
            if not isinstance(message_dict, dict):
                raise ValueError(f"{FILE_PATH} Converter.__init__() failed error - Message part must be a dictionary.")
            if 'role' not in message_dict or 'content' not in message_dict:
                raise ValueError(
                    f"{FILE_PATH} Converter.__init__() failed error - Message dict must have 'role' and 'content' keys.")

            # Validate role
            valid_roles = ['system', 'user', 'assistant', 'tool', 'function']
            if message_dict['role'] not in valid_roles:
                raise ValueError(
                    f"{FILE_PATH} Converter.__init__() failed error - Invalid role '{message_dict['role']}' in message. "
                    f"Must be one of {valid_roles}.")

            # Validate content field (supports string or list for multimodal)
            message_content = message_dict['content']

            if isinstance(message_content, str):
                pass  # Text content is valid
            elif isinstance(message_content, list):
                if not message_content:
                    raise ValueError(
                        f"{FILE_PATH} Converter.__init__() failed error - Multimodal content list cannot be empty.")

                for part_idx, part in enumerate(message_content):
                    if not isinstance(part, dict):
                        raise ValueError(
                            f"{FILE_PATH} Converter.__init__() failed error - Multimodal content part at index {part_idx} "
                            f"must be a dictionary.")
                    if 'type' not in part:
                        raise ValueError(
                            f"{FILE_PATH} Converter.__init__() failed error - Multimodal content part at index {part_idx} "
                            f"must have a 'type' key.")

                    part_type = part['type']
                    if part_type == 'text':
                        if 'text' not in part or not isinstance(part['text'], str):
                            raise ValueError(
                                f"{FILE_PATH} Converter.__init__() failed error - Text content part at index {part_idx} "
                                f"must have a 'text' (string) key.")
                    elif part_type == 'image_url':
                        if 'image_url' not in part or not isinstance(part['image_url'], dict):
                            raise ValueError(
                                f"{FILE_PATH} Converter.__init__() failed error - Image content part at index {part_idx} "
                                f"must have an 'image_url' (dict) key.")

                        image_url_obj = part['image_url']
                        if 'url' not in image_url_obj or not isinstance(image_url_obj['url'], str):
                            raise ValueError(
                                f"{FILE_PATH} Converter.__init__() failed error - image_url object at index {part_idx} "
                                f"must have a 'url' (string) key.")

                        if 'detail' in image_url_obj and not isinstance(image_url_obj['detail'], str):
                            raise ValueError(
                                f"{FILE_PATH} Converter.__init__() failed error - image_url detail at index {part_idx} "
                                f"must be a string.")
                    else:
                        raise ValueError(
                            f"{FILE_PATH} Converter.__init__() failed error - Unknown content part type '{part_type}' "
                            f"at index {part_idx}. Expected 'text' or 'image_url'.")
            else:
                raise ValueError(
                    f"{FILE_PATH} Converter.__init__() failed error - Message content must be a string or a list of content parts.")

            return message_dict

        if isinstance(content, dict):
            messages_list.append(_validate_single_message_dict(content))
        elif isinstance(content, list):
            if not content:
                raise ValueError(f"{FILE_PATH} Converter.__init__() failed error - Content list cannot be empty.")
            for cont in content:
                messages_list.append(_validate_single_message_dict(cont))
        else:
            raise TypeError(
                f"{FILE_PATH} Converter.__init__() failed error - content must be a dict or a list of dicts.")

        payload['messages'] = messages_list

        # Validate and add max_tokens
        if max_tokens is not None:
            if isinstance(max_tokens, int) and max_tokens >= 0:
                payload['max_tokens'] = max_tokens
            else:
                raise ValueError(
                    f"{FILE_PATH} Converter.__init__() failed error - max_tokens must be a non-negative integer.")

        # Validate and add temperature
        if temperature is not None:
            if isinstance(temperature, (float, int)) and 0 <= temperature <= 2:
                payload['temperature'] = float(temperature)
            else:
                raise ValueError(
                    f"{FILE_PATH} Converter.__init__() failed error - temperature must be between 0 and 2.0.")

        # Validate and add top_p
        if top_p is not None:
            if isinstance(top_p, (float, int)) and 0 <= top_p <= 1:
                payload['top_p'] = float(top_p)
            else:
                raise ValueError(f"{FILE_PATH} Converter.__init__() failed error - top_p must be between 0 and 1.0.")

        # Validate and add seed
        if seed is not None:
            if isinstance(seed, int):
                payload['seed'] = seed
            else:
                raise ValueError(f"{FILE_PATH} Converter.__init__() failed error - seed must be an integer.")

        # Validate and add n
        if n is not None:
            if isinstance(n, int) and n >= 1:
                payload['n'] = n
            else:
                raise ValueError(f"{FILE_PATH} Converter.__init__() failed error - n must be a positive integer.")

        payload['stream'] = stream
        self.payload = payload
