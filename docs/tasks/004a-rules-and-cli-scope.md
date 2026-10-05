# TASK-004A: Refine project rules and CLI scope

## Goal
Make the maintainability rules permanent in AGENTS.md, record that the target product is web-based and the CLI is temporary, and split `src/cli/main.py` where it mixed responsibilities.

## Requirements
- add permanent maintainability rules to AGENTS.md (small focused files and functions, no large catch-all files, split on multiple responsibilities, separate UI/business logic/data access/validation, no god classes or modules or giant main files, reuse instead of copy, no convenience-driven feature placement, core independent from CLI and future web UI)
- do not expand the CLI beyond its current scope
- review and minimally split `src/cli/main.py`
- document that the target product is web-based and the CLI is temporary
- make TASK-003A and TASK-004 CHANGELOG entries consistent
- run all unittest tests
- do not commit or push

## Solution

### Rules and product direction
- AGENTS.md: added "Product direction" (web-based target product, CLI is a temporary development/testing interface and must not be expanded, core must stay independent from any UI) and "Maintainability rules" (permanent rules listed above). The two rules now fully covered by "Maintainability rules" (small focused units, no duplication) were removed from "Code quality" so each rule has exactly one place.
- docs/architecture.md: status now states the target product is a web application and documents the two existing layers (`src/core` reusable core, `src/cli` temporary interface).
- README: current status mentions the web target and the temporary role of the CLI.
- docs/decisions.md: DEC-003 consequences now record that the CLI is temporary and the product is web-based.

### CLI split
`src/cli/main.py` mixed input parsing, prompting, text formatting, session composition and application flow. Split by responsibility, no behavior change:

- `src/cli/rendering.py`: pure terminal text formatting (`ALL`, `LINE`, `format_menu`, `format_question`, `format_answer`, `format_explanation`)
- `src/cli/prompts.py`: input parsing and prompting (`resolve_choice`, `resolve_count`, `prompt_choice`, `prompt_count`, `ask_to_reveal_explanation`)
- `src/cli/session.py`: session composition over the core (`available_options`, `build_session`)
- `src/cli/main.py`: interactive flow and entry point (`present_question`, `run_session`, `main`)

Dependency direction is one way: `main` → `prompts` → `rendering`, `main` → `session` → `src.core`. No new features, options or CLI behavior were added.

## Files created
- src/cli/rendering.py
- src/cli/prompts.py
- src/cli/session.py
- docs/tasks/004a-rules-and-cli-scope.md

## Files updated
- src/cli/main.py
- src/cli/__init__.py (module overview)
- tests/test_cli.py (imports only)
- AGENTS.md
- docs/architecture.md
- docs/decisions.md
- README.md
- CHANGELOG.md

## Validation
- `python3 -m unittest discover -s tests -v`: 24/24 tests passed
- `python3 -m src.cli.main` verified manually after the split: category filter, single question, explanation revealed, invalid input re-prompt
- No CLI features, options or dependencies added; `data/` and `src/core` unchanged