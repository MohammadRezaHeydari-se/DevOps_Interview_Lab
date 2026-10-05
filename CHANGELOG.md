# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Role profiles for interview selection: one small JSON file per role under `data/profiles/` (DevOps Engineer, Cloud / Azure, IT Infrastructure, IT Support, Linux / System Administration) plus `schema.json`. A profile holds only `id`, `role` and `areas` (question category to positive weight) and never duplicates question content.
- Core profile modules, kept separate from question logic: `src/core/profile_models.py` (`RoleProfile`), `src/core/profile_validators.py` (`validate_profile`) and `src/core/profile_loader.py` (`load_profiles`).
- `src/core/json_io.py` with the shared JSON file reader used by both core loaders.
- `tests/test_profiles.py` covering profile validation, profile loading and profile data consistency.
- DEC-004 in `docs/decisions.md` for profile storage and model.
- Minimal Python `.gitignore` for `__pycache__/`, `*.pyc`, `.venv/`, and `venv/`.
- CLI interview practice (`python3 -m src.cli.main`): choose category, difficulty and question count, then answer one question at a time. The short answer is revealed on Enter; explanation and follow-up questions are optional.
- `tests/test_cli.py` covering the non-interactive CLI logic (choice/count parsing, session building, formatting).
- DEC-003 in `docs/decisions.md` for the CLI layer on top of the question core.

### Changed

- Split `src/cli/main.py` into focused modules: `src/cli/session.py` (session composition over the core), `src/cli/prompts.py` (input parsing and prompting) and `src/cli/rendering.py` (terminal text formatting). `src/cli/main.py` now only wires the interactive flow and stays the entry point.
- AGENTS.md: added the permanent "Product direction" and "Maintainability rules" sections, including that the target product is web-based and the CLI is a temporary development/testing interface.
- docs/architecture.md: recorded the web-based target product, the reusable core and the temporary role of the CLI.
- README: documents the run and test commands, and that the CLI is temporary.
- Question loading, validation, filtering and selection remain in `src/core` only; the CLI delegates to it and no behavior changed.
- `src/core/loader.py` now uses the shared `read_json_file` helper instead of its own JSON reading code.

### Removed

- Unused imports in `src/core/loader.py` and `src/core/validators.py`, and in `tests/test_core.py`.
- Checked-in Python bytecode caches (`__pycache__/`) and a stale `.pytest_cache` directory. Tests use the standard library only: `python3 -m unittest discover -s tests -v`, no external dependency is required.