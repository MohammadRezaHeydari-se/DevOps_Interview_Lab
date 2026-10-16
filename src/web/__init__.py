"""Flask application for the web MVP.

This is the product-facing layer. It only wires the reusable core: profile
loading, input validation helpers and interview building stay in `src.core`.
See `src.web.routes` for the routes, `src.web.catalog` for core data,
`src.web.forms` for request validation and `src.web.session_state` for the
local interview state.
"""

from __future__ import annotations

import secrets

from flask import Flask

from .routes import bp


def create_app() -> Flask:
    """Create the Flask application with its routes registered."""
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=secrets.token_hex(32),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,  # Local HTTP only; enable for any HTTPS deployment.
        MAX_CONTENT_LENGTH=16 * 1024,  # Interview forms contain only short text.
    )
    app.register_blueprint(bp)
    return app
