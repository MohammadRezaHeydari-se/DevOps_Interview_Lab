"""User input parsing and prompting for the interview CLI.

Input is read and validated here only; the parsing helpers (`resolve_choice`,
`resolve_count`) are plain functions so they can be tested without a TTY.
"""

from __future__ import annotations

from typing import Optional, Sequence

from src.cli.rendering import ALL, format_menu


def resolve_choice(text: str, options: Sequence[str]) -> Optional[str]:
    """Map user input to an option value; ALL or empty input means no filter.

    Any unknown value raises ValueError so the caller can ask again.
    """
    value = text.strip()
    if not value or value.lower() == ALL:
        return None
    if value not in options:
        raise ValueError(f"Unknown option: {value}")
    return value


def resolve_count(text: str, available: int) -> int:
    """Parse a requested question count, clamped to the available questions."""
    value = int(text.strip())
    if value < 1:
        raise ValueError("Count must be 1 or greater")
    return min(value, available)


def prompt_choice(header: str, options: Sequence[str]) -> Optional[str]:
    """Ask for an option until a valid one is given. None means all."""
    print(format_menu(options, header=header))
    while True:
        try:
            return resolve_choice(input(f"Choose ({ALL} for all): "), options)
        except ValueError as error:
            print(error)


def prompt_count(available: int) -> int:
    """Ask how many questions to practice until a valid count is given."""
    while True:
        try:
            return resolve_count(input(f"How many questions (1-{available}): "), available)
        except ValueError as error:
            print(error)


def ask_to_reveal_explanation() -> bool:
    return input("Reveal explanation and follow-up questions? [y/N]: ").strip().lower() == "y"