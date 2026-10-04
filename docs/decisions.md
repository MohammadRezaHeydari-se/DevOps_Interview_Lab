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
