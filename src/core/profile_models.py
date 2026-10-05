"""Model for role profiles used to build interviews per job role."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class RoleProfile:
    """Interview areas of one job role and their relative importance.

    A profile only describes which question categories matter for a role and how
    important each one is. It never contains question content.
    """

    id: str
    role: str
    areas: Dict[str, float]