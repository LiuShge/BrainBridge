import os

from src.public.run_lib.provider_converter.converter import Converter
from src.public.run_lib.requests_core.request_core import Request
from src.public.static_lib.logger.log_core import Logger, LogLevels

print("--- Testing editable-install style imports ---")
print(f"Working directory: {os.getcwd()}")
print(f"Converter class found: {Converter.__name__}")
print(f"Request class found: {Request.__name__}")

test_logger = Logger(level=LogLevels.INFO, text="Import test success via package imports")
print(f"Logger class found: {test_logger.__class__.__name__}")
print("Log Output:")
print(test_logger.text_log_builder())
