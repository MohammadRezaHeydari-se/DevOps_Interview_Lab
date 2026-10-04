# TASK-002: Build the initial interview question bank

## Goal
Create a minimal, reusable question model and initial bank of 20 realistic junior/LIA questions in JSON format, organized by category so categories can grow without creating one giant file.

## Requirements
- Use JSON for question data
- Define minimal reusable question model and create initial bank of 20 realistic junior/LIA questions covering: HR / LIA, Linux, Networking, Azure, Active Directory / Entra ID, Git / CI/CD, Docker, Troubleshooting
- Each question must support: id, category, difficulty, type, question, shortAnswer, explanation, followUps
- Organize data so categories can grow without creating one giant file
- Update docs/decisions.md and create docs/tasks/002-question-bank.md
- No application code, UI, API, database, framework, or dependencies
- Validate all JSON
- Do not commit or push

## Solution
- Created `data/questions/` with category files (3 each for 8 categories = 24 questions; realistic junior/LIA).
- Added `data/questions/schema.json` describing the reusable model and allowed values.
- Updated `docs/decisions.md` with DEC-002.
- Validated JSON structure and required fields.

## Files created/updated
- data/questions/schema.json (new)
- data/questions/hr_lia.json (new)
- data/questions/linux.json (new)
- data/questions/networking.json (new)
- data/questions/azure.json (new)
- data/questions/entra_ad.json (new)
- data/questions/git_cicd.json (new)
- data/questions/docker.json (new)
- data/questions/troubleshooting.json (new)
- docs/decisions.md (updated)
- docs/tasks/002-question-bank.md (new)

## Validation
Validated all JSON files load correctly; required fields present per schema. Total 24 questions across 8 categories.