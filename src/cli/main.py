"""Interactive practice flow and entry point for the CLI.

The CLI is a temporary development/testing interface for the reusable core.
Wiring only: questions come from `src.core`, input from `src.cli.prompts`,
text from `src.cli.rendering`.
"""

from __future__ import annotations

from typing import Sequence

from src.cli.prompts import ask_to_reveal_explanation, prompt_choice, prompt_count
from src.cli.rendering import LINE, format_answer, format_explanation, format_question
from src.cli.session import available_options, build_session
from src.core.loader import load_questions
from src.core.models import Question
from src.core.selectors import filter_questions


def present_question(question: Question, index: int, total: int) -> None:
    """Show one question, then reveal the short answer on Enter."""
    print(format_question(question, index, total))
    input("Press Enter to reveal the short answer...")
    print(format_answer(question))
    if ask_to_reveal_explanation():
        print(format_explanation(question))
    input("Press Enter for the next question...")


def run_session(session: Sequence[Question]) -> None:
    """Walk through the session until the last question is answered."""
    total = len(session)
    for index, question in enumerate(session, start=1):
        present_question(question, index, total)
    print(LINE)
    print(f"Session finished: {total} question(s) answered.")


def main() -> int:
    """Entry point for the interactive practice session."""
    questions = load_questions()
    if not questions:
        print("No questions found in data/questions.")
        return 1

    category = prompt_choice("Categories:", available_options(questions, "category"))
    difficulty = prompt_choice("Difficulty levels:", available_options(questions, "difficulty"))

    candidates = filter_questions(questions, category=category, difficulty=difficulty)
    if not candidates:
        print("No questions match that selection.")
        return 1

    count = prompt_count(len(candidates))
    session = build_session(
        questions,
        category=category,
        difficulty=difficulty,
        count=count,
    )
    run_session(session)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())