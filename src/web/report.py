"""Transparent, self-reported interview practice feedback.

This is not hiring suitability, automated answer grading, or a job-match model.
Unrated questions are excluded from the score and reported separately.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Mapping, Sequence

from src.core.models import Question

_POINTS = {"got-it": 100, "partly": 50, "need-practice": 0}


def build_report(question_ids: Sequence[str], ratings: Mapping[str, str],
                 questions: Mapping[str, Question]) -> dict:
    """Summarize subjective confidence by technical area, without false precision."""
    areas = defaultdict(list)
    for question_id in question_ids:
        question = questions.get(question_id)
        rating = ratings.get(question_id)
        if question is not None and rating in _POINTS:
            areas[question.category].append(_POINTS[rating])
    assessed = sum(len(scores) for scores in areas.values())
    total = len(question_ids)
    average = round(sum(sum(scores) for scores in areas.values()) / assessed) if assessed else None
    breakdown = [
        {"name": name, "score": round(sum(scores) / len(scores)), "count": len(scores)}
        for name, scores in sorted(areas.items())
    ]
    return {
        "score": average,
        "assessed": assessed,
        "total": total,
        "unrated": total - assessed,
        "areas": breakdown,
        "strengths": [area for area in breakdown if area["score"] >= 75],
        "practice": [area for area in breakdown if area["score"] < 75],
    }
