"""Routes for the web MVP interview flow.

Thin controllers: read the request, use the core interview builder and the
local cookie session, and render a template. No business logic and no
duplicate filtering or weighting.
"""

from __future__ import annotations

from flask import Blueprint, redirect, render_template, request, url_for

from src.core.interview_builder import build_interview
from src.core.models import Question

from . import session_state
from .catalog import Catalog, difficulty_options, load_catalog, load_questions_by_id
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


def _render_question(
    question: Question,
    number: int,
    total: int,
    *,
    revealed: bool = False,
    answer: str = "",
):
    return render_template(
        "question.html",
        question=question,
        number=number,
        total=total,
        is_last=number >= total,
        revealed=revealed,
        answer=answer,
    )


def _current_question() -> Question | None:
    question_id = session_state.current_question_id()
    if question_id is None:
        return None
    return load_questions_by_id().get(question_id)


@bp.get("/")
def home():
    """Show the interview request form."""
    return _render_home(load_catalog(), {}, [])


@bp.post("/session")
def create_session():
    """Validate the request, build a session and redirect to its first question."""
    catalog = load_catalog()
    session_request, errors = parse_session_request(request.form, catalog)
    if session_request is None:
        return _render_home(catalog, request.form, errors, status=400)

    interview = build_interview(
        session_request.role,
        list(load_questions_by_id().values()),
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

    session_state.start([question.id for question in interview.questions])
    return redirect(url_for("main.question"))


@bp.get("/session/question")
def question():
    """Show the current question without exposing the reference answer."""
    if not session_state.is_active():
        return redirect(url_for("main.home"))
    if session_state.is_complete():
        return redirect(url_for("main.complete"))

    current = _current_question()
    if current is None:
        session_state.clear()
        return redirect(url_for("main.home"))

    return _render_question(
        current,
        session_state.current_index() + 1,
        session_state.total(),
    )


@bp.post("/session/answer")
def answer():
    """Reveal the answer for the current question or move to the next one."""
    if not session_state.is_active():
        return redirect(url_for("main.home"))
    if session_state.is_complete():
        return redirect(url_for("main.complete"))

    current = _current_question()
    if current is None:
        session_state.clear()
        return redirect(url_for("main.home"))

    action = request.form.get("action", "")
    if action == "reveal":
        return _render_question(
            current,
            session_state.current_index() + 1,
            session_state.total(),
            revealed=True,
            answer=request.form.get("answer", ""),
        )
    if action == "next":
        session_state.advance()
        if session_state.is_complete():
            return redirect(url_for("main.complete"))
        return redirect(url_for("main.question"))

    return redirect(url_for("main.question"))


@bp.get("/session/complete")
def complete():
    """Show the completion screen once every question has been passed."""
    if not session_state.is_active():
        return redirect(url_for("main.home"))
    if not session_state.is_complete():
        return redirect(url_for("main.question"))
    return render_template("complete.html", total=session_state.total())


@bp.post("/session/new")
def new_session():
    """Clear the current interview and return to the request form."""
    session_state.clear()
    return redirect(url_for("main.home"))
