"""CLPG exception types."""

from __future__ import annotations


class CLPGError(Exception):
    """Base exception for CLPG runtime errors."""


class LedgerError(CLPGError):
    """Raised when a ledger cannot be appended or verified."""


class ConformanceError(CLPGError):
    """Raised when conformance fixtures do not match expected behavior."""
