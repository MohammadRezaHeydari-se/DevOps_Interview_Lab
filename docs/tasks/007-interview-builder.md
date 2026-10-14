# TASK-007: Build the interview session builder

## Goal
Build a reusable interview builder in the reusable core that composes an interview session from the existing question bank, role profiles and company profiles, without touching question content, profile data or the CLI.

## Requirements
- required role profile and optional company profile
- difficulty filter or all difficulties
- requested question count
- weighted category selection primarily based on role areas
- company focus adjusts role weights but never replaces them
- no duplicate questions
- deterministic selection with an optional seed
- handle insufficient matching questions gracefully
- reject incompatible role/company combinations
- reuse existing models, loaders, selectors and validation helpers
- keep weighting and session building separate, with small focused files/functions
- no CLI, question content or profile data changes
- no web code, scoring, AI, database or external dependencies
- focused unittest tests for selection, weighting, filtering, compatibility, reproducibility and edge cases
- update relevant docs and this report
- run the full test suite
- do not commit or push

## Solution

### Modules (all in `src/core`, independent from the CLI and any web UI)
- `src/core/weighting.py`: pure weighting math.
  - `combine_weights(role_areas, company_focus=None)`: role areas define the categories and the base weights. A company focus only multiplies the weight of categories the role already defines (missing categories default to factor `1.0`); categories the company adds but the role does not define are ignored. Company focus therefore adjusts role weights without replacing them.
  - `allocate_quota(weights, total)`: distributes the requested count across categories proportionally to their weights using the largest-remainder method. Ties break on category name, so the result is deterministic and independent of mapping order.
- `src/core/compatibility.py`: `IncompatibleProfileError` and `ensure_compatible(role, company=None)`. A company must list the role id in `roleProfileIds`; a missing company is always compatible.
- `src/core/interview_models.py`: frozen `InterviewSession` dataclass (`role`, `company`, `difficulty`, `requestedCount`, `questions`) with an `is_complete` property.
- `src/core/interview_builder.py`: `build_interview(role, questions, *, company=None, difficulty=None, count=5, seed=None)`. Orchestration only: validate the count, check compatibility, filter by difficulty through `selectors.filter_questions` (`None` means all), combine weights, then select. Selection uses `selectors.select_random` per category with the `exclude_ids` argument to guarantee no duplicates and seeded reproducibility.

### Behaviour
- Weighted category selection is role-driven; a compatible company profile adjusts the mix (e.g. `{"A": 1.0, "B": 1.0}` with company focus `{"A": 1.0, "B": 0.25}` over 10 questions yields 8/2 instead of 5/5).
- If a category runs out of questions, the leftover slots are redistributed to categories that still have questions.
- If the bank cannot satisfy the requested count, the session is returned with what is available (`is_complete` is `False`) instead of raising.
- An incompatible role/company pair raises `IncompatibleProfileError`; a negative count raises `ValueError`.

## Files created
- src/core/weighting.py
- src/core/compatibility.py
- src/core/interview_models.py
- src/core/interview_builder.py
- tests/test_weighting.py
- tests/test_interview_builder.py
- docs/tasks/007-interview-builder.md

## Files updated
- docs/decisions.md (DEC-006)
- docs/architecture.md
- README.md
- CHANGELOG.md

## Validation
- `python3 -m unittest discover -s tests -v`: 94/94 tests passed (8 core + 16 CLI + 18 role profiles + 17 company profiles + 12 weighting + 23 interview builder)
- `tests/test_weighting.py` covers role/company combination, category replacement/ignore rules, largest-remainder allocation, tie-breaking and empty inputs
- `tests/test_interview_builder.py` covers selection, weighted distribution, difficulty filtering, compatibility, reproducibility, shortfall redistribution and edge cases
- Data-driven tests build complete 5-question sessions for the `devops-engineer` role with and without the `itm8` company profile
- No CLI, question data or profile data changed; `python3 -m src.cli.main` behavior unchanged; standard library only
