# BrainBridge Project Documentation

---

## Overview
**BrainBridge** is a Python-based, multifunctional toolkit designed to provide high-performance, modular, and extensible solutions for API request handling, data conversion, configuration management, and GUI prototyping. The project follows a clear directory structure and strict coding standards to ensure maintainability and scalability.

---

## Project Structure
The project root directory contains the following key directories and files:

```
BrainBridge/
├── config/ # Configuration files
│ ├── runtime_conf/ # Runtime configurations (editable)
│ ├── sys_conf/ # System default configurations (read-only)
│ └── user_conf/ # User-defined configurations (overrides system defaults)
├── storage/ # Runtime-generated data (logs, metadata, etc.)
├── src/ # Core source code
│ ├── public/ # Public modules
│ │ ├── run_lib/ # Runtime utilities (e.g., request handling, data conversion)
│ │ └── static_lib/ # Static utilities (shared helper functions)
│ ├── GUI/ # GUI prototypes
│ └── .tests/ # Test cases and sandbox
├── simple_import.py # Dynamic import utility script
├── launcher.py # Main launcher script
├── _launcher.py # Auxiliary launcher script
├── _reset.py # Reset script (cleans runtime data)
└── README.md # Project documentation
```

~~Actually, there is no readme file.~~

---

## Getting Started

### Environment Setup
1. **Activate the Virtual Environment**:
- **Windows (PowerShell)**:
```powershell
.\.venv\Scripts\Activate.ps1
```
- **Unix/MacOS**:
```bash
source .venv/Scripts/activate
```

2. **Install Dependencies**:
Use `pip` to install the required dependencies (if `requirements.txt` is available):
```bash
pip install -r requirements.txt
```

3. **Verify Import Paths**:
Run the `simple_import.py` script to ensure the dynamic import tool correctly recognizes `run_lib` and `static_lib`:
```bash
python simple_import.py
```

---

## Development Guidelines

### Coding Style
- **Naming Conventions**:
- Directories and modules: `snake_case` (e.g., `run_lib`).
- Classes: `PascalCase` (e.g., `Request`).
- Functions and variables: `snake_case` (e.g., `validate_message`).
- Constants: `UPPER_CASE` (e.g., `DEFAULT_TIMEOUT`).

- **Code Standards**:
- Use 4-space indentation.
- Public functions and classes **must** include Docstrings, following [PEP 257](https://peps.python.org/pep-0257/).
- Avoid magic numbers; document critical logic with comments or Docstrings.
- Ensure code passes `python -m py_compile` for syntax validation.

### Testing
- **Test Directory**: Test cases are located in `src/.tests/`.
- **Run Tests**: Use the following command to execute the sandbox test and verify the project structure:
```bash
python src/.tests/sandbox/test.py
```
- **Write Tests**: New test files must be named `test_*.py` and placed in `src/.tests/`.

---

## Configuration Management
The project configurations are categorized into three types, stored in the `config/` directory:
1. **Runtime Configurations** (`runtime_conf/`): Editable configurations for runtime environments.
2. **System Configurations** (`sys_conf/`): System default configurations (avoid modifying).
3. **User Configurations** (`user_conf/`): User-defined configurations that override system defaults.

⚠️ **Important**:
- **Do not** commit sensitive information (e.g., API keys, tokens) to the configuration directories.
- The `storage/` directory stores runtime-generated logs and data. Exclude it from version control.

---

## Contribution Guidelines

### Commit Messages
- **Format**: Use the `type(scope): summary` pattern. For example:
```
feat(request): add timeout parameter validation
fix(converter): handle empty content list
```
- **Single Topic**: Each commit should focus on a single feature or fix.

### Pull Requests (PRs)
- **Clear Descriptions**: PRs must detail the changes, their purpose, and their impact.
- **Test Commands**: List relevant test commands (e.g., `python simple_import.py` or sandbox tests).
- **Environment Changes**: If configurations (e.g., `config/*`) are modified, explain the changes.
- **UI Changes**: For modifications to `src/GUI/`, include screenshots if applicable.

---

## Common Commands

| Command | Description |
|--------------------------------------|---------------------------------------------|
| `python simple_import.py` | Verify dynamic import tool functionality. |
| `python src/.tests/sandbox/test.py` | Run sandbox tests to validate project structure. |
| `python -m py_compile src/*.py` | Check for syntax errors in source code. |
| `python launcher.py` | Start the main program. |

---

## How to Contribute
We welcome contributions to the **BrainBridge** project! Follow these steps:
1. Fork the repository and create a branch.
2. Adhere to the [Coding Style](#coding-style) and [Commit Guidelines](#commit-messages).
3. Write test cases and ensure all tests pass.
4. Submit a Pull Request with a detailed description of the changes.

---

## License
This project is licensed under the [MIT License](LICENSE) (if applicable).

---

## Contact
For questions or suggestions, please contact the project maintainers:
- **Email**: serge-workplace@outlook.com\sergewithteto@gmail.com
- **GitHub**: [BrainBridge](https://github.com/yourusername/BrainBridge)

---

**BrainBridge** aims to build an efficient, scalable, and maintainable Python toolkit. Thank you for your contributions and support! 🚀
