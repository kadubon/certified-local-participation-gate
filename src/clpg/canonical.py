"""Canonical JSON helpers."""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel


def to_jsonable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return to_jsonable(value.model_dump(mode="json", exclude_none=False))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]
    if isinstance(value, set):
        return sorted((to_jsonable(item) for item in value), key=lambda item: canonical_json(item))
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(
        to_jsonable(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def canonical_bytes(value: Any) -> bytes:
    return canonical_json(value).encode("utf-8")
