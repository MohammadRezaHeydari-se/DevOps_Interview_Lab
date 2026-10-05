from __future__ import annotations

import random
from typing import List, Optional, Set

from .models import Question


def filter_questions(
    questions: List[Question],
    *,
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    type_: Optional[str] = None,
) -> List[Question]:
    result = list(questions)
    if category is not None:
        result = [q for q in result if q.category == category]
    if difficulty is not None:
        result = [q for q in result if q.difficulty == difficulty]
    if type_ is not None:
        result = [q for q in result if q.type == type_]
    return result


def select_random(
    questions: List[Question],
    count: int,
    *,
    seed: Optional[int] = None,
    exclude_ids: Optional[Set[str]] = None,
) -> List[Question]:
    if count < 0:
        count = 0
    pool = list(questions)
    if exclude_ids:
        pool = [q for q in pool if q.id not in exclude_ids]
    if seed is not None:
        rnd = random.Random(seed)
    else:
        rnd = random.Random()
    rnd.shuffle(pool)
    return pool[:count]
