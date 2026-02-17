# BrainBridge

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg?style=flat-square)

**A robust, modular Python framework bridging backend logic and user-facing applications.**

[Features](#-key-features) • [Installation](#-getting-started) • [Usage](#-usage-examples) • [Configuration](#-configuration)

</div>

---

## 📖 Overview

**BrainBridge** features a high-performance network layer with SSE support, a unified AI provider argument converter, and a suite of terminal-based utility tools. It follows a strict modular architecture separating runtime libraries from static utilities, ensuring scalability and ease of maintenance.

---

## 📂 Project Structure

The project follows a strict modular architecture.

```text
BrainBridge/src
├── public
│   ├── run_lib                 # [Dynamic] Runtime Libraries
│   │   ├── files_manager       # File I/O abstractions
│   │   ├── mini_tools          # Utilities (TUI, Timer, Backups)
│   │   ├── provider_converter  # AI API Argument Normalization
│   │   └── requests_core       # Advanced HTTP Client (Threaded/SSE)
│   └── static_lib              # [Static] Libraries
│       ├── checker             # Integrity & Version Checking
│       ├── information         # Configuration & Env Info
│       └── logger              # Centralized Logging
├── GUI                         # Graphical User Interface (Pyside/Tkinter)
├── stubs                       # Type Hinting Stubs (.pyi)
└── .test                       # Unit Tests & Sandbox
```

---

## ✨ Key Features

### 1. 🌐 Advanced Network Layer (`requests_core`)
A thread-safe wrapper around `requests` optimized for stability and streaming.
- **SSE Support**: Native handling of Server-Sent Events for AI streaming responses.
- **Thread Pool**: `RequestPool` for executing concurrent GET/POST tasks.
- **Robust Error Handling**: Built-in retry logic and detailed logging.

### 2. 🧠 AI Provider Converter (`provider_converter`)
A middleware engine that normalizes arguments between different AI providers.
- **Type Safety**: Strictly validates input types (e.g., messages, model) against provider configs.
- **Argument Mapping**: Automatically maps generic arguments to provider-specific keys.
- **Response Unwrapping**: Standardizes response formats from complex nested JSON.

### 3. 🖥️ Interactive TUI Tools (`mini_tools`)
- **Decision Panel**: A keyboard-interactive (WASD/Arrows) terminal menu system.
- **Files Convergence**: Packs/unpacks directory trees into single portable text files (Base64 encoded) with SHA256 integrity checks.
- **High-Precision Timer**: Benchmarking tool with customizable decimal precision.

### 4. 🛡️ Integrity & Security (`checker`)
- **Self-Healing**: Detects corrupted files via hash mismatch and restores them from backups.
- **Strict Environment**: Enforces Python version compatibility.

---

## 🚀 Getting Started

### Prerequisites
- **Python**: 3.12 or higher (Targeting features up to Python 3.14).
- **Dependencies**: `requests`, `pynput` (for TUI).

### Installation
Clone the repository and install dependencies:

```bash
git clone https://github.com/your-username/BrainBridge.git
cd BrainBridge
pip install -r requirements.txt
```

---

## 📖 Usage Examples

### 1. HTTP Requests with Logging

Use the `Request` class for enhanced HTTP operations.

```python
from public.run_lib.requests_core.request_core import Request

# Initialize with logging enabled
req = Request(enable_logging=True, timeout=10)

# Simple GET
response = req.get("https://api.example.com/data")
print(f"Status: {response.status_code}")

# Server-Sent Events (SSE) for AI Streams
# Note: Using POST method for AI endpoints usually requires a JSON payload
sse_url = "https://api.openai.com/v1/chat/completions"
for event in req.request_sse(method="POST", url=sse_url, json={...}):
    print(f"Received chunk: {event.get('data')}")
```

### AI Argument Conversion

Standardize inputs for different LLM providers using Converter.

```python
from public.run_lib.provider_converter.converter import Converter

try:
    # Convert generic arguments to OpenAI-specific format
    conv = Converter(
        provider="openai",
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}]
    )
    payload = conv.information
    print(f"Payload ready for API: {payload}")

except ValueError as e:
    print(f"Validation Error: {e}")
```

### Terminal Decision Panel

Create interactive CLI menus with keyboard navigation.

```python
from public.run_lib.mini_tools.decision_panel import DecisionPanelPage

page = DecisionPanelPage(
    title="Main Menu",
    prompt_text="Please select an operation",
    operation_tips="Use W/S to navigate, Enter to confirm"
)

page.set_options([
    {"prompt": "Start Server", "output": "start"},
    {"prompt": "Configuration", "output": "config"},
    {"prompt": "Exit", "output": "exit"}
])

result = page.run_once()
print(f"User selected: {result}")
```

### 4. File Backup & Aggregation

Pack a folder into a single file for transport or backup.

```python
from public.run_lib.mini_tools.files_convg import aggregate_to_backup, unpack_from_backup

# 1. Backup
# Define structure: { "source_dir": ["specific_file_path", ...] }
tree_structure = {
    "/path/to/src": ["/path/to/src/file1.txt"]
}
aggregate_to_backup(tree_structure, "backup.bb")

# 2. Restore
unpack_from_backup("backup.bb", "/path/to/restore_dir")
```

## ⚙️ Configuration

The framework uses a dual-layer configuration system located in `src/public/static_lib/information/config`:

| Config Type | File | Description |
| :--- | :--- | :--- |
| **System Config** | `sys_conf` | Default fallback settings. |
| **User Config** | `user_conf` | User overrides (**ignored by git** to protect local secrets). |

---

## 🛠 Development

### Type Stubs
The project includes comprehensive `.pyi` stub files in `src/stubs` to support static type checking with **mypy** or **PyCharm**.

### Testing
Run the internal test suite:

```bash
python -m src.public.run_lib.requests_core.thread_requests
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).