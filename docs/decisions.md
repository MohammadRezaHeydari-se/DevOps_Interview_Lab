# Architecture Decision Log

This document records architectural decisions for the DevOps Interview Lab project.

## Decision template

Each decision should include:
- Date
- Status
- Context
- Decision
- Consequences

## Decisions

### DEC-002: Question bank storage format

- **Date:** 2026-10-04
- **Status:** Accepted
- **Context:** TASK-002 requires building initial interview question bank. Data must be JSON, support the specified fields (id, category, difficulty, type, question, shortAnswer, explanation, followUps). Categories should be able to grow without creating one giant file.
- **Decision:** Store questions as JSON files per category under `data/questions/`. Include a reusable model/schema (`schema.json`) documenting required fields and allowed values. Each category file contains an array of question objects.
- **Consequences:**
  - Easy to extend by adding new category files.
  - Simple to validate and consume without framework dependencies.
  - Clear separation of concerns; no application code introduced.

### DEC-003: CLI layer on top of the question core

- **Date:** 2026-10-05
- **Status:** Accepted
- **Context:** TASK-004 requires an interactive practice session. Question loading, validation, filtering and selection already exist in `src/core` and must not be duplicated. Tests must run without a TTY.
- **Decision:** Add a separate `src/cli` package using the Python 3 standard library only. `src/cli/main.py` is the entry point (`python3 -m src.cli.main`); it reuses `src.core.loader.load_questions`, `src.core.selectors.filter_questions` and `src.core.selectors.select_random`. Interaction is done with `input()`/`print()`, and the non-interactive logic (choice parsing, count parsing, session building, formatting) is kept as plain functions so it can be unit tested.
- **Consequences:**
  - The core stays reusable and free of any CLI concerns.
  - CLI behavior is testable without user interaction.
  - The CLI is a temporary development/testing interface; the target product is a web application, so the CLI is not expanded further.
  - No framework, packaging tool or external dependency is introduced.

### DEC-004: Role profile storage and model

- **Date:** 2026-10-05
- **Status:** Accepted
- **Context:** TASK-005 requires selecting questions by job role. A profile must describe only which interview areas matter for a role and their relative importance, and must never duplicate question content.
- **Decision:** Store one small JSON profile per role under `data/profiles/`, with `schema.json` documenting the contract. A profile holds `id`, `role` and `areas`, where `areas` maps a question category to a positive weight (larger weight means more important). Profiles are a separate data domain: `src/core/profile_models.py`, `src/core/profile_validators.py` and `src/core/profile_loader.py` are kept apart from question models, validation and loading, and profile validation never checks category names against the question bank.
- **Consequences:**
  - A new role is added by adding one JSON file, with no code change.
  - Interview building stays in the core and is not tied to the CLI or any future web UI.
  - Category typos in profiles are caught by a test, not by profile validation.

### DEC-005: Company profile storage and model

- **Date:** 2026-10-05
- **Status:** Accepted
- **Context:** TASK-006 requires tailoring interviews per company. No verified company-specific interview requirements are documented, and company profiles must never duplicate question content.
- **Decision:** Store one small JSON company profile per company under `data/profiles/companies/`, with `schema.json` documenting the contract. A company profile holds `id`, `company`, `roleProfileIds`, `focus` (question category to positive weight) and an optional `notes` string. Company profiles are a separate domain: `src/core/company_models.py`, `src/core/company_validators.py` and `src/core/company_loader.py` stay separate from the role profile modules, and only the shared field predicates in `src/core/validation_rules.py` and the JSON reader in `src/core/json_io.py` are reused. Initial profiles (Kreab, itm8, Ductus) use generic focus areas and reference all role profiles, with a note stating that no company-specific requirements are documented.
- **Consequences:**
  - A new company is added by adding one JSON file, with no code change.
  - Company-specific weights can be filled in later when documented, without changing the model.
  - Cross-domain checks (role profile ids, category names) stay in tests, not in core validation, so no data domain depends on another.
