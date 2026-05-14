"""Digest helpers for canonical CLPG objects."""

from __future__ import annotations

import hashlib
from typing import Any

from clpg.canonical import canonical_bytes


def sha256_digest(value: Any) -> str:
    payload = value if isinstance(value, bytes) else canonical_bytes(value)
    return "sha256:" + hashlib.sha256(payload).hexdigest()
