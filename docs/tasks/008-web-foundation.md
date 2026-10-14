# TASK-008: Build the minimal web MVP foundation

## Goal
Add a small, modular Flask web application that exposes the reusable interview core in a browser: choose a role and optional company, pick a difficulty and a question count, and see the first question of the built session.

## Requirements
- Flask for the web layer, server-rendered HTML templates and minimal CSS (Flask is the only approved new dependency)
- small modular web application
- home page with role, optional company, difficulty and question count
- load available roles/companies from the existing profile loaders
- validate submitted choices and role/company compatibility
- use the existing interview builder to create a session
- show the first question in the browser
- keep business logic in `src/core`; no duplicate filtering or weighting
- keep routes, templates and styling separate
- friendly errors for invalid inputs
- local development MVP only: no login, database, AI, scoring, persistence, Docker, React or deployment
- no CLI or question/profile data changes
- small modules and functions; avoid a large `app.py`
- focused unittest tests using Flask's test client
- document installation and local run commands in README
- update relevant docs and this report
- run all tests
- do not commit or push

## Solution

### Web package (`src/web`, dependency direction `web -> core` only)
- `src/web/__init__.py`: `create_app()` application factory; registers one blueprint.
- `src/web/routes.py`: thin controllers. `GET /` renders the request form; `POST /session` parses and validates the request, calls the core interview builder and renders the first question. On invalid input or no matches it re-renders the home page with friendly errors and HTTP 400.
- `src/web/catalog.py`: `Catalog` (roles, companies, id lookups), `load_catalog()` (through `src.core.profile_loader` and `src.core.company_loader`) and `difficulty_options()` (from `src.core.validators.ALLOWED_DIFFICULTIES`). No business logic.
- `src/web/forms.py`: `parse_session_request(form, catalog)` validates role (required), company (optional), difficulty (optional) and count (`1..100`) and delegates compatibility to `src.core.compatibility.ensure_compatible`. Returns a validated `SessionRequest` or friendly errors.
- `src/web/__main__.py`: `python3 -m src.web` runs the development server.

### Templates and styling
- `src/web/templates/base.html`: shared layout and stylesheet link.
- `src/web/templates/home.html`: the request form plus error list.
- `src/web/templates/question.html`: the first question with category, difficulty, short answer, explanation and follow-ups.
- `src/web/static/style.css`: minimal CSS only.

### Reused core (no duplication)
- profile and company loading: `load_profiles` / `load_company_profiles`
- difficulty values: `ALLOWED_DIFFICULTIES`
- compatibility: `ensure_compatible` / `IncompatibleProfileError`
- session building (filtering, weighting, selection): `build_interview`
- questions: `load_questions`

The web layer performs only input parsing and template rendering; no filtering, weighting or selection is reimplemented.

## Files created
- src/web/__init__.py
- src/web/__main__.py
- src/web/routes.py
- src/web/catalog.py
- src/web/forms.py
- src/web/templates/base.html
- src/web/templates/home.html
- src/web/templates/question.html
- src/web/static/style.css
- tests/test_web.py
- docs/tasks/008-web-foundation.md

## Files updated
- docs/decisions.md (DEC-007)
- docs/architecture.md
- README.md (installation and local run)
- CHANGELOG.md

## Validation
- `python3 -m unittest discover -s tests`: 113/113 tests passed (94 core/CLI/profile/builder + 19 web)
- `tests/test_web.py` uses Flask's test client: home page rendering, role/company/difficulty options, static CSS, valid session with and without a company, requested count, graceful shortfall, and friendly errors for missing/unknown role, unknown company, unknown difficulty, non-numeric and out-of-range count, and no matching questions
- `parse_session_request` is unit-tested with a synthetic catalog for the compatible, optional-company and incompatible cases
- Dependency audit: `src/web` imports only `flask` (approved) and `src.core`; the core still imports no web code and the CLI is untouched
- No question or profile data changed; no login, database, AI, scoring, persistence, Docker, React or deployment added
