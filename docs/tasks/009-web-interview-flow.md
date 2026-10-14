# TASK-009: Build interactive web interview flow

## Goal
Extend the Flask web MVP so a user can complete an interview one question at a time: answer in a textarea, reveal the reference answer on request, move to the next question without repeats, and reach a completion screen.

## Requirements
- preserve the generated question order throughout the session
- show question number and total
- let the user write an answer in a textarea
- reveal the reference short answer and explanation on request
- navigate to the next question without repeating questions
- show a simple completion screen
- allow starting a new interview
- keep session state minimal and local; no database
- do not expose reference answers before reveal
- reuse the existing core interview builder and question models
- keep routes, session state, validation, templates and CSS separate
- avoid large files, duplicated logic and unnecessary abstractions
- no AI evaluation, scoring, authentication, deployment, React or new dependencies
- no question or profile data changes
- focused Flask test-client tests for the full flow, invalid navigation and completion
- update docs and create this report
- run all tests
- do not commit or push

## Solution

### Session state
- `src/web/session_state.py`: minimal per-user state kept in Flask's signed-cookie session. Only the ordered question ids and the current index are stored; no question content and no database. Functions: `start`, `clear`, `is_active`, `total`, `current_index`, `current_question_id`, `is_complete`, `advance`.
- `src/web/__init__.py`: `create_app` now sets a per-instance random `SECRET_KEY` with `secrets.token_hex(32)`, so no secret is committed and no extra configuration is needed for local development.

### Routes (`src/web/routes.py`, thin controllers)
- `GET /`: request form (unchanged).
- `POST /session`: validate, build the session with the core `build_interview`, store the ordered question ids and redirect (POST/Redirect/GET) to the first question.
- `GET /session/question`: show the current question number/total and a textarea. The reference answer is never rendered here.
- `POST /session/answer`: `action=reveal` re-renders the current question with the reference short answer and explanation; `action=next` advances, and redirects to the completion screen after the last question. Invalid actions keep the current question.
- `GET /session/complete`: completion screen; redirects home without a session and to the question page before completion.
- `POST /session/new`: clears the interview and returns to the form.

State guards make invalid navigation safe: missing session redirects to the form, and an already completed session redirects to the completion screen.

### Data access and templates
- `src/web/catalog.py`: added `load_questions_by_id()` (through the core `load_questions`) so the current question is resolved from the ordered ids without touching question data.
- `src/web/templates/question.html`: number/total header, question card, answer textarea, and Reveal / Next (or Finish) buttons; the answer block renders only after a reveal request.
- `src/web/templates/complete.html`: completion screen with a "Start a new interview" form.
- `src/web/static/style.css`: small additions for the textarea, action row and secondary button.

Order is preserved because the exact ordered id list produced by the core builder is stored; each step simply reads the id at the current index and the builder is never re-run mid-session. No filtering, weighting or selection is reimplemented.

## Files created
- src/web/session_state.py
- src/web/templates/complete.html
- docs/tasks/009-web-interview-flow.md

## Files updated
- src/web/__init__.py
- src/web/routes.py
- src/web/catalog.py
- src/web/templates/question.html
- src/web/static/style.css
- tests/test_web.py
- docs/decisions.md (DEC-008)
- docs/architecture.md
- README.md
- CHANGELOG.md

## Validation
- `python3 -m unittest discover -s tests`: 127/127 tests passed (94 core/CLI/profile/builder + 33 web)
- `tests/test_web.py` covers: start redirect, first question hides every bank reference answer, stable order on refresh, reveal shows the answer without advancing and hides it again on refresh, next navigates without repeats through completion, the last question offers Finish, the completion screen, starting a new interview clearing state, and invalid navigation (no session, completion before finish, unknown action)
- Manual smoke test with `python3 -m src.web` and `curl` cookie jar confirmed the start/reveal/question flow returns the expected status codes and shows the answer only after reveal
- No question or profile data changed; no CLI changes; no AI evaluation, scoring, authentication, deployment, new dependency or database added
