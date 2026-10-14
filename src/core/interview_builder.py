"""Build a weighted interview session from a role (and optional company) profile.

Orchestration only: weighting math lives in `weighting`, compatibility in
`compatibility`, and question filtering/selection in `selectors`. The builder
adds no question content and stays independent from the CLI and any web UI.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Set

from .compatibility import ensure_compatible
from .company_models import CompanyProfile
from .interview_models import InterviewSession
from .models import Question
from .profile_models import RoleProfile
from .selectors import filter_questions, select_random
from .weighting import allocate_quota, combine_weights


def build_interview(
    role: RoleProfile,
    questions: Sequence[Question],
    *,
    company: Optional[CompanyProfile] = None,
    difficulty: Optional[str] = None,
    count: int = 5,
    seed: Optional[int] = None,
) -> InterviewSession:
    """Build a weighted, duplicate-free interview session.

    The required role profile drives category weighting. An optional compatible
    company profile adjusts those weights without replacing them. Questions are
    filtered by difficulty (`None` means all difficulties) and selected without
    duplicates, deterministically when a `seed` is given. If fewer questions
    match than requested, the session returns what is available instead of
    raising.
    """
    if count < 0:
        raise ValueError("count must be non-negative")
    ensure_compatible(role, company)

    pool = filter_questions(list(questions), difficulty=difficulty)
    by_category = _group_by_category(pool)
    weights = combine_weights(
        role.areas,
        company.focus if company is not None else None,
    )
    selected = _select_weighted(by_category, weights, count, seed)
    return InterviewSession(
        role=role,
        company=company,
        difficulty=difficulty,
        requestedCount=count,
        questions=selected,
    )


def _group_by_category(questions: Sequence[Question]) -> Dict[str, List[Question]]:
    grouped: Dict[str, List[Question]] = {}
    for question in questions:
        grouped.setdefault(question.category, []).append(question)
    return grouped


def _select_weighted(
    by_category: Dict[str, List[Question]],
    weights: Dict[str, float],
    count: int,
    seed: Optional[int],
) -> List[Question]:
    selected: List[Question] = []
    seen_ids: Set[str] = set()
    remaining_weights = {
        area: weight
        for area, weight in weights.items()
        if weight > 0 and by_category.get(area)
    }
    while remaining_weights and len(selected) < count:
        quota = allocate_quota(remaining_weights, count - len(selected))
        progressed = False
        for area in sorted(quota):
            chosen = select_random(
                by_category.get(area, []),
                quota[area],
                seed=seed,
                exclude_ids=seen_ids,
            )
            if not chosen:
                continue
            seen_ids.update(question.id for question in chosen)
            selected.extend(chosen)
            progressed = True
        if not progressed:
            break
        remaining_weights = {
            area: weight
            for area, weight in remaining_weights.items()
            if _has_available(by_category.get(area, []), seen_ids)
        }
    return selected


def _has_available(questions: Sequence[Question], seen_ids: Set[str]) -> bool:
    return any(question.id not in seen_ids for question in questions)
