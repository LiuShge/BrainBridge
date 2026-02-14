from simple_import import change_sys_path, restore_sys_path
change_sys_path(to_runlib=True)
from requests_core.request_core import Request
from provider_converter.converter import Converter
restore_sys_path()
import json

_history = []
MAX_HISTORY = 12

def main():
    def _history_adder(content: dict[str, str]):
        global _history
        _history.append(content)
    req_er = Request(timeout=120)
    while True:
        user_input = input("User: ")
        if user_input.lower() in ['stop','exit','break']:
            break
        message = {"role":"user","content":user_input,"name":"Serge"}
        _history_adder(message)
        vairy = {"Content-Type": "application/json","Authorization": "Bearer sk-****"}
        information = Converter("openai_completion", model ='gpt-5-nano', input = _history, stream = True)
        assistant_output = req_er.request_sse(method="POST",
                                              url="https://api.vectorengine.ai/v1/chat/completions",
                                              json=information.information, headers=vairy)

        print("\nAssistant:", end=' ')
        for i in assistant_output:
            raw_data = i.get('data', '').strip()
            if not raw_data or raw_data == "[DONE]":
                continue
            try:
                json_data = json.loads(raw_data)
                choices = json_data.get('choices', [])
                if choices:
                    delta = choices[0].get('delta', {})
                    content = delta.get('content', '')
                    if content:
                        print(str(content).encode('latin-1').decode('utf-8'), end='', flush=True)
                elif 'delta' in json_data:
                    print(json_data['delta'], end='', flush=True)
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                continue
        print('\n')
        if len(_history) > MAX_HISTORY:
            del _history[0]

if __name__ == "__main__":
    main()
