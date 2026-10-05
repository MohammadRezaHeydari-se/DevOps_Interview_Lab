# TASK-006: Add company interview profiles

## Goal
Add a minimal reusable company profile model so interviews can be tailored per company, without inventing undocumented company requirements, duplicating question content, or adding interview-building logic.

## Requirements
- minimal reusable company profile model
- initial profiles for Kreab, itm8, Ductus
- a company profile may define id, company name, relevant role profile ids, focus areas with relative weights and optional short notes
- no question content in company profiles
- no invented company-specific technical requirements; keep profiles generic where verified information is unavailable
- small JSON files under `data/profiles/companies/`
- minimum loader/model/validator code, reusing shared JSON infrastructure
- company logic kept separate from role profile logic where responsibilities differ
- no CLI changes, no interview-building logic, no web code
- Python standard library only
- focused unittest tests, small single-purpose files and functions
- update relevant docs and this report
- run the full test suite
- do not commit or push

## Solution

### Data
One small JSON file per company plus `schema.json` (DEC-005). Fields: `id`, `company`, `roleProfileIds`, `focus`, optional `notes`.

- data/profiles/companies/kreab.json
- data/profiles/companies/itm8.json
- data/profiles/companies/ductus.json
- data/profiles/companies/schema.json

Content policy: no verified company-specific interview requirements are documented, so the three profiles carry the same generic focus areas over the existing categories and reference all role profiles. Each profile's `notes` states that the focus is generic because no verified company-specific requirements are documented. Any company-specific weighting must be added later from documented facts.

### Core code (minimum, separate from role profiles)
- `src/core/company_models.py`: frozen `CompanyProfile(id, company, roleProfileIds, focus, notes="")`
- `src/core/company_validators.py`: `validate_company_profile` checks required fields, non-empty id/company, non-empty `roleProfileIds` list of non-empty strings, non-empty `focus` object with positive weights, and optional `notes` string. Cross-domain checks stay out of the validator.
- `src/core/company_loader.py`: `load_company_profiles(companies_dir=None)` reads `data/profiles/companies`, skips `schema.json` and invalid entries, reuses `read_json_file` from `src/core/json_io.py`.
- `src/core/validation_rules.py`: shared predicates `is_non_empty_string` and `is_positive_weight`, now used by both profile validators so field validation is not copied.

No interview-building, weighting or selection logic was added.

## Files created
- data/profiles/companies/schema.json
- data/profiles/companies/kreab.json
- data/profiles/companies/itm8.json
- data/profiles/companies/ductus.json
- src/core/company_models.py
- src/core/company_validators.py
- src/core/company_loader.py
- src/core/validation_rules.py
- tests/test_company_profiles.py
- docs/tasks/006-company-profiles.md

## Files updated
- src/core/profile_validators.py (uses the shared predicates)
- docs/decisions.md (DEC-005)
- CHANGELOG.md
- README.md

## Validation
- `python3 -m unittest discover -s tests -v`: 59/59 tests passed (8 core + 16 CLI + 18 role profiles + 17 company profiles)
- 3 company profiles load with unique ids, float weights, `schema.json` skipped; invalid, malformed and non-object files skipped; missing directory returns no profiles
- Data tests assert every `roleProfileIds` entry references an existing role profile and that company profiles carry no question content fields
- Role profile loading still returns exactly 5 profiles (the new subdirectory is not picked up)
- No CLI, question data or web code changed; import audit shows only the standard library