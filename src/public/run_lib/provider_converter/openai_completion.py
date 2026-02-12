#TODO: 使用files_manager填充FILE_PATH

from typing import List, Optional, Union

FILE_PATH = "BrainBridge/main/net/request/Interface/openai_completion.py"

class Converter:
    # 传入必要的和可选的数据并加工为未来的payload传出
    def __init__(self,
                 model: str,
                 content: Union[List[dict], dict],
                 stream: bool = False,
                 temperature: Optional[Union[float, int]] = None,
                 max_tokens: Optional[int] = None, # Renamed to max_tokens
                 top_p: Optional[Union[float, int]] = None,
                 seed: Optional[int] = None,
                 n: Optional[int] = None):

        payload = dict()

        payload['model'] = model

        messages_list = []

        # 辅助函数：验证单个消息字典（包括其 content 字段，支持多模态）
        def _validate_single_message_dict(message_dict: dict) -> dict:
            if not isinstance(message_dict, dict):
                raise ValueError(f"{FILE_PATH} Converter.__init__() failed error - Message part must be a dictionary.")
            if 'role' not in message_dict or 'content' not in message_dict:
                raise ValueError(f"{FILE_PATH} Converter.__init__() failed error - Message dict must have 'role' and 'content' keys.")

            # 验证 role
            valid_roles = ['system', 'user', 'assistant', 'tool', 'function']
            if message_dict['role'] not in valid_roles:
                raise ValueError(f"{FILE_PATH} Converter.__init__() failed error - Invalid role '{message_dict['role']}' in message. Must be one of {valid_roles}.")

            # 验证 content 字段，支持 string 或 list (多模态)
            message_content = message_dict['content']

            if isinstance(message_content, str):
                # 文本内容，符合现有规范
                pass
            elif isinstance(message_content, list):
                # 多模态内容，进一步验证列表中的每个部分
                if not message_content:
                    raise ValueError(f"{FILE_PATH} Converter.__init__() failed error - Multimodal content list cannot be empty.")

                for part_idx, part in enumerate(message_content):
                    if not isinstance(part, dict):
                        raise ValueError(f"{FILE_PATH} Converter.__init__() failed error - Multimodal content part at index {part_idx} must be a dictionary.")
                    if 'type' not in part:
                        raise ValueError(f"{FILE_PATH} Converter.__init__() failed error - Multimodal content part at index {part_idx} must have a 'type' key.")

                    part_type = part['type']
                    if part_type == 'text':
                        if 'text' not in part or not isinstance(part['text'], str):
                            raise ValueError(f"{FILE_PATH} Converter.__init__() failed error - Text content part at index {part_idx} must have a 'text' (string) key.")
                    elif part_type == 'image_url':
                        if 'image_url' not in part or not isinstance(part['image_url'], dict):
                            raise ValueError(f"{FILE_PATH} Converter.__init__() failed error - Image content part at index {part_idx} must have an 'image_url' (dict) key.")
                        
                        image_url_obj = part['image_url']
                        if 'url' not in image_url_obj or not isinstance(image_url_obj['url'], str):
                            raise ValueError(f"{FILE_PATH} Converter.__init__() failed error - image_url object at index {part_idx} must have a 'url' (string) key.")
                        
                        if 'detail' in image_url_obj and not isinstance(image_url_obj['detail'], str):
                            raise ValueError(f"{FILE_PATH} Converter.__init__() failed error - image_url detail at index {part_idx} must be a string.")
                        # detail 字段是可选的，没有则不作处理
                    else:
                        raise ValueError(f"{FILE_PATH} Converter.__init__() failed error - Unknown content part type '{part_type}' at index {part_idx}. Expected 'text' or 'image_url'.")
            else:
                raise ValueError(f"{FILE_PATH} Converter.__init__() failed error - Message content must be a string or a list of content parts.")
            
            return message_dict # 返回验证过的消息字典


        if isinstance(content, dict):
            # 如果 content 是单个字典，直接验证并添加到 messages_list
            messages_list.append(_validate_single_message_dict(content))
        elif isinstance(content, list):
            # 如果 content 是字典列表，遍历每个字典进行验证并添加到 messages_list
            if not content: # 确保 content 列表不为空
                raise ValueError(f"{FILE_PATH} Converter.__init__() failed error - Content list cannot be empty.")
            for cont in content:
                messages_list.append(_validate_single_message_dict(cont))
        else:
            raise TypeError(f"{FILE_PATH} Converter.__init__() failed error - content must be a dict or a list of dicts.")

        payload['messages'] = messages_list # 使用正确的键名

        # 处理 max_tokens 参数
        if max_tokens is not None:
            if isinstance(max_tokens, int) and max_tokens >= 0:
                payload['max_tokens'] = max_tokens
            else:
                raise ValueError(f"{FILE_PATH} Converter.__init__() failed error - max_tokens must be a non-negative integer.")

        # 处理 temperature 参数
        if temperature is not None:
            if isinstance(temperature, (float, int)) and 0 <= temperature <= 2: # OpenAI allows temperature up to 2.0
                payload['temperature'] = float(temperature)
            else:
                raise ValueError(f"{FILE_PATH} Converter.__init__() failed error - temperature must be between 0 and 2.0.")

        # 处理 top_p 参数
        if top_p is not None:
            if isinstance(top_p, (float, int)) and 0 <= top_p <= 1:
                payload['top_p'] = float(top_p)
            else:
                raise ValueError(f"{FILE_PATH} Converter.__init__() failed error - top_p must be between 0 and 1.0.")

        if seed is not None:
            if isinstance(seed, int):
                payload['seed'] = seed
            else:
                raise ValueError(f"{FILE_PATH} Converter.__init__() failed error - seed must be an integer.")

        # 处理 n 参数
        if n is not None:
            if isinstance(n, int) and n >= 1: # n 通常至少为 1
                payload['n'] = n
            else:
                raise ValueError(f"{FILE_PATH} Converter.__init__() failed error - n must be a positive integer.")

        payload['stream'] = stream

        self.payload = payload

