"""Session composition for the interview CLI.

Thin layer over the reusable core: loading, filtering and selection stay in
`src.core` so the CLI adds no logic of its own.
"""

from __future__ import annotations

from typing import List, Optional, Sequence

from src.core.models import Question
from src.core.selectors import filter_questions, select_random


def available_options(questions: Sequence[Question], attribute: str) -> List[str]:
    """Sorted unique values of a question attribute, e.g. "category"."""
    return sorted({getattr(q, attribute) for q in questions})


def build_session(
    questions: Sequence[Question],
    *,
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    count: int = 5,
    seed: Optional[int] = None,
) -> List[Question]:
    """Build a practice session using the core filtering and selection logic."""
    pool = filter_questions(list(questions), category=category, difficulty=difficulty)
    return select_random(pool, count=count, seed=seed)