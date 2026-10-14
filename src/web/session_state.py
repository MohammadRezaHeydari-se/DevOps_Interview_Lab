"""Minimal interview state stored in Flask's signed-cookie session.

No database and no question content: only the ordered question ids and the
current position are kept, so the order the core interview builder produced is
preserved for the whole session.
"""

from __future__ import annotations

from typing import List, Optional

from flask import session

_QUESTION_IDS = "interview_question_ids"
_INDEX = "interview_index"


def start(question_ids: List[str]) -> None:
    """Begin a session with the given question ids in their generated order."""
    session[_QUESTION_IDS] = list(question_ids)
    session[_INDEX] = 0


def clear() -> None:
    """Drop all interview state."""
    session.pop(_QUESTION_IDS, None)
    session.pop(_INDEX, None)


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
