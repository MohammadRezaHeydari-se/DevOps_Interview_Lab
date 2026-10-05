# AGENTS.md - Permanent instructions for AI coding assistants

These instructions apply to all AI coding assistants working on the DevOps Interview Lab repository. They are intended to be followed for every task.

## Core principles

- Keep changes minimal. Follow the "one task at a time" principle.
- Avoid overengineering. Prefer simple, readable solutions.
- Never implement functionality that was not explicitly requested.
- Do not refactor unrelated code.
- Production readiness will be added gradually.

## Product direction

- The final product is a web application. No web framework, frontend stack, or deployment model has been selected yet, and no such choice may be made unless it is explicitly requested.
- The CLI in `src/cli` is a temporary development and testing interface for the reusable core. It is not the product and must not become one.
- Do not expand the CLI beyond its current scope: no new features, options, or layers of convenience.
- The reusable core in `src/core` must stay independent from the CLI and from any future web UI.
- Anything that will be reused by the web UI belongs in the core, not in `src/cli`.

## Before making changes

1. **Inspect the repository**: Read relevant files and understand the existing state before changing anything.
2. **Preserve existing structure**: Respect the current architecture and conventions. Do not reorganize files unless explicitly requested.
3. **Understand scope**: Confirm the task is explicitly requested and within scope.
4. **Plan minimally**: Only plan the change needed to satisfy the current task.

## While working

1. **Make the smallest reasonable change**: Only modify what is necessary to complete the task.
2. **Preserve the existing architecture**: Do not restructure or redesign unless explicitly asked.
3. **Document important changes**: If a change affects behavior, architecture, contracts, or significant decisions, explain and document it.
4. **Update relevant documentation**: When architecture or behavior changes, update README.md, docs/architecture.md, docs/decisions.md, CHANGELOG.md, or other relevant docs.
5. **Avoid speculation**: Do not add TODOs, placeholders, or future features unless explicitly requested.

## Maintainability rules

These rules are permanent and apply to every change.

- Prefer small focused files and functions.
- Do not create large catch-all files. A file has one clear responsibility.
- Split code when a file contains multiple clear responsibilities.
- Keep UI, business logic, data access and validation separate.
- Avoid god classes, god modules and giant main files.
- Reuse shared logic instead of copying it; one behavior has one implementation.
- New features must not be added to an existing file just because it is convenient. Create the focused module it belongs in.
- Keep the reusable core independent from the CLI and from any future web UI.

## Code quality

- **No duplicate resources**: Never create duplicate database connections or infrastructure clients. Shared resources must go through a centralized, reusable project service/layer.
- **Right design style**: Use functional design for simple/stateless logic; use OOP only when objects, state, or domain behavior justify it.
- **Modular, not fragmented**: Use the selected framework's native modular structure when applicable. Avoid large monolithic files, but split files only when there is a clear responsibility boundary.
- **No speculative abstractions**: Do not create abstractions the current task does not require.
- **No new dependencies**: Do not add dependencies without explicit approval.

## Before considering a task complete

1. **Verify scope**: Ensure you only did what was asked and no more.
2. **Run available tests/checks**: Look for and run any tests, linters, typecheckers, or other checks that exist in the repository. If none exist, note it briefly.
3. **Review your changes**: Check that each modified/created file has a clear purpose and matches the project's style.
4. **Verify documentation is consistent**: If you changed behavior/architecture, ensure docs are updated.
5. **Confirm no unintended artifacts**: No temporary files, debug code, or unrelated edits.

## Repository boundaries

- **Implementer role**: OpenCode is an implementer, not the project architect. Follow only the explicitly assigned task; never invent features or architecture.
- **Repository root only**: Determine the repository root with `git rev-parse --show-toplevel` and do all work inside it. Never inspect or modify files outside it, do not use `../`, and do not scan parent/sibling directories, the home directory, or unrelated repositories. If a tool returns files outside the repository, stop using those results.
- **Explicit scope**: Follow the explicit task scope. Do not read or modify unrelated files, and do not implement or suggest the next task; the next task must be provided explicitly by the project owner.
- **Explicit task tracking**: Every development task must have an explicit TASK ID.
- **Missing decisions**: If a required decision is missing, stop and report it rather than inventing one.
- **Technology choices**: Do not choose technologies, frameworks, libraries, or architectural patterns unless explicitly instructed.

## Git safety

- Never run `git init`, `git commit`, `git push`, remote changes, or destructive Git commands unless explicitly requested by the project owner.
- Read-only inspection (`git status`, `git diff`, `git log`, `git rev-parse`) is allowed; anything that writes history, refs, remotes, or the working tree state requires an explicit request.

## Notes

- The developer must be able to understand and explain every part of the project.
- Architecture will be decided incrementally. Do not preemptively select frameworks, libraries, or deployment patterns.
