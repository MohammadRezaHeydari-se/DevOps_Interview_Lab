from __future__ import annotations

from typing import Dict, List, Tuple

ALLOWED_CATEGORIES = {
    "HR / LIA",
    "Linux",
    "Networking",
    "Azure",
    "Active Directory / Entra ID",
    "Git / CI/CD",
    "Docker",
    "Troubleshooting",
}
ALLOWED_DIFFICULTIES = {"junior", "mid", "senior"}
ALLOWED_TYPES = {"theory", "practical"}


def validate_question(data: Dict) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    required = (
        "id",
        "category",
        "difficulty",
        "type",
        "question",
        "shortAnswer",
        "explanation",
        "followUps",
    )
    for key in required:
        if key not in data:
            errors.append(f"Missing field: {key}")
    if errors:
        return False, errors

    if not isinstance(data["id"], str) or not data["id"].strip():
        errors.append("id must be non-empty string")
    if data["category"] not in ALLOWED_CATEGORIES:
        errors.append(f"category invalid: {data['category']}")
    if data["difficulty"] not in ALLOWED_DIFFICULTIES:
        errors.append(f"difficulty invalid: {data['difficulty']}")
    if data["type"] not in ALLOWED_TYPES:
        errors.append(f"type invalid: {data['type']}")
    for field in ("question", "shortAnswer", "explanation"):
        if not isinstance(data[field], str):
            errors.append(f"{field} must be string")
    if not isinstance(data["followUps"], list) or not all(
        isinstance(f, str) for f in data["followUps"]
    ):
        errors.append("followUps must be list of strings")

    return (len(errors) == 0), errors
