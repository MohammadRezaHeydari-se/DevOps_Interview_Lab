"""Loading of company profiles.

Separate from role profile loading: a company profile is its own model with its
own validation rules. Reuses the shared JSON reading infrastructure.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .company_models import CompanyProfile
from .company_validators import validate_company_profile
from .json_io import read_json_file


def load_company_profiles(companies_dir: str | None = None) -> List[CompanyProfile]:
    """Load all company profiles, skipping invalid entries."""
    if companies_dir is None:
        base = Path(__file__).resolve().parents[2] / "data" / "profiles" / "companies"
    else:
        base = Path(companies_dir)
    profiles: List[CompanyProfile] = []
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
        ok, _ = validate_company_profile(raw)
        if not ok:
            continue
        profiles.append(_build_company_profile(raw))
    return profiles


def _build_company_profile(raw: Dict) -> CompanyProfile:
    return CompanyProfile(
        id=str(raw["id"]),
        company=str(raw["company"]),
        roleProfileIds=[str(item) for item in raw["roleProfileIds"]],
        focus={str(area): float(weight) for area, weight in raw["focus"].items()},
        notes=str(raw.get("notes", "")),
    )