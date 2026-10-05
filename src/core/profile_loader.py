"""Loading of role profiles.

Separate from question loading: profiles and questions are different data
domains with different models and validation rules.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from .json_io import read_json_file
from .profile_models import RoleProfile
from .profile_validators import validate_profile


def load_profiles(profiles_dir: str | None = None) -> List[RoleProfile]:
    """Load all role profiles, skipping invalid entries."""
    if profiles_dir is None:
        base = Path(__file__).resolve().parents[2] / "data" / "profiles"
    else:
        base = Path(profiles_dir)
    profiles: List[RoleProfile] = []
    if not base.exists():
        return profiles
    for path in sorted(base.iterdir()):
        if not path.is_file() or not path.name.endswith(".json"):
            continue
        if path.name == "schema.json":
            continue
        try:
            raw = read_json_file(path)
        except Exception:
            continue
        if not isinstance(raw, dict):
            continue
        ok, _ = validate_profile(raw)
        if not ok:
            continue
        profiles.append(
            RoleProfile(
                id=str(raw["id"]),
                role=str(raw["role"]),
                areas={str(area): float(weight) for area, weight in raw["areas"].items()},
            )
        )
    return profiles