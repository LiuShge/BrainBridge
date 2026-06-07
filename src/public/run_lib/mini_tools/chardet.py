"""Small in-repo replacement for the subset of chardet used by BrainBridge."""

from __future__ import annotations

from typing import Any, Dict, Optional


DetectionResult = Dict[str, Optional[Any]]

__all__ = ["DetectionResult", "detect"]


_BOM_ENCODINGS: tuple[tuple[bytes, str], ...] = (
    (b"\xef\xbb\xbf", "utf-8-sig"),
    (b"\xff\xfe\x00\x00", "utf-32-le"),
    (b"\x00\x00\xfe\xff", "utf-32-be"),
    (b"\xff\xfe", "utf-16-le"),
    (b"\xfe\xff", "utf-16-be"),
)

_CANDIDATES: tuple[tuple[str, float, Optional[str]], ...] = (
    ("utf-8", 0.99, None),
    ("utf-16", 0.80, None),
    ("utf-16-le", 0.75, None),
    ("utf-16-be", 0.75, None),
    ("gb18030", 0.72, "Chinese"),
    ("cp1252", 0.55, None),
)


def detect(byte_string: bytes) -> DetectionResult:
    """Return a chardet-like detection mapping for a byte string."""
    if not isinstance(byte_string, (bytes, bytearray)):
        raise TypeError("detect() expects a bytes-like object")

    data = bytes(byte_string)
    if not data:
        return {"encoding": None, "confidence": 0.0, "language": None}

    for bom, encoding in _BOM_ENCODINGS:
        if data.startswith(bom):
            return {"encoding": encoding, "confidence": 1.0, "language": None}

    if all(byte < 0x80 for byte in data):
        return {"encoding": "ascii", "confidence": 1.0, "language": None}

    for encoding, confidence, language in _CANDIDATES:
        try:
            data.decode(encoding)
        except UnicodeDecodeError:
            continue
        return {"encoding": encoding, "confidence": confidence, "language": language}

    return {"encoding": "latin-1", "confidence": 0.20, "language": None}
