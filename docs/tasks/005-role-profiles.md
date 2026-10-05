# TASK-005: Add interview role profiles

## Goal
Add a minimal reusable profile model so interviews can be selected per job role, without duplicating question content and without touching question logic or the CLI.

## Requirements
- minimal reusable profile model for selecting questions by job role
- initial roles: DevOps Engineer, Cloud / Azure, IT Infrastructure, IT Support, Linux / System Administration
- a profile defines only the interview areas/categories and their relative importance
- store profiles as small JSON data files
- no question content inside profiles
- minimum core code to load and validate profiles
- profile loading/validation kept separate from question logic
- no CLI changes, no company profiles, no web code
- Python standard library only
- focused unittest tests
- update relevant documentation and this report
- run the full test suite
- do not commit or push

## Solution

### Data
`data/profiles/` holds one small JSON file per role plus `schema.json` (DEC-004). A profile contains only `id`, `role` and `areas`, where `areas` maps a question category to a positive weight (larger weight = more important for the role). No question text, answers or explanations appear in profiles.

- data/profiles/devops_engineer.json
- data/profiles/cloud_azure.json
- data/profiles/it_infrastructure.json
- data/profiles/it_support.json
- data/profiles/linux_sysadmin.json
- data/profiles/schema.json

### Core code (minimum, separate from question logic)
- `src/core/profile_models.py`: frozen `RoleProfile` dataclass (id, role, areas)
- `src/core/profile_validators.py`: `validate_profile` checks required fields, non-empty id/role, non-empty `areas` object and positive numeric weights. It deliberately does not check category names against the question bank, so profile validation stays independent of question logic.
- `src/core/profile_loader.py`: `load_profiles(profiles_dir=None)` scans a directory, skips `schema.json` and invalid entries, returns `RoleProfile` objects with float weights.
- `src/core/json_io.py`: shared `read_json_file` used by both loaders, so JSON reading is not copied. `src/core/loader.py` now uses it.

No interview-building or weighting logic was added: profiles currently define the data needed to build an interview, and that logic is a separate, later task.

## Files created
- data/profiles/schema.json
- data/profiles/devops_engineer.json
- data/profiles/cloud_azure.json
- data/profiles/it_infrastructure.json
- data/profiles/it_support.json
- data/profiles/linux_sysadmin.json
- src/core/profile_models.py
- src/core/profile_validators.py
- src/core/profile_loader.py
- src/core/json_io.py
- tests/test_profiles.py
- docs/tasks/005-role-profiles.md

## Files updated
- src/core/loader.py (uses shared read_json_file; removed the private copy)
- docs/decisions.md (DEC-004)
- CHANGELOG.md
- README.md
- data/profiles/schema.json (description wording only)

## Validation
- `python3 -m unittest discover -s tests -v`: 42/42 tests passed (8 core + 16 CLI + 18 profiles)
- Profiles load correctly: 5 roles, unique ids, float weights, `schema.json` ignored, invalid/malformed files skipped, missing directory returns no profiles
- A data test asserts every profile area exists in the question bank, so category typos are caught
- No CLI, question data or web code changed; `python3 -m src.cli.main` behavior unchanged