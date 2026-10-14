"""Result model for a built interview session.

Separate from the builder so the output contract stays explicit and reusable by
any future caller (CLI or web UI).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .company_models import CompanyProfile
from .models import Question
from .profile_models import RoleProfile


@dataclass(frozen=True)
class InterviewSession:
    """A built interview: the selected questions plus the inputs used."""

    role: RoleProfile
    company: Optional[CompanyProfile]
    difficulty: Optional[str]
    requestedCount: int
    questions: List[Question]

    @property
    def is_complete(self) -> bool:
        """True when the requested number of questions could be selected."""
        return len(self.questions) >= self.requestedCount
