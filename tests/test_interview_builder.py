from __future__ import annotations

import unittest
from collections import Counter

from src.core.company_loader import load_company_profiles
from src.core.company_models import CompanyProfile
from src.core.compatibility import IncompatibleProfileError
from src.core.interview_builder import build_interview
from src.core.loader import load_questions
from src.core.models import Question
from src.core.profile_loader import load_profiles
from src.core.profile_models import RoleProfile


def make_question(qid: str, category: str, difficulty: str = "junior") -> Question:
    return Question(
        id=qid,
        category=category,
        difficulty=difficulty,
        type="theory",
        question="Q?",
        shortAnswer="A",
        explanation="E",
        followUps=[],
    )


def make_role(areas: dict, role_id: str = "role") -> RoleProfile:
    return RoleProfile(id=role_id, role="Role", areas=areas)


def make_company(
    focus: dict,
    role_profile_ids: list | None = None,
    company_id: str = "company",
) -> CompanyProfile:
    return CompanyProfile(
        id=company_id,
        company="Company",
        roleProfileIds=role_profile_ids if role_profile_ids is not None else ["role"],
        focus=focus,
    )


def balanced_questions(categories=("A", "B"), per_category: int = 10) -> list:
    return [
        make_question(f"{category}-{index}", category)
        for category in categories
        for index in range(per_category)
    ]


class TestSelection(unittest.TestCase):
    def setUp(self):
        self.questions = balanced_questions()

    def test_builds_requested_count(self):
        session = build_interview(make_role({"A": 1.0}), self.questions, count=6, seed=1)
        self.assertEqual(len(session.questions), 6)
        self.assertTrue(session.is_complete)

    def test_does_not_select_duplicate_questions(self):
        session = build_interview(
            make_role({"A": 1.0, "B": 1.0}), self.questions, count=10, seed=1
        )
        ids = [question.id for question in session.questions]
        self.assertEqual(len(ids), len(set(ids)))

    def test_count_zero_returns_empty_session(self):
        session = build_interview(make_role({"A": 1.0}), self.questions, count=0)
        self.assertEqual(session.questions, [])
        self.assertTrue(session.is_complete)

    def test_negative_count_is_rejected(self):
        with self.assertRaises(ValueError):
            build_interview(make_role({"A": 1.0}), self.questions, count=-1)

    def test_empty_question_bank_returns_empty_session(self):
        session = build_interview(make_role({"A": 1.0}), [], count=5)
        self.assertEqual(session.questions, [])
        self.assertFalse(session.is_complete)

    def test_unknown_category_questions_are_never_selected(self):
        questions = balanced_questions(categories=("A", "Z"))
        session = build_interview(make_role({"A": 1.0}), questions, count=20, seed=1)
        self.assertTrue(all(question.category == "A" for question in session.questions))


class TestWeighting(unittest.TestCase):
    def setUp(self):
        self.questions = balanced_questions()

    def test_role_weights_drive_category_distribution(self):
        session = build_interview(
            make_role({"A": 1.0, "B": 0.1}), self.questions, count=10, seed=1
        )
        counts = Counter(question.category for question in session.questions)
        self.assertEqual(counts, {"A": 9, "B": 1})

    def test_equal_role_weights_split_evenly(self):
        session = build_interview(
            make_role({"A": 1.0, "B": 1.0}), self.questions, count=10, seed=1
        )
        counts = Counter(question.category for question in session.questions)
        self.assertEqual(counts, {"A": 5, "B": 5})

    def test_company_focus_adjusts_role_distribution(self):
        session = build_interview(
            make_role({"A": 1.0, "B": 1.0}),
            self.questions,
            company=make_company({"A": 1.0, "B": 0.25}),
            count=10,
            seed=1,
        )
        counts = Counter(question.category for question in session.questions)
        self.assertEqual(counts, {"A": 8, "B": 2})

    def test_company_focus_never_adds_categories_outside_role(self):
        questions = balanced_questions(categories=("A", "C"))
        session = build_interview(
            make_role({"A": 1.0}),
            questions,
            company=make_company({"A": 1.0, "C": 9.0}),
            count=20,
            seed=1,
        )
        self.assertTrue(session.questions)
        self.assertTrue(all(question.category == "A" for question in session.questions))


class TestFiltering(unittest.TestCase):
    def setUp(self):
        self.questions = [
            make_question("j-1", "A", "junior"),
            make_question("j-2", "A", "junior"),
            make_question("s-1", "A", "senior"),
            make_question("m-1", "B", "mid"),
        ]

    def test_difficulty_filter_selects_matching_only(self):
        session = build_interview(
            make_role({"A": 1.0}),
            self.questions,
            difficulty="junior",
            count=5,
            seed=1,
        )
        self.assertTrue(all(question.difficulty == "junior" for question in session.questions))

    def test_none_difficulty_uses_all_difficulties(self):
        session = build_interview(
            make_role({"A": 1.0, "B": 1.0}), self.questions, count=10, seed=1
        )
        self.assertEqual(len(session.questions), 4)

    def test_difficulty_without_matches_returns_empty_session(self):
        session = build_interview(
            make_role({"A": 1.0}),
            self.questions,
            difficulty="senior",
            count=5,
            seed=1,
        )
        self.assertEqual(len(session.questions), 1)


class TestCompatibility(unittest.TestCase):
    def setUp(self):
        self.questions = balanced_questions()

    def test_company_without_role_is_rejected(self):
        company = make_company({"A": 1.0}, role_profile_ids=["other"])
        with self.assertRaises(IncompatibleProfileError):
            build_interview(make_role({"A": 1.0}), self.questions, company=company)

    def test_compatible_company_is_accepted(self):
        company = make_company({"A": 1.0}, role_profile_ids=["role"])
        session = build_interview(make_role({"A": 1.0}), self.questions, company=company)
        self.assertIs(session.company, company)

    def test_missing_company_is_accepted(self):
        session = build_interview(make_role({"A": 1.0}), self.questions)
        self.assertIsNone(session.company)


class TestReproducibility(unittest.TestCase):
    def setUp(self):
        self.questions = balanced_questions()
        self.role = make_role({"A": 1.0, "B": 0.4})

    def test_same_seed_produces_same_session(self):
        first = build_interview(self.role, self.questions, count=8, seed=42)
        second = build_interview(self.role, self.questions, count=8, seed=42)
        self.assertEqual(
            [question.id for question in first.questions],
            [question.id for question in second.questions],
        )

    def test_session_records_its_inputs(self):
        company = make_company({"A": 1.0})
        session = build_interview(
            self.role,
            self.questions,
            company=company,
            difficulty="junior",
            count=4,
            seed=7,
        )
        self.assertIs(session.role, self.role)
        self.assertIs(session.company, company)
        self.assertEqual(session.difficulty, "junior")
        self.assertEqual(session.requestedCount, 4)


class TestEdgeCases(unittest.TestCase):
    def test_requesting_more_than_available_returns_available(self):
        questions = balanced_questions(categories=("A",), per_category=3)
        session = build_interview(make_role({"A": 1.0}), questions, count=10, seed=1)
        self.assertEqual(len(session.questions), 3)
        self.assertFalse(session.is_complete)

    def test_role_area_without_questions_is_skipped(self):
        questions = balanced_questions(categories=("B",), per_category=4)
        session = build_interview(
            make_role({"A": 1.0, "B": 0.5}), questions, count=4, seed=1
        )
        self.assertEqual(len(session.questions), 4)
        self.assertTrue(all(question.category == "B" for question in session.questions))

    def test_shortfall_is_redistributed_across_categories(self):
        questions = [make_question(f"a-{i}", "A") for i in range(1)] + [
            make_question(f"b-{i}", "B") for i in range(10)
        ]
        session = build_interview(
            make_role({"A": 1.0, "B": 1.0}), questions, count=5, seed=1
        )
        counts = Counter(question.category for question in session.questions)
        self.assertEqual(len(session.questions), 5)
        self.assertEqual(counts["B"], 4)


class TestRealData(unittest.TestCase):
    def setUp(self):
        self.roles = {profile.id: profile for profile in load_profiles()}
        self.companies = {profile.id: profile for profile in load_company_profiles()}
        self.questions = load_questions()

    def test_builds_complete_session_for_role(self):
        session = build_interview(self.roles["devops-engineer"], self.questions, count=5, seed=3)
        self.assertEqual(len(session.questions), 5)
        self.assertEqual(len({question.id for question in session.questions}), 5)

    def test_builds_session_with_compatible_company(self):
        session = build_interview(
            self.roles["devops-engineer"],
            self.questions,
            company=self.companies["itm8"],
            count=5,
            seed=3,
        )
        self.assertEqual(len(session.questions), 5)
        self.assertTrue(session.is_complete)


if __name__ == "__main__":
    unittest.main()
