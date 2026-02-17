# 🧠 BrainBridge

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg?style=flat-square&logo=python&logoColor=white)
![Architecture](https://img.shields.io/badge/architecture-Micro--Modular-purple.svg?style=flat-square)
![Module Size](https://img.shields.io/badge/module%20size-%3C2kb-red.svg?style=flat-square)
![Type Safety](https://img.shields.io/badge/type%20safety-100%25%20Stubbed-success.svg?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)

**An uncompromising, self-contained LLM runtime protocol for those who demand absolute control.**

[Manifesto](#-manifesto) • [Architecture](#-architecture) • [Key Features](#-key-features) • [Quick Start](#-quick-start) • [Showcase](#-showcase)

</div>

---

## 🏴 Manifesto

**BrainBridge is not just a framework; it is a rebellion against "Dependency Hell".**

In an era where "Hello World" requires 500MB of `site-packages`, BrainBridge takes a different path. Built by a **14-year-old architect** in collaboration with AI, this project demonstrates what is possible when you refuse to compromise on performance and clarity.

* **We reject "Async Infection":** We use Threading + Blocking I/O to preserve architectural purity and linear logic.
* **We reject "Bloat":** Every core module is strictly kept under **2kb**.
* **We reject "Black Boxes":** No hidden logic. 100% transparent, self-governing runtime.

---

## 🏗 Architecture

BrainBridge bypasses standard package managers by implementing a **Custom Import Injection System**. It is designed to be a "Portable Runtime" — drop the folder anywhere, and it works.

```text
BrainBridge/
├── src/
│ ├── public/
│ │ ├── run_lib/ # [The Engine]
│ │ │ ├── requests_core/ # Hand-crafted HTTP/SSE Client (Threaded)
│ │ │ ├── provider_converter/ # LLM Argument Normalization Layer
│ │ │ └── mini_tools/ # Atomic utilities (TUI, Timer, FileConvg)
│ │ └── static_lib/ # [The Foundation]
│ │ ├── checker/ # Self-Healing Integrity Checkers
│ │ └── logger/ # Zero-dependency structured logging
│ └── stubs/ # [The Contract] Hand-written .pyi files
└── main.py # Entry point with auto-environment injection
```

---

## ✨ Key Features

### 1. ⚡ Atomic Micro-Modules (<2kb)
Engineered for **instant cold-start**. By stripping away metadata overhead and sticking to pure logic, BrainBridge starts faster than the Python interpreter can blink.

### 2. 🛡️ The "Async Defense" Strategy
We consciously chose **`requests` + `threading`** over `asyncio`.
* **Why?** To prevent the "Function Coloring Problem" from contaminating business logic.
* **Result:** Debuggable, linear code that handles concurrency (up to 50 threads) with zero mental overhead.

### 3. 📝 Strict Static Contracts (Stubs)
While the runtime is dynamic and flexible, the development experience is strictly typed.
* **100% .pyi Coverage:** Hand-maintained stub files ensure your IDE knows exactly what's happening, even with dynamic path injection.
* **Best of Both Worlds:** Python's flexibility at runtime, Rust-like discipline at compile time.

### 4. 🧩 The Universal Converter
A data-driven middleware that bridges your logic to any LLM provider (OpenAI, Anthropic, Local Models).
* **Config-Driven:** Add new models via JSON, not code.
* **Auto-Normalization:** Automatically maps generic `messages` to provider-specific payloads.

### 5. 📦 Portable "Green Software"
* **No Installation Required:** Uses runtime `sys.path` modification.
* **Self-Healing:** The `checker` module verifies file hashes on startup, ensuring the integrity of your portable environment.

---

## 🚀 Quick Start

**Prerequisite:** Python 3.12+ (We use modern syntax).

### 1. Clone (Don't Install)
BrainBridge is a runtime environment, not a library.

```bash
git clone https://github.com/your-username/BrainBridge.git
cd BrainBridge
# Install minimal dependencies (requests, pynput)
pip install -r requirements.txt
```

### 2. Run the Core

```python
# In your main.py
import sys
import os

# [Magic happens here] Inject runtime paths
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from public.run_lib.requests_core.request_core import Request
from public.run_lib.provider_converter.converter import Converter

# 1. Setup a Converter for OpenAI
conv = Converter(provider="openai", model="gpt-4", messages=[{"role": "user", "content": "Hi"}])

# 2. Fire a Request with Logging
req = Request(enable_logging=True)
response = req.get("https://api.openai.com/v1/chat/completions", headers=..., json=conv.information)

print(response.json())
```

---

## 🎨 Showcase

### The "Decision Panel" TUI
A keyboard-interactive terminal UI (WASD control), implemented with zero heavy UI libraries.

```python
from public.run_lib.mini_tools.decision_panel import DecisionPanelPage

page = DecisionPanelPage(title="BRAIN BRIDGE KERNEL", prompt_text="Select Module:")
page.set_options([
{"prompt": "Initialize Core", "output": "init"},
{"prompt": "System Check", "output": "check"},
{"prompt": "Deploy", "output": "deploy"}
])
selection = page.run_once()
```

### File Convergence Protocol (`.bb` format)
Pack entire directory trees into a single Base64 stream for easy context injection into LLMs.

```python
from public.run_lib.mini_tools.files_convg import aggregate_to_backup
# Turn a folder into a single string
aggregate_to_backup({"/src/core": ["file1.py", "file2.py"]}, "snapshot.bb")
```

---

## ⚙️ Configuration

We respect your secrets.
* **`sys_conf`**: Tracks system defaults.
* **`user_conf`**: (Git-ignored) Where your API keys live.

---

## 👨‍💻 Origin Story

> "I wanted a tool that respected my intelligence, not one that hid everything behind a `run()` function."

Developed in **4 days** of intense flow state by a **14-year-old developer** and an AI copilot. BrainBridge is an experiment in **High-Efficiency Engineering**—proving that with the right architecture, one person can build what usually takes a team.

---

## 📄 License

MIT License. **Copy it, fork it, break it.** Just don't make it bloated.
