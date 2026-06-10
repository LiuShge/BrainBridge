"""Shared ignore normalization and matching helpers for file utilities."""

from __future__ import annotations

from typing import Literal

IgnoreKind = Literal["dir", "file"]
IgnoreSpec = str | list[str] | dict[IgnoreKind, list[str]] | None
NormalizedIgnores = dict[IgnoreKind, list[str]]

__all__ = [
    "IgnoreKind",
    "IgnoreSpec",
    "NormalizedIgnores",
    "normalize_ignores",
    "should_ignore_name",
]


def _coerce_ignore_words(words: list[str], kind: IgnoreKind) -> list[str]:
    normalized: list[str] = []
    for word in words:
        if not isinstance(word, str):
            raise TypeError(f"ignores[{kind!r}] entries must be str")
        normalized.append(word)
    return normalized


def normalize_ignores(ignores: IgnoreSpec) -> NormalizedIgnores:
    """Normalize all supported ignore shapes into a directory/file mapping."""
    normalized: NormalizedIgnores = {"dir": [], "file": []}

    if ignores is None:
        return normalized

    if isinstance(ignores, str):
        normalized["file"] = [ignores]
        return normalized

    if isinstance(ignores, list):
        normalized["file"] = _coerce_ignore_words(ignores, "file")
        return normalized

    if isinstance(ignores, dict):
        allowed_keys = {"dir", "file"}
        extra_keys = set(ignores.keys()) - allowed_keys
        if extra_keys:
            raise ValueError(f"Unsupported ignore keys: {sorted(extra_keys)!r}")

        dir_words = ignores.get("dir", [])
        file_words = ignores.get("file", [])
        if not isinstance(dir_words, list):
            raise TypeError("ignores['dir'] must be a list of str")
        if not isinstance(file_words, list):
            raise TypeError("ignores['file'] must be a list of str")

        normalized["dir"] = _coerce_ignore_words(dir_words, "dir")
        normalized["file"] = _coerce_ignore_words(file_words, "file")
        return normalized

    raise TypeError("ignores must be None, str, list[str], or dict[str, list[str]]")


def should_ignore_name(name: str, kind: IgnoreKind, normalized_ignores: NormalizedIgnores) -> bool:
    """Return True when a basename contains any ignore token for the given kind."""
    if kind not in {"dir", "file"}:
        raise ValueError(f"Unsupported ignore kind: {kind!r}")
    return any(word in name for word in normalized_ignores[kind])
