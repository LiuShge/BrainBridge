from simple_import import change_sys_path
change_sys_path(to_runlib=True)

from requests_core.request_core import Request
from provider_converter.converter import Converter,Operator

from json import loads

requester = Request(timeout=120)
headers_builder = Operator.HeadersBuilder()
output_parser = Operator.ResponseUnwarp()

_history = []

while True:
    reasoning = False
    user_input = input("User: ")
    if user_input.replace(" ",'').lower() in ['break','stop','exit','bye']:
        break
    _history.append({"role": "user","content": user_input})
    payload = Converter("openai_completion", model = "openai/gpt-oss-20b", messages = _history).information
    headers = headers_builder.builder(api_token="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")
    _resp = requester.request_sse("POST","https://integrate.api.nvidia.com/v1/chat/completions",json=payload,headers=headers)
    assistant_output = ''
    think_len = 0
    print("Assistant: ",end='')
    for resp in _resp:
        if resp["data"].replace("\n", '') != "[DONE]":
            output = output_parser.unwarp("openai_completion",
                                          loads(resp["data"]))
            if not output['response_usage']:
                if "reasoning" in output["raw_response"]["choices"][0]["delta"].keys():
                    if not reasoning:
                        reasoning = True
                        print("\n<think/>\n",end="")
                    think = output["raw_response"]["choices"][0]["delta"]["reasoning"]
                    think_len += len(think)
                    print(think, end='')
                    if think_len >= 120:
                        print('')
                        think_len -= 120
                else:
                    if reasoning:
                        reasoning = False
                        print("\n</think>\n")
                if output["response_text"]:
                    print(output["response_text"],end='')
                    assistant_output+=output["response_text"]
            if output.get("response_usage"):
                print(f"\nUsage: {output['response_usage']}")