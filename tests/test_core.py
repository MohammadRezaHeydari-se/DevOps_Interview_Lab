from __future__ import annotations

import unittest

from src.core.loader import load_questions
from src.core.models import Question
from src.core.selectors import filter_questions, select_random
from src.core.validators import validate_question, ALLOWED_CATEGORIES


class TestCore(unittest.TestCase):
    def setUp(self):
        self.questions = load_questions()

    def test_load_returns_questions(self):
        self.assertGreater(len(self.questions), 0)
        for q in self.questions[:2]:
            self.assertIsInstance(q, Question)

    def test_validate_question_rejects_bad(self):
        bad = {
            "id": "",
            "category": "Unknown",
            "difficulty": "hard",
            "type": "maybe",
            "question": 123,
            "shortAnswer": "",
            "explanation": "",
            "followUps": ["ok", 5],
        }
        ok, errs = validate_question(bad)
        self.assertFalse(ok)
        self.assertTrue(len(errs) > 0)

    def test_validate_question_accepts_good(self):
        good = {
            "id": "t-001",
            "category": "Linux",
            "difficulty": "junior",
            "type": "practical",
            "question": "Q?",
            "shortAnswer": "A",
            "explanation": "E",
            "followUps": ["f1"],
        }
        ok, errs = validate_question(good)
        self.assertTrue(ok)
        self.assertEqual(errs, [])

    def test_filter_by_category(self):
        res = filter_questions(self.questions, category="Linux")
        self.assertTrue(all(q.category == "Linux" for q in res))
        self.assertGreaterEqual(len(res), 1)

    def test_filter_by_difficulty_and_type(self):
        res = filter_questions(self.questions, difficulty="junior", type_="theory")
        self.assertTrue(all(q.difficulty == "junior" and q.type == "theory" for q in res))

    def test_select_random_no_duplicates_and_deterministic(self):
        pool = self.questions
        s1 = select_random(pool, count=3, seed=42)
        s2 = select_random(pool, count=3, seed=42)
        self.assertEqual([q.id for q in s1], [q.id for q in s2])
        ids = [q.id for q in s1]
        self.assertEqual(len(ids), len(set(ids)))

    def test_all_categories_present(self):
        cats = set(q.category for q in self.questions)
        for c in ALLOWED_CATEGORIES:
            self.assertIn(c, cats)

    def test_followups_are_strings(self):
        for q in self.questions:
            for f in q.followUps:
                self.assertIsInstance(f, str)


if __name__ == "__main__":
    unittest.main()
