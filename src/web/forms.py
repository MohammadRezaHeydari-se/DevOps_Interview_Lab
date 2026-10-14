"""Validation of the interview request submitted from the home page.

Input parsing and friendliness only. Compatibility is delegated to the core and
no filtering, weighting or selection happens here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Mapping, Optional, Tuple

from src.core.company_models import CompanyProfile
from src.core.compatibility import IncompatibleProfileError, ensure_compatible
from src.core.profile_models import RoleProfile

from .catalog import Catalog, difficulty_options

MIN_COUNT = 1
MAX_COUNT = 100


@dataclass(frozen=True)
class SessionRequest:
    """A validated interview request ready for the core interview builder."""

    role: RoleProfile
    company: Optional[CompanyProfile]
    difficulty: Optional[str]
    count: int


def parse_session_request(
    form: Mapping[str, str],
    catalog: Catalog,
) -> Tuple[Optional[SessionRequest], List[str]]:
    """Return a validated request or a list of friendly error messages."""
    errors: List[str] = []

    role = _resolve_role(form.get("role", ""), catalog, errors)
    company = _resolve_company(form.get("company", ""), catalog, errors)
    difficulty = _resolve_difficulty(form.get("difficulty", ""), errors)
    count = _resolve_count(form.get("count", ""), errors)

    if role is None or errors:
        return None, errors

    try:
        ensure_compatible(role, company)
    except IncompatibleProfileError:
        errors.append(f"{company.company} does not offer the {role.role} role.")
        return None, errors

    return (
        SessionRequest(role=role, company=company, difficulty=difficulty, count=count),
        errors,
    )


def _resolve_role(
    value: str, catalog: Catalog, errors: List[str]
) -> Optional[RoleProfile]:
    value = value.strip()
    if not value:
        errors.append("Please choose a role.")
        return None
    role = catalog.roles_by_id.get(value)
    if role is None:
        errors.append("Please choose a role from the list.")
    return role


def _resolve_company(
    value: str, catalog: Catalog, errors: List[str]
) -> Optional[CompanyProfile]:
    value = value.strip()
    if not value:
        return None
    company = catalog.companies_by_id.get(value)
    if company is None:
        errors.append("Please choose a company from the list.")
    return company


def _resolve_difficulty(value: str, errors: List[str]) -> Optional[str]:
    value = value.strip()
    if not value:
        return None
    if value not in difficulty_options():
        errors.append("Please choose a difficulty from the list.")
        return None
    return value


def _resolve_count(value: str, errors: List[str]) -> int:
    value = value.strip()
    try:
        count = int(value)
    except (TypeError, ValueError):
        errors.append("Question count must be a whole number.")
        return 0
    if count < MIN_COUNT or count > MAX_COUNT:
        errors.append(f"Question count must be between {MIN_COUNT} and {MAX_COUNT}.")
        return 0
    return count
