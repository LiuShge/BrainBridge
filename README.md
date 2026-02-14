• # BrainBridge
  Provider-agnostic AI API middleware that normalizes inputs and outputs via JSON-configured rules.

  ## Core Features
  - 🧩 Decoupled transformers: `Converter` normalizes inputs, `Operator.ResponseUnwarp` normalizes outputs.
  - 🧷 Type safety: `.pyi` stubs in `src/stubs/` for IDE support and static checking.
  - 🗂️ JSON-driven matching: provider rules in `config/sys_conf/base_arg_match.json` and schemas in `config/sys_conf/escape_table.json`.

  ## Project Architecture
      .
      ├─ src/
      │  ├─ public/
      │  │  ├─ run_lib/
      │  │  │  ├─ provider_converter/   # input mapping, type validation, response unwrapping
      │  │  │  ├─ requests_core/        # request wrapper, logging, SSE streaming
      │  │  │  └─ files_manager/        # JSON/file helpers used by config loader
      │  │  └─ static_lib/              # shared static helpers (checker, logger, info)
      │  ├─ stubs/                      # .pyi type stubs mirroring run_lib APIs
      │  ├─ _main_test.py               # streaming CLI example
      │  └─ simple_import.py            # dynamic sys.path loader for run_lib/static_lib
      ├─ config/
      │  └─ sys_conf/
      │     ├─ base_arg_match.json      # generic -> provider input/output paths
      │     └─ escape_table.json        # provider schemas for type validation
      └─ storage/                       # runtime logs/artifacts (generated)

  Core flow:
  Input -> Converter (normalize + type check) -> Request (send JSON payload) -> External API -> ResponseUnwarp (parse output)

  Notes:
  - Serialization: `Request.post` and `Request.request_sse` pass `json=...`; `requests` handles JSON encoding.
  - Error handling: `Converter` raises `ValueError` for missing essentials, unsupported providers, or type mismatch; `_ConfigEngine` validates config and falls back to `sys_conf` on
  failure; `Request` logs and re-raises exceptions; `request_sse` uses `raise_for_status()`.
  - There is no standalone requests_builder module yet; payload assembly currently lives in `Converter` plus the `requests_core` call sites.

  ## Quick Start
  Python 3.14+ is expected (modern typing features supported).
```python
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
                                                    url="https://api.***.com/v1/chat/completions",
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
```
  ## For Developers
  - Provider rules live in `config/sys_conf/`. Edit `base_arg_match.json` for input/output mappings and `escape_table.json` for schema/type rules.
  - `ConfigEngine` merges `config/sys_conf` with `config/user_conf` when present and validates the result before use.
  - `.pyi` files under `src/stubs/` mirror the runtime modules; they are for type checking only and are not imported at runtime.

  ## Roadmap
  - *TODO*: async request core and streaming
  - *TODO*: benchmarking + profiling harness
