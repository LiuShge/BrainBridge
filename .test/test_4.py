from json import loads

from brainbridge.run_lib.provider_converter.converter import Converter, Operator
from brainbridge.run_lib.requests_core.request_core import Request


def main() -> None:
    requester = Request(timeout=120)
    headers_builder = Operator.HeadersBuilder()
    output_parser = Operator.ResponseUnwrap()
    history = []

    while True:
        reasoning = False
        user_input = input("User: ")
        if user_input.replace(" ", "").lower() in ["break", "stop", "exit", "bye"]:
            break
        history.append({"role": "user", "content": user_input})
        payload = Converter("openai_completion", model="openai/gpt-oss-20b", messages=history).information
        headers = headers_builder.builder(
            api_token="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"
        )
        response_stream = requester.request_sse(
            "POST",
            "https://integrate.api.nvidia.com/v1/chat/completions",
            json=payload,
            headers=headers,
        )
        assistant_output = ""
        think_len = 0
        print("Assistant: ", end="")
        for resp in response_stream:
            if resp["data"].replace("\n", "") == "[DONE]":
                continue
            output = output_parser.unwrap("openai_completion", loads(resp["data"]))
            if not output["response_usage"]:
                delta = output["raw_response"]["choices"][0]["delta"]
                if "reasoning" in delta:
                    if not reasoning:
                        reasoning = True
                        print("\n<think/>\n", end="")
                    think = delta["reasoning"]
                    think_len += len(think)
                    print(think, end="")
                    if think_len >= 120:
                        print("")
                        think_len -= 120
                else:
                    if reasoning:
                        reasoning = False
                        print("\n</think>\n")
                if output["response_text"]:
                    print(output["response_text"], end="")
                    assistant_output += output["response_text"]
            if output.get("response_usage"):
                print(f"\nUsage: {output['response_usage']}")


if __name__ == "__main__":
    main()
