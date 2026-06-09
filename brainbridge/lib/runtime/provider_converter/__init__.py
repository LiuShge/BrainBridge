"""Provider conversion APIs for BrainBridge runtime."""

from typing import Any, Dict

from .converter import Converter, Operator, _ConfigEngine
from .user_config import (
    read_user_provider_config,
    update_user_provider_config,
    write_user_provider_config,
)


def build_headers(api_token: str, include_accept: bool = False) -> Dict[str, str]:
    """Build standard request headers for provider API calls."""
    return Operator.HeadersBuilder.builder(api_token=api_token, include_accept=include_accept)


def unwrap_response(provider: str, response: Any) -> Dict[str, Any]:
    """Normalize a provider response into BrainBridge's standard structure."""
    return Operator.ResponseUnwrap.unwrap(provider=provider, response=response)


def list_providers() -> list[str]:
    """Return the currently available provider names from merged configuration."""
    _, escape_table = _ConfigEngine.get_configs()
    return sorted(escape_table.keys())


def provider_exists(provider: str) -> bool:
    """Return True when a provider is defined in the merged configuration."""
    return provider in set(list_providers())

__all__ = [
    "Converter",
    "Operator",
    "build_headers",
    "unwrap_response",
    "list_providers",
    "provider_exists",
    "read_user_provider_config",
    "write_user_provider_config",
    "update_user_provider_config",
]
