# TASK-003: Build the question bank core

## Goal
Build small reusable core (Python 3 stdlib only) to load, validate, filter, and select questions without duplicating logic.

## Requirements
- load all question JSON files
- validate questions against our model
- filter by category, difficulty and type
- return reusable Question objects
- randomly select questions without duplicating logic
- Keep data loading, validation and question selection separate
- Do not modify question content
- Add focused unittest tests
- No UI, API, database, framework or external dependencies
- Update relevant docs and create docs/tasks/003-question-core.md
- Run all tests and JSON validation
- Do not commit or push

## Solution
Created core modules:
- src/core/models.py: frozen Question dataclass
- src/core/validators.py: required fields, enums, type checks
- src/core/loader.py: scans data/questions, skips schema.json, validates, returns Question objects
- src/core/selectors.py: filter_questions (category/difficulty/type), select_random (shuffle with seed, optional exclude_ids)

Added tests/test_core.py with 8 focused unit tests. All pass. JSON validated.

## Files created
- src/core/__init__.py
- src/core/models.py
- src/core/validators.py
- src/core/loader.py
- src/core/selectors.py
- tests/test_core.py
- docs/tasks/003-question-core.md

## Results
- 8/8 tests passed
- All JSON files valid
- Core functions separated as requested