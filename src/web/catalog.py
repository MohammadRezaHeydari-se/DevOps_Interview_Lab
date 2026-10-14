"""Core data available to the web layer.

Aggregates the existing core loaders and question-bank values so the web layer
never duplicates filtering, weighting or validation. No business logic lives
here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from src.core.company_loader import load_company_profiles
from src.core.company_models import CompanyProfile
from src.core.profile_loader import load_profiles
from src.core.profile_models import RoleProfile
from src.core.validators import ALLOWED_DIFFICULTIES


@dataclass(frozen=True)
class Catalog:
    """Role and company profiles available for building interviews."""

    roles: List[RoleProfile]
    companies: List[CompanyProfile]

    @property
    def roles_by_id(self) -> Dict[str, RoleProfile]:
        return {role.id: role for role in self.roles}

    @property
    def companies_by_id(self) -> Dict[str, CompanyProfile]:
        return {company.id: company for company in self.companies}


def load_catalog() -> Catalog:
    """Load roles and companies through the shared core loaders."""
    return Catalog(roles=load_profiles(), companies=load_company_profiles())


def difficulty_options() -> List[str]:
    """Difficulty values accepted by the question bank, plus "all" (blank)."""
    return sorted(ALLOWED_DIFFICULTIES)
