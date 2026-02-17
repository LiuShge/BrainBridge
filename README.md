# 🧠 BrainBridge

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg?style=flat-square&logo=python&logoColor=white)
![Type Safety](https://img.shields.io/badge/type%20safety-100%25%20Stubbed-success.svg?style=flat-square)
![Architecture](https://img.shields.io/badge/architecture-Self--Contained-purple.svg?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)

**A High-Precision, Self-Contained LLM Runtime Protocol.**

*Designed for developers who demand absolute control over their AI infrastructure.*

[Philosophy](#-design-philosophy) • [Architecture](#-system-architecture) • [Features](#-core-capabilities) • [Usage](#-usage-examples) • [Origin](#-the-origin)

</div>

---

## 📖 Introduction

**BrainBridge** is not a typical Python library; it is a **portable runtime environment** designed to bridge the gap between complex Backend Logic and User-Facing Applications in the LLM era.

Unlike massive frameworks that abstract away execution details, BrainBridge offers a **transparent, white-box approach**. It rejects the "Dependency Hell" of modern Python development by implementing a custom import system, a hand-crafted threading engine, and a configuration-driven adaptation layer.

Whether you are building a private AI agent, a CLI tool, or a specialized data pipeline, BrainBridge provides the skeleton to build robust, linear, and type-safe applications without the bloat.

---

## 💎 Design Philosophy

### 1. Atomic Modularity & Transparency
Instead of monolithic logic, BrainBridge is built on **Atomic Modules**. Each component (Logger, Timer, Request Core) is designed to do one thing perfectly with zero hidden side effects. The code is kept linear and readable, allowing for instant debugging and "surgical" modifications.

### 2. The "Async Defense" Strategy
We consciously chose **Threaded Blocking I/O** over `asyncio`.
* **Reasoning:** Asynchronous code introduces "Function Coloring" (viral complexity) that fragments business logic.
* **Solution:** By using a highly optimized `RequestPool` (Threading), we achieve high concurrency (sufficient for LLM I/O) while keeping the codebase **linear, predictable, and easy to maintain**.

### 3. Static Contracts in a Dynamic World
BrainBridge utilizes extensive runtime magic (dynamic path injection, config loading), but it enforces strict development discipline via **Type Stubs (`.pyi`)**.
* Every dynamic module is mirrored by a static stub.
* This ensures that while the runtime is flexible, your IDE provides **100% accurate type hinting and autocompletion**, catching errors before execution.

### 4. Environment Autonomy
BrainBridge is designed to be **"Green Software"**. It does not rely on global `site-packages` for its core logic. It carries its own runtime environment, meaning you can clone the folder to any machine with Python, and it just works—no installation required.

---

## 🏗 System Architecture

The project structure is strictly divided into **Dynamic Logic (`run_lib`)** and **Static Infrastructure (`static_lib`)**.

```text
BrainBridge/
├── src/
│ ├── public/
│ │ ├── run_lib/ # [The Engine]
│ │ │ ├── requests_core/ # Advanced HTTP Client (Threaded, SSE, Retry)
│ │ │ ├── provider_converter/ # LLM Argument Normalization Middleware
│ │ │ └── mini_tools/ # Atomic utilities (TUI, Timer, FileConvg)
│ │ └── static_lib/ # [The Foundation]
│ │   ├── checker/ # Self-Healing Integrity & Version Control
│ │   ├── logger/ # Zero-dependency Structured Logging
│ │   └── information/ # Dual-layer Configuration (Sys/User)
│ └── stubs/ # [The Contract] Hand-written Type Definitions
└── main.py # Entry point with Environment Injection
```

---

## ⚡ Core Capabilities

### 🌐 Intelligent Network Layer
* **Native SSE Support:** Hand-crafted stream parser for Server-Sent Events, essential for LLM streaming responses (e.g., ChatGPT style typing effect).
* **Threaded Request Pool:** Capable of dispatching parallel requests without the complexity of `async/await`.
* **Detailed Lifecycle Logging:** Every request is tracked, timed, and logged for full observability.

### 🧠 Universal Provider Converter
* **Config-Driven Adapter:** Maps generic arguments (e.g., `messages`, `model`) to provider-specific payloads (OpenAI, Anthropic, DeepSeek) using `escape_table.json`.
* **Type Guarding:** Automatically validates input types against the provider's schema before the request is even sent.

### 🖥️ Native Terminal UI (TUI)
* **Decision Panel:** A keyboard-interactive (WASD/Arrow keys) menu system implemented without heavy external UI libraries.
* **Loading Bars:** Customizable, high-precision progress indicators.

### 📦 File Convergence Protocol (`.bb`)
* **Context Packing:** Aggregates complex directory trees into a single Base64-encoded stream.
* **Use Case:** Perfect for feeding an entire codebase into an LLM context window for analysis.

---

## 💻 Usage Examples

### 1. The Core Loop: LLM Interaction
This example demonstrates how to convert arguments, send a request, and handle the response log.

```python
# Inject internal paths first
from src.set_source_dir import _set_source_dir
_set_source_dir()

from src.public.run_lib.requests_core.request_core import Request
from src.public.run_lib.provider_converter.converter import Converter

# 1. Normalize Arguments for OpenAI
# This validates types and maps keys based on 'escape_table.json'
try:
  llm_payload = Converter(
    provider="openai",
    model="gpt-4-turbo",
    messages=[{"role": "user", "content": "Explain Quantum Mechanics."}],
    stream=True
    ).information
except ValueError as e:
  print(f"Config Error: {e}")
exit(1)

# 2. Initialize Network Engine
req = Request(enable_logging=True, timeout=30)

# 3. Execute SSE Stream Request
print("Receiving Stream:")
url = "https://api.openai.com/v1/chat/completions"
# Headers would typically include Authorization
headers = {"Authorization": "Bearer sk-..."}

for event in req.request_sse(method="POST", url=url, json=llm_payload, headers=headers):
  # 'event' is a parsed dictionary: {'id':..., 'event':..., 'data':...}
  print(event.get('data'), end="", flush=True)

# 4. Check Logs
print(f"\nTotal Logs: {len(req)}")
```

### 2. Interactive Terminal Menu
Build robust CLI tools with the built-in Decision Panel.

```python
from src.public.run_lib.mini_tools.decision_panel import DecisionPanelPage

# Initialize the TUI Page
menu = DecisionPanelPage(
  title="BrainBridge Control Center",
  prompt_text="Select Deployment Mode",
  operation_tips="[W/S] Navigate [Enter] Confirm"
  )

# Define Options
menu.set_options([
  {"prompt": "🚀 Production Mode", "output": "prod"},
  {"prompt": "🛠️ Debug Mode", "output": "debug"},
  {"prompt": "📂 Safe Mode (No Network)", "output": "safe"}
  ])

# Run the Event Loop
selected_mode = menu.run_once()
print(f"System starting in: {selected_mode}")
```

### 3. Codebase Snapshot (Packing)
Pack a project into a single token-efficient string for LLM analysis.

```python
from src.public.run_lib.mini_tools.files_convg import aggregate_to_backup

# Define the tree to pack
target_tree = {
  "./src": ["./src/main.py", "./src/utils.py"]
  }

# Generate snapshot
aggregate_to_backup(target_tree, output_backup_path="./snapshots/v1.bb")
print("Backup complete. Hash verified.")
```

---

## 👨‍💻 The Origin

**BrainBridge** is an experiment in **High-Efficiency Engineering**.

It was architected and implemented in a **4-day sprint** by a **14-year-old developer** in collaboration with AI.

The goal was not to build "just another wrapper," but to prove that with a clear architectural vision (Atomic Design, Static Contracts) and modern AI assistance, one can build a professional-grade, self-contained runtime that rivals complex commercial frameworks in stability and control.

---

## 📄 License

This project is licensed under the **MIT License**.
*Use it, fork it, study it. Just keep it clean.*


`Developers in China, if you have a significant interest in this project, you can sponsor the developer... As a student, he has very limited funds to invest in development...`
