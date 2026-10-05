"""Validation for company profile data.

Kept separate from role profile validation: a company profile has different
fields (linked role profiles, focus areas, optional notes). Role profile ids and
category names are not checked here on purpose, so this validator depends on no
other data domain.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from .validation_rules import is_non_empty_string, is_positive_weight

REQUIRED_COMPANY_FIELDS = ("id", "company", "roleProfileIds", "focus")
OPTIONAL_COMPANY_FIELDS = ("notes",)


def validate_company_profile(data: Dict) -> Tuple[bool, List[str]]:
    """Validate one company profile object and return (ok, errors)."""
    if not isinstance(data, dict):
        return False, ["Company profile must be a JSON object"]

    errors: List[str] = []
    for field in REQUIRED_COMPANY_FIELDS:
        if field not in data:
            errors.append(f"Missing field: {field}")
    if errors:
        return False, errors

    for field in ("id", "company"):
        if not is_non_empty_string(data[field]):
            errors.append(f"{field} must be a non-empty string")

    errors.extend(_validate_role_profile_ids(data["roleProfileIds"]))
    errors.extend(_validate_focus(data["focus"]))

    notes = data.get("notes", "")
    if not isinstance(notes, str):
        errors.append("notes must be a string")

    return (len(errors) == 0), errors


def _validate_role_profile_ids(value: object) -> List[str]:
    if not isinstance(value, list) or not value:
        return ["roleProfileIds must be a non-empty list of role profile ids"]
    if not all(is_non_empty_string(item) for item in value):
        return ["roleProfileIds entries must be non-empty strings"]
    return []


def _validate_focus(value: object) -> List[str]:
    if not isinstance(value, dict) or not value:
        return ["focus must be a non-empty object of category weights"]
    errors: List[str] = []
    for area, weight in value.items():
        if not is_non_empty_string(area):
            errors.append("focus area name must be a non-empty string")
        if not is_positive_weight(weight):
            errors.append(f"focus weight must be a positive number: {area}")
    return errors