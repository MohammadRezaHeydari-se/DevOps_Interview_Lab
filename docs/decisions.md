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

### DEC-006: Interview building and category weighting

- **Date:** 2026-10-14
- **Status:** Accepted
- **Context:** TASK-007 requires building an interview session from the existing question bank, role profiles and company profiles. Selection must be weighted primarily by role areas, a company focus must adjust but never replace role weights, questions must not repeat, selection must be deterministic when a seed is given, and an insufficient question bank must be handled gracefully.
- **Decision:** Add interview building to the reusable core, separate from the CLI and any future web UI, and split by responsibility:
  - `src/core/weighting.py` holds the pure weighting math. `combine_weights` multiplies every role area weight by the company focus weight for the same category (missing categories default to a factor of `1.0`); categories a company adds but the role does not define are ignored, so the role always owns the category set. `allocate_quota` distributes the requested count with the largest-remainder method, breaking ties by category name.
  - `src/core/compatibility.py` holds `ensure_compatible` and `IncompatibleProfileError`; a company must list the role id in `roleProfileIds`, and a missing company is always compatible.
  - `src/core/interview_models.py` holds the frozen `InterviewSession` result (`role`, `company`, `difficulty`, `requestedCount`, `questions`, `is_complete`).
  - `src/core/interview_builder.py` holds `build_interview`, which only orchestrates: check the count and compatibility, filter with `selectors.filter_questions`, combine weights, then select with `selectors.select_random` per category using `exclude_ids` to prevent duplicates. Leftover slots are redistributed when a category runs out, and a shortfall yields a smaller session instead of an error.
- **Consequences:**
  - Weighting can be reasoned about and tested on its own; session building stays orchestration.
  - Role areas always define the categories and base weights, and company focus is a bounded adjustment.
  - The builder is reusable by a future web UI and is not tied to the CLI.
  - The builder returns fewer questions rather than raising when the bank is insufficient, so callers can inspect `is_complete`.

### DEC-007: Flask web MVP

- **Date:** 2026-10-14
- **Status:** Accepted
- **Context:** TASK-008 requires a minimal browser front end for the already reusable core. A web stack had to be chosen; Flask is the only approved new dependency. The web layer must not duplicate the core's filtering, weighting or selection, and must stay a small local-development MVP.
- **Decision:** Add a small `src/web` package using Flask with server-rendered Jinja templates and minimal CSS. `src/web/__init__.py` exposes a `create_app()` factory that registers one blueprint. Routers, request parsing, core data access and templates are separate small modules: `routes.py` (thin controllers), `forms.py` (input validation and compatibility delegation), `catalog.py` (core loaders and allowed values) and `templates/` + `static/`. The layer only calls `src.core` (`load_profiles`, `load_company_profiles`, `load_questions`, `ensure_compatible`, `build_interview`); it reimplements no business logic. Invalid input re-renders the home page with friendly messages and HTTP 400. Local run is `python3 -m src.web`.
- **Consequences:**
  - Flask becomes the first and only external dependency, enabled by explicit approval.
  - The core stays UI-agnostic and the CLI is unchanged; the web layer is the product-facing front end.
  - The MVP has no login, database, AI, scoring, persistence, containerization or deployment; those remain separate, later decisions.
  - Routes, templates and styling stay separated, so each can grow or be replaced independently.

### DEC-008: Local interview flow state without a database

- **Date:** 2026-10-14
- **Status:** Accepted
- **Context:** TASK-009 requires completing an interview one question at a time in the browser: preserve the generated order, reveal answers on request, navigate without repeats and finish, all without a database. Reference answers must never reach the page before a reveal request.
- **Decision:** Keep the interview state in Flask's signed-cookie session (`flask.session`), through `src/web/session_state.py`. The state stores only the ordered question ids produced once by the core `build_interview` and the current index; question content is resolved on demand through the core loader (`load_questions_by_id`). The builder is not re-run mid-session, so the generated order is preserved exactly. Routes follow POST/Redirect/GET, and the reference answer block is rendered only by the reveal action. `create_app` sets a per-instance random `SECRET_KEY` (`secrets.token_hex(32)`), so no secret is committed.
- **Consequences:**
  - No database, no persistence layer and no new dependency; the state is small and local to the user's browser.
  - Sessions are dropped on server restart, which is acceptable for the local development MVP.
  - The flow is testable with Flask's test client, including invalid navigation guards.
  - Future scoring, progress or persistence would require a separate, explicit decision.
