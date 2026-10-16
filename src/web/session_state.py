"""Minimal interview state stored in Flask's signed-cookie session.

No database and no question content: only the ordered question ids and the
current position are kept, so the order the core interview builder produced is
preserved for the whole session. Self-assessments are stored as a simple
mapping from question id to the user's subjective rating.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from flask import session

_QUESTION_IDS = "interview_question_ids"
_INDEX = "interview_index"
_RATINGS = "interview_ratings"
_ROLE = "interview_role"

_VALID_RATINGS = {"got-it", "partly", "need-practice"}


def start(question_ids: List[str], role: str = "") -> None:
    """Begin a session with the given question ids in their generated order."""
    session[_QUESTION_IDS] = list(question_ids)
    session[_INDEX] = 0
    session[_RATINGS] = {}
    session[_ROLE] = role


def clear() -> None:
    """Drop all interview state."""
    session.pop(_QUESTION_IDS, None)
    session.pop(_INDEX, None)
    session.pop(_RATINGS, None)
    session.pop(_ROLE, None)


def is_active() -> bool:
    """True when an interview session exists."""
    return bool(session.get(_QUESTION_IDS))


def total() -> int:
    """Number of questions in the current session."""
    return len(session.get(_QUESTION_IDS, []))


def current_index() -> int:
    """Zero-based position of the question being shown."""
    return int(session.get(_INDEX, 0))


def current_question_id() -> Optional[str]:
    """Id of the question at the current position, if any."""
    question_ids = session.get(_QUESTION_IDS, [])
    position = current_index()
    if 0 <= position < len(question_ids):
        return question_ids[position]
    return None


def is_complete() -> bool:
    """True when every question has been passed."""
    return is_active() and current_index() >= total()


def advance() -> None:
    """Move to the next question."""
    session[_INDEX] = current_index() + 1


def question_ids() -> List[str]:
    """The ordered question ids for the current session."""
    ids = session.get(_QUESTION_IDS, [])
    if not isinstance(ids, list):
        return []
    return list(ids)


def ratings() -> Dict[str, str]:
    """All self-assessments recorded so far."""
    ratings = session.get(_RATINGS, {})
    if not isinstance(ratings, dict):
        session[_RATINGS] = {}
        return {}
    return dict(ratings)


def record_rating(rating: str) -> None:
    """Record a subjective self-assessment for the current question."""
    question_id = current_question_id()
    if question_id is None:
        return
    if rating not in _VALID_RATINGS:
        return
    stored = session.get(_RATINGS, {})
    if not isinstance(stored, dict):
        stored = {}
    stored[question_id] = rating
    session[_RATINGS] = stored


def role() -> str:
    """Role label selected for this practice session."""
    return str(session.get(_ROLE, ""))
