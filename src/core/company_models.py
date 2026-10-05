"""Model for company profiles used to tailor interviews per company."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class CompanyProfile:
    """Interview tailoring data for one company.

    A company profile references role profiles by id and adds interview focus
    areas with relative weights. It never contains question content, and it
    only states what is documented.
    """

    id: str
    company: str
    roleProfileIds: List[str]
    focus: Dict[str, float]
    notes: str = ""