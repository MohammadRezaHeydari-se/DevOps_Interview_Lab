"""Validation rules shared by the core validators.

Small predicates only, so every data domain validates fields in the same way
without depending on another domain's validator.
"""

from __future__ import annotations


def is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_positive_weight(value: object) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and value > 0