"""Validation for role profile data.

Profiles are a separate data domain, so their rules stay separate from question
validation. Category names are not checked here on purpose: a profile is
validated on its own shape, not against the question bank.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

REQUIRED_PROFILE_FIELDS = ("id", "role", "areas")


def validate_profile(data: Dict) -> Tuple[bool, List[str]]:
    """Validate one profile object and return (ok, errors)."""
    if not isinstance(data, dict):
        return False, ["Profile must be a JSON object"]

    errors: List[str] = []
    for field in REQUIRED_PROFILE_FIELDS:
        if field not in data:
            errors.append(f"Missing field: {field}")
    if errors:
        return False, errors

    for field in ("id", "role"):
        if not isinstance(data[field], str) or not data[field].strip():
            errors.append(f"{field} must be a non-empty string")

    areas = data["areas"]
    if not isinstance(areas, dict) or not areas:
        errors.append("areas must be a non-empty object of category weights")
        return False, errors

    for area, weight in areas.items():
        if not isinstance(area, str) or not area.strip():
            errors.append("area name must be a non-empty string")
        if isinstance(weight, bool) or not isinstance(weight, (int, float)) or weight <= 0:
            errors.append(f"area weight must be a positive number: {area}")

    return (len(errors) == 0), errors