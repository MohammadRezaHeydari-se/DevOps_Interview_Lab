"""Terminal text formatting for the interview CLI.

Pure functions only: no input, no printing, no session logic.
"""

from __future__ import annotations

from typing import Sequence

from src.core.models import Question

ALL = "all"
LINE = "-" * 60


def format_menu(options: Sequence[str], *, header: str) -> str:
    lines = [header, f"  {ALL}"]
    lines.extend(f"  {option}" for option in options)
    return "\n".join(lines)


def format_question(question: Question, index: int, total: int) -> str:
    return "\n".join(
        [
            LINE,
            f"Question {index}/{total} - {question.category} ({question.difficulty})",
            "",
            question.question,
        ]
    )


def format_answer(question: Question) -> str:
    return "\n".join(["", "Short answer:", question.shortAnswer])


def format_explanation(question: Question) -> str:
    lines = ["", "Explanation:", question.explanation]
    if question.followUps:
        lines.append("")
        lines.append("Follow-up questions:")
        lines.extend(f"  - {follow_up}" for follow_up in question.followUps)
    return "\n".join(lines)