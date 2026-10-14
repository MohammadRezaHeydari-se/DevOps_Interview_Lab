# Architecture

**Status:** A minimal Flask web MVP is the current product-facing layer (DEC-007). Broader architecture (data store, deployment) has not been selected yet.

The architecture for DevOps Interview Lab will be decided incrementally as the project evolves. No data store or deployment model has been chosen at this stage.

The code that exists today has three clearly separated layers:

- `src/core`: the reusable core. Question models, validation, data loading, selection, profile models and interview building. It has no UI dependency and stays reusable by any UI layer.
- `src/web`: the product-facing Flask MVP. Server-rendered templates and minimal CSS. It only wires the core (loading, validation, compatibility, interview building) and reimplements no business logic.
- `src/cli`: a temporary development and testing interface for the core. It is not the product and will not be expanded beyond its current scope.

The interview builder in `src/core` composes a weighted interview session from the question bank, a required role profile and an optional company profile. It reuses the existing loaders, selectors and models, and keeps weighting (`src/core/weighting.py`) separate from session building (`src/core/interview_builder.py`).

The web layer keeps routes (`src/web/routes.py`), request validation (`src/web/forms.py`), core data access (`src/web/catalog.py`), local interview state (`src/web/session_state.py`) and presentation (`src/web/templates`, `src/web/static`) separate. Each interview session keeps only the ordered question ids and the current index in Flask's signed-cookie session (DEC-008); no database is used. Flask is the only external dependency (approved for TASK-008).

This approach aligns with the project's philosophy of keeping things simple, avoiding overengineering, and adding production readiness gradually.

## Principles

- Architecture decisions will be made only when needed to support a specific, explicitly requested feature.
- All architectural choices will be documented in [decisions.md](decisions.md).
- The core stays independent from any UI layer.
- Simplicity and clarity will take precedence over premature optimization.
