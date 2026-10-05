from __future__ import annotations

import unittest

from src.cli.prompts import resolve_choice, resolve_count
from src.cli.rendering import (
    ALL,
    format_answer,
    format_explanation,
    format_menu,
    format_question,
)
from src.cli.session import available_options, build_session
from src.core.loader import load_questions
from src.core.models import Question


def make_question(**overrides) -> Question:
    data = {
        "id": "t-001",
        "category": "Linux",
        "difficulty": "junior",
        "type": "theory",
        "question": "What is a process?",
        "shortAnswer": "A running program instance.",
        "explanation": "The kernel keeps a process table.",
        "followUps": ["What is a PID?"],
    }
    data.update(overrides)
    return Question(**data)


class TestChoices(unittest.TestCase):
    def setUp(self):
        self.options = ["Azure", "Linux"]

    def test_resolve_choice_all_variants(self):
        for text in ("", "  ", ALL, "All", " all "):
            self.assertIsNone(resolve_choice(text, self.options))

    def test_resolve_choice_returns_option(self):
        self.assertEqual(resolve_choice(" Linux ", self.options), "Linux")

    def test_resolve_choice_rejects_unknown(self):
        with self.assertRaises(ValueError):
            resolve_choice("Kubernetes", self.options)

    def test_resolve_count_parses_and_clamps(self):
        self.assertEqual(resolve_count(" 3 ", 5), 3)
        self.assertEqual(resolve_count("9", 5), 5)

    def test_resolve_count_rejects_invalid(self):
        for text in ("0", "-2", "abc", ""):
            with self.assertRaises(ValueError):
                resolve_count(text, 5)


class TestAvailableOptions(unittest.TestCase):
    def test_sorted_unique_categories(self):
        questions = [
            make_question(id="a", category="Linux"),
            make_question(id="b", category="Azure"),
            make_question(id="c", category="Linux"),
        ]
        self.assertEqual(available_options(questions, "category"), ["Azure", "Linux"])

    def test_difficulty_levels_from_bank(self):
        questions = load_questions()
        levels = available_options(questions, "difficulty")
        self.assertIn("junior", levels)
        self.assertEqual(levels, sorted(levels))


class TestBuildSession(unittest.TestCase):
    def setUp(self):
        self.questions = load_questions()

    def test_filters_by_category_and_difficulty(self):
        session = build_session(self.questions, category="Linux", difficulty="junior", count=50)
        self.assertTrue(all(q.category == "Linux" and q.difficulty == "junior" for q in session))
        self.assertGreaterEqual(len(session), 1)

    def test_respects_requested_count_and_no_duplicates(self):
        session = build_session(self.questions, count=3, seed=7)
        self.assertEqual(len(session), 3)
        self.assertEqual(len({q.id for q in session}), 3)

    def test_same_seed_gives_same_session(self):
        first = build_session(self.questions, count=4, seed=11)
        second = build_session(self.questions, count=4, seed=11)
        self.assertEqual([q.id for q in first], [q.id for q in second])

    def test_empty_selection_returns_empty_session(self):
        session = build_session(self.questions, category="Linux", count=5)
        self.assertEqual(len(session), len([q for q in self.questions if q.category == "Linux"]))


class TestFormatting(unittest.TestCase):
    def setUp(self):
        self.question = make_question()

    def test_format_menu_lists_all_and_options(self):
        menu = format_menu(["Azure", "Linux"], header="Categories:")
        self.assertIn("Categories:", menu)
        self.assertIn("all", menu)
        self.assertIn("Azure", menu)
        self.assertIn("Linux", menu)

    def test_format_question_shows_progress_and_text(self):
        text = format_question(self.question, 1, 5)
        self.assertIn("Question 1/5", text)
        self.assertIn("Linux (junior)", text)
        self.assertIn("What is a process?", text)

    def test_format_answer_shows_short_answer(self):
        self.assertIn("A running program instance.", format_answer(self.question))

    def test_format_explanation_lists_follow_ups(self):
        text = format_explanation(self.question)
        self.assertIn("The kernel keeps a process table.", text)
        self.assertIn("What is a PID?", text)

    def test_format_explanation_without_follow_ups(self):
        text = format_explanation(make_question(followUps=[]))
        self.assertNotIn("Follow-up questions:", text)


if __name__ == "__main__":
    unittest.main()