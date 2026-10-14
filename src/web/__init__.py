"""Flask application for the web MVP.

This is the product-facing layer. It only wires the reusable core: profile
loading, input validation helpers and interview building stay in `src.core`.
See `src.web.routes` for the routes, `src.web.catalog` for core data and
`src.web.forms` for request validation.
"""

from __future__ import annotations

from flask import Flask

from .routes import bp


def create_app() -> Flask:
    """Create the Flask application with its routes registered."""
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app
