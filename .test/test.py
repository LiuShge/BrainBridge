from typing import Literal, Dict, List, TypedDict
import os, json

import brainbridge.utils.timer as timer
import brainbridge.lib.runtime.provider_converter.converter as converter
import brainbridge.lib.runtime.requests_core.request_core as rq

class Message(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str

def get_information()-> Dict[Literal["url", "token", "model"], str|None]:
    try:
        with open("./.info", "r") as f:
            lines = f.readlines()
            info = {}
            for line in lines:
                key, value = line.strip().split(":", 1)
                info[key.strip()] = value.strip()
            return info
    except FileNotFoundError:
        return {"url": None, "token": None, "model": None}

def write_information(url: str|None, token: str|None, model: str|None):
    with open("./.info", "w") as f:
        if url: f.write(f"url: {url}\n")
        if token: f.write(f"token: {token}\n")
        if model: f.write(f"model: {model}\n")
        
def build_payload(model: str, messages: List[Message], stream: bool = False) -> converter.Converter:
    return converter.Converter(
        provider="openai_completion",
        model=model,
        messages=messages,
        stream=stream,
    )

def build_headers(token: str) -> Dict[str, str]:
    return converter.Operator.HeadersBuilder.builder(
        api_token=token,
        include_accept=True,
    )

def get_chat_list() -> List[str]:
    if not os.path.exists("./histories"):
        os.makedirs("./histories")
    return [f[:-5] for f in os.listdir("./histories") if f.endswith(".json")]

def save_chat(title: str|None, messages: List[Message]) -> str:
    if title is None:
        _time = timer.Time.f_time({'Y','M','D','h','m','s'})
        title = f"{_time['Y']}-{_time['M']}-{_time['D']}_{_time['h']}:{_time['m']}:{_time['s']}"
    if not os.path.exists("./histories"):
        os.makedirs("./histories")
    with open(f"./histories/{title}.json", "w") as f:
        f.write(json.dumps(messages))
    return title

def display_chat(messages: List[Message]):
    print("\033[H\033[2J", end="")
    print("="*15+'\n'+"CHAT START\n"+"="*15+'\n')
    if messages:
        for msg in messages:
            print(f"\033[1;36m{msg['role'].upper()}\033[0m: \033[1;37m{msg['content']}\033[0m\n")

_rq = rq.Request(timeout=100)
flags = ["/help", "/exit", "/model", "/rm_last_msg", "/clear_all", "/new_chat", "/mk_title", "/save_chat", "/select_chat"]
HELPS = """This is a simple command-line chat interface. You can type your messages and receive responses from the AI model. Here are the available commands:\n\
Here are the available commands:\n\
/help: Show this help message\n\
/exit: Exit the chat\n\
/model: Change the AI model\n\
/rm_last_msg: Remove the last message\n\
/clear_all: Clear all messages\n\
/new_chat: Start a new chat\n\
/mk_title: Set a title for the current chat\n\
/save_chat: Save the current chat\n\
/select_chat: Select a saved chat\n
"""
def main():
    info = get_information()
    if not all(info.values()):
        print("Please provide the following information:")
        url = input("URL: ")
        token = input("Token: ")
        model = input("Model: ")
        write_information(url, token, model)
    else:
        url = info["url"]
        token = info["token"]
        model = info["model"]

    title = None
    messages: List[Message] = []

    print("="*15+'\n'+"CHAT START\n"+"="*15+'\n')
    while True:
        user_input = input("\033[1;36mUSER\033[0m: \033[1;37m")
        print("\033[0m", end="")
        if user_input in flags:
            match user_input:
                case "/help":
                    print("="*15+'\n'+HELPS+'='*15+'\n')
                case "/exit":
                    print("Exiting the chat. Goodbye!")
                    break
                case "/model":
                    model = input("Enter the new model: ")
                    print(f"Model changed to {model}")
                    write_information(url, token, model)
                case "/rm_last_msg":
                    if messages:
                        rmd_msg = messages.pop()
                        print("\b"*len(rmd_msg['content']+rmd_msg['role']+": "), end="")
                    else:
                        print("\033[1;31mNo messages to remove.\033[0m")
                case "/clear_all":
                    messages.clear()
                    print("\033[1;31mAll messages deleted.\033[0m")
                    timer.Time.sleep(1)
                    display_chat(messages)
                case "/new_chat":
                    title = save_chat(title, messages)
                    messages.clear()
                    title = None
                    print("\033[1;31mNew chat started.\033[0m")
                    timer.Time.sleep(1)
                    display_chat(messages)
                case "/mk_title":
                    title = input("\nEnter the title for the current chat: ")
                case "/save_chat":
                    title = save_chat(title, messages)
                    print(f"\033[1;32mChat saved as '{title}'.\033[0m")
                case "/select_chat":
                    chat_list = get_chat_list()
                    if not chat_list:
                        print("\033[1;31mNo saved chats available.\033[0m")
                    else:
                        print("\nAvailable chats:")
                        for idx, chat_title in enumerate(chat_list):
                            print(f"{idx + 1}. {chat_title}")
                        selection = input("Select a chat by number: ")
                        if selection.isdigit() and 1 <= int(selection) <= len(chat_list):
                            selected_chat = chat_list[int(selection) - 1]
                            with open(f"./histories/{selected_chat}.json", "r") as f:
                                messages = json.loads(f.read())
                            title = selected_chat
                            print(f"\033[1;32mChat '{selected_chat}' loaded.\033[0m")
                            timer.Time.sleep(1)
                            display_chat(messages)
                        else:
                            print("\033[1;31mInvalid selection.\033[0m")
        else:
            messages.append(Message(role="user", content=user_input))
            payload = build_payload(model, messages, stream=True)
            headers = build_headers(token)
            resp = _rq.request_sse(
                'POST',
                url,
                headers=headers,
                json=payload.information,
            )
            try:
                print("\033[1;36mASSISTANT\033[0m: ", end="")
                chunks: List[str] = []
                for chunk in resp:
                    event_data = chunk.get("data", "").strip()
                    if not event_data:
                        continue
                    if event_data == "[DONE]":
                        break

                    rsp = converter.Operator.ResponseUnwrap.unwrap(
                        "openai_completion",
                        json.loads(event_data),
                    )
                    text = rsp.get("response_text")
                    if text:
                        print(f"\033[1;37m{text}\033[0m", end="", flush=True)
                        chunks.append(text)
                print()
                messages.append(Message(role="assistant", content="".join(chunks)))

            except Exception as e:
                print(f"\033[1;31mError processing response: {e}\033[0m")

if __name__ == "__main__":
    main()
