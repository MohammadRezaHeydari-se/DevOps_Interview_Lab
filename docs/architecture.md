# Architecture

**Status:** The target product is a web application. No architecture has been selected yet.

The architecture for DevOps Interview Lab will be decided incrementally as the project evolves. No web framework, frontend stack, data store, or deployment model has been chosen at this stage.

The code that exists today has two clearly separated layers:

- `src/core`: the reusable core. Question models, validation, data loading, selection, profile models and interview building. It has no UI dependency and stays reusable by any future web UI.
- `src/cli`: a temporary development and testing interface for the core. It is not the product and will not be expanded beyond its current scope.

The interview builder in `src/core` composes a weighted interview session from the question bank, a required role profile and an optional company profile. It reuses the existing loaders, selectors and models, and keeps weighting (`src/core/weighting.py`) separate from session building (`src/core/interview_builder.py`).

This approach aligns with the project's philosophy of keeping things simple, avoiding overengineering, and adding production readiness gradually.

## Principles

- Architecture decisions will be made only when needed to support a specific, explicitly requested feature.
- All architectural choices will be documented in [decisions.md](decisions.md).
- The core stays independent from any UI layer.
- Simplicity and clarity will take precedence over premature optimization.
