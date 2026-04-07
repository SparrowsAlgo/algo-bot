"""Small shared helpers."""

from __future__ import annotations

from typing import TypeVar

T = TypeVar("T")


def identity(value: T) -> T:
    """Return the input value unchanged."""
    return value
