"""Routes for the web MVP.

Thin controllers: load core data, validate the submitted request, ask the core
interview builder for a session and render a template. No business logic.
"""

from __future__ import annotations

from flask import Blueprint, render_template, request

from src.core.interview_builder import build_interview
from src.core.loader import load_questions

from .catalog import Catalog, difficulty_options, load_catalog
from .forms import parse_session_request

bp = Blueprint("main", __name__)


def _render_home(catalog: Catalog, form, errors, status: int = 200):
    return (
        render_template(
            "home.html",
            catalog=catalog,
            difficulties=difficulty_options(),
            form=form,
            errors=errors,
        ),
        status,
    )


@bp.get("/")
def home():
    """Show the interview request form."""
    return _render_home(load_catalog(), {}, [])


@bp.post("/session")
def create_session():
    """Validate the request, build a session and show its first question."""
    catalog = load_catalog()
    session_request, errors = parse_session_request(request.form, catalog)
    if session_request is None:
        return _render_home(catalog, request.form, errors, status=400)

    interview = build_interview(
        session_request.role,
        load_questions(),
        company=session_request.company,
        difficulty=session_request.difficulty,
        count=session_request.count,
    )
    if not interview.questions:
        return _render_home(
            catalog,
            request.form,
            ["No questions match that selection. Try another role or difficulty."],
            status=400,
        )

    return render_template(
        "question.html",
        interview=interview,
        question=interview.questions[0],
    )
