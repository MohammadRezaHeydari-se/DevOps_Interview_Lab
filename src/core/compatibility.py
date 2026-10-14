"""Role/company profile compatibility.

A company profile declares which role profiles it supports. Building an
interview with a company that does not support the requested role is rejected
before any selection happens.
"""

from __future__ import annotations

from typing import Optional

from .company_models import CompanyProfile
from .profile_models import RoleProfile


class IncompatibleProfileError(ValueError):
    """Raised when a company profile does not support a role profile."""


def ensure_compatible(
    role: RoleProfile,
    company: Optional[CompanyProfile] = None,
) -> None:
    """Raise `IncompatibleProfileError` if the company does not support the role.

    A missing company is always compatible: company tailoring is optional.
    """
    if company is None:
        return
    if role.id not in company.roleProfileIds:
        raise IncompatibleProfileError(
            f"Company '{company.id}' does not support role '{role.id}'"
        )
