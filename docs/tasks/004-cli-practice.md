# TASK-004: Add CLI interview practice

## Goal
Build a minimal Python CLI on top of the existing question core so a candidate can run a practice session in the terminal, without duplicating any loading, filtering or selection logic.

## Requirements
- choose a category or all categories
- choose difficulty or all levels
- choose number of questions
- receive one question at a time
- reveal the short answer after pressing Enter
- optionally reveal the explanation and follow-up questions
- continue until the session ends
- reuse the existing loader and selectors
- keep CLI logic separate from the core
- Python standard library only
- add unittest tests for non-interactive CLI logic
- update relevant docs and create this report
- do not commit or push

## Solution
Added `src/cli/main.py` as the entry point (`python3 -m src.cli.main`):

- `main()`: loads questions via `src.core.loader.load_questions`, prompts for category, difficulty and count, then runs the session
- `prompt_choice()` / `prompt_count()`: interactive input with re-prompt on invalid input
- `present_question()` / `run_session()`: one question at a time, short answer on Enter, optional explanation and follow-up questions, session continues until the last question
- `resolve_choice()` / `resolve_count()` / `available_options()` / `build_session()` / `format_*()`: non-interactive logic, tested without a TTY

`build_session()` delegates to `src.core.selectors.filter_questions` and `src.core.selectors.select_random`, and `main()` uses `filter_questions` to report how many questions match the selection. No loading, filtering or selection logic was duplicated.

## Files created
- src/cli/__init__.py
- src/cli/main.py
- tests/test_cli.py
- docs/tasks/004-cli-practice.md

## Files updated
- README.md (usage and current status)
- CHANGELOG.md
- docs/decisions.md (DEC-003)

## Validation
- `python3 -m unittest discover -s tests -v`: 24/24 tests passed (8 core + 16 CLI)
- Manual run of `python3 -m src.cli.main` verified for: all categories, single category, single difficulty, single question, explanation revealed, explanation skipped, invalid input re-prompt
- Imports limited to the standard library and `src`; no external dependency
- Question data and core behavior unchanged