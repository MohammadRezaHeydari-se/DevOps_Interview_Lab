from __future__ import annotations

import html
import re
import unittest

from src.core.loader import load_questions
from src.core.profile_models import RoleProfile
from src.web import create_app
from src.web.catalog import Catalog
from src.web.forms import parse_session_request

QUESTION_TEXT_RE = re.compile(r'<p class="question-text">(.*?)</p>', re.S)


def current_question_text(body: str) -> str:
    match = QUESTION_TEXT_RE.search(body)
    assert match is not None, "question text not found in page"
    return html.unescape(match.group(1).strip())


def make_role(role_id: str, role: str) -> RoleProfile:
    return RoleProfile(id=role_id, role=role, areas={"Linux": 1.0})


class TestHomePage(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_home_returns_form(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn('name="role"', body)
        self.assertNotIn('name="company"', body)
        self.assertIn('name="difficulty"', body)
        self.assertIn('name="count"', body)

    def test_home_lists_existing_roles(self):
        body = self.client.get("/").get_data(as_text=True)
        self.assertIn("DevOps Engineer", body)
        self.assertIn("IT Support", body)

    def test_home_lists_difficulties_without_company_names(self):
        body = self.client.get("/").get_data(as_text=True)
        self.assertNotIn("Kreab", body)
        self.assertIn("All difficulties", body)
        self.assertIn("junior", body)

    def test_stylesheet_is_served(self):
        response = self.client.get("/static/style.css")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/css", response.content_type)
        response.close()


class TestCreateSession(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_create_redirects_to_question(self):
        response = self.client.post(
            "/session", data={"role": "devops-engineer", "count": "2"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/session/question", response.headers["Location"])

    def test_valid_request_starts_interview(self):
        response = self.client.post(
            "/session",
            data={
                "role": "devops-engineer",
                "company": "",
                "difficulty": "",
                "count": "5",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("Question 1 of 5", body)
        self.assertIn('name="answer"', body)

    def test_requested_count_is_reflected(self):
        response = self.client.post(
            "/session",
            data={"role": "devops-engineer", "count": "2"},
            follow_redirects=True,
        )
        self.assertIn("Question 1 of 2", response.get_data(as_text=True))

    def test_count_larger_than_bank_shows_available(self):
        response = self.client.post(
            "/session",
            data={"role": "devops-engineer", "count": "100"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Question 1 of", response.get_data(as_text=True))


class TestInterviewFlow(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def start(self, count: int = 3):
        return self.client.post(
            "/session",
            data={"role": "devops-engineer", "count": str(count)},
            follow_redirects=True,
        )

    def test_interview_has_distinct_interviewer_and_response_panels(self):
        body = self.start(count=2).get_data(as_text=True)
        self.assertIn('class="interview-grid"', body)
        self.assertIn('class="interviewer-panel"', body)
        self.assertIn('class="candidate-panel"', body)
        self.assertIn('aria-label="Interview progress"', body)

    def test_revealed_reference_appears_after_response(self):
        self.start(count=1)
        body = self.client.post(
            "/session/answer", data={"action": "reveal", "answer": "My approach"}
        ).get_data(as_text=True)
        self.assertIn('class="reference-panel"', body)
        self.assertIn("My approach", body)
        self.assertIn("Explanation", body)

    def test_first_question_hides_reference_answer(self):
        body = self.start(count=5).get_data(as_text=True)
        self.assertIn("Question 1 of 5", body)
        self.assertIn('name="answer"', body)
        self.assertNotIn("Short answer", body)
        for question in load_questions():
            self.assertNotIn(question.shortAnswer, body)

    def test_question_order_is_stable_on_refresh(self):
        self.start(count=3)
        first = current_question_text(
            self.client.get("/session/question").get_data(as_text=True)
        )
        second = current_question_text(
            self.client.get("/session/question").get_data(as_text=True)
        )
        self.assertEqual(first, second)

    def test_reveal_shows_reference_answer_without_advancing(self):
        self.start(count=2)
        text = current_question_text(
            self.client.get("/session/question").get_data(as_text=True)
        )
        body = self.client.post(
            "/session/answer",
            data={"action": "reveal", "answer": "draft answer"},
            follow_redirects=True,
        ).get_data(as_text=True)
        self.assertIn("Question 1 of 2", body)
        self.assertIn("Short answer", body)
        self.assertIn("Explanation", body)
        self.assertIn("draft answer", body)
        self.assertIn(text, body)

        refreshed = self.client.get("/session/question").get_data(as_text=True)
        self.assertNotIn("Short answer", refreshed)

    def test_next_navigates_without_repeats_until_complete(self):
        self.start(count=3)
        seen = []
        for number in range(1, 4):
            body = self.client.get("/session/question").get_data(as_text=True)
            self.assertIn(f"Question {number} of 3", body)
            text = current_question_text(body)
            self.assertNotIn(text, seen)
            seen.append(text)

            revealed = self.client.post(
                "/session/answer",
                data={"action": "reveal", "answer": "x"},
                follow_redirects=True,
            ).get_data(as_text=True)
            self.assertIn("Short answer", revealed)
            self.assertIn(text, revealed)

            advance = self.client.post(
                "/session/answer", data={"action": "next"}, follow_redirects=True
            )

        self.assertIn("Interview complete", advance.get_data(as_text=True))

    def test_last_question_offers_finish(self):
        self.start(count=3)
        self.client.post("/session/answer", data={"action": "next"}, follow_redirects=True)
        self.client.post("/session/answer", data={"action": "next"}, follow_redirects=True)
        body = self.client.get("/session/question").get_data(as_text=True)
        self.assertIn("Question 3 of 3", body)
        self.assertIn("Finish interview", body)

    def test_report_shows_role_and_self_rated_score(self):
        self.start(count=1)
        self.client.post(
            "/session/answer",
            data={"action": "next", "self_assessment": "got-it"},
        )
        body = self.client.get("/session/complete").get_data(as_text=True)
        self.assertIn("DevOps Engineer", body)
        self.assertIn("100", body)
        self.assertIn("Self-rated confidence", body)
        self.assertIn("Skill breakdown", body)

    def test_unrated_interview_does_not_claim_match_score(self):
        self.start(count=1)
        self.client.post("/session/answer", data={"action": "next"})
        body = self.client.get("/session/complete").get_data(as_text=True)
        self.assertIn("Not enough information", body)
        self.assertIn("Not rated", body)

    def test_completion_screen(self):
        self.start(count=1)
        response = self.client.post(
            "/session/answer", data={"action": "next"}, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("Interview complete", body)
        self.assertIn("1 question", body)

    def test_question_after_completion_redirects_to_complete(self):
        self.start(count=1)
        self.client.post("/session/answer", data={"action": "next"}, follow_redirects=True)
        response = self.client.get("/session/question")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/session/complete", response.headers["Location"])

    def test_start_new_interview_clears_session(self):
        self.start(count=1)
        self.client.post("/session/answer", data={"action": "next"}, follow_redirects=True)
        home = self.client.post("/session/new", follow_redirects=True).get_data(as_text=True)
        self.assertIn("Configure your session", home)
        self.assertEqual(self.client.get("/session/question").status_code, 302)


class TestPracticeExperience(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_answer_textarea_is_optional(self):
        self.client.post("/session", data={"role": "devops-engineer", "count": "1"}, follow_redirects=True)
        question = self.client.get("/session/question").get_data(as_text=True)
        self.assertIn("Your answer (optional)", question)

    def test_reveal_with_empty_answer(self):
        self.client.post("/session", data={"role": "devops-engineer", "count": "1"}, follow_redirects=True)
        response = self.client.post("/session/answer", data={"action": "reveal"}, follow_redirects=True)
        body = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Short answer", body)
        self.assertIn("Explanation", body)

    def test_self_assessment_radio_choices_present(self):
        self.client.post("/session", data={"role": "devops-engineer", "count": "1"}, follow_redirects=True)
        body = self.client.get("/session/question").get_data(as_text=True)
        self.assertIn('value="got-it"', body)
        self.assertIn('value="partly"', body)
        self.assertIn('value="need-practice"', body)
        self.assertIn("subjective", body.lower())

    def test_missing_assessment_is_handled_safely(self):
        self.client.post("/session", data={"role": "devops-engineer", "count": "1"}, follow_redirects=True)
        response = self.client.post("/session/answer", data={"action": "next"}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Interview complete", response.get_data(as_text=True))

    def test_invalid_assessment_is_ignored(self):
        self.client.post("/session", data={"role": "devops-engineer", "count": "1"}, follow_redirects=True)
        response = self.client.post(
            "/session/answer",
            data={"action": "next", "self_assessment": "invalid"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("Interview complete", body)
        self.assertNotIn("Self-assessment summary", body)

    def test_self_assessment_stored_for_correct_question(self):
        self.client.post("/session", data={"role": "devops-engineer", "count": "1"}, follow_redirects=True)
        self.client.post(
            "/session/answer",
            data={"action": "next", "self_assessment": "got-it"},
            follow_redirects=True,
        )
        body = self.client.get("/session/complete").get_data(as_text=True)
        self.assertIn("Self-assessment summary", body)
        self.assertIn("got-it", body)

    def test_assessments_persist_across_navigation(self):
        self.client.post("/session", data={"role": "devops-engineer", "count": "2"}, follow_redirects=True)
        self.client.post(
            "/session/answer",
            data={"action": "next", "self_assessment": "need-practice"},
            follow_redirects=True,
        )
        body = self.client.get("/session/question").get_data(as_text=True)
        self.assertIn("Question 2 of 2", body)
        self.client.post(
            "/session/answer",
            data={"action": "next", "self_assessment": "partly"},
            follow_redirects=True,
        )
        complete = self.client.get("/session/complete").get_data(as_text=True)
        self.assertIn("Self-assessment summary", complete)
        self.assertIn("need-practice", complete)
        self.assertIn("partly", complete)

    def test_completion_summary_shows_correct_counts(self):
        self.client.post("/session", data={"role": "devops-engineer", "count": "2"}, follow_redirects=True)
        self.client.post(
            "/session/answer",
            data={"action": "next", "self_assessment": "got-it"},
            follow_redirects=True,
        )
        self.client.post(
            "/session/answer",
            data={"action": "next", "self_assessment": "got-it"},
            follow_redirects=True,
        )
        body = self.client.get("/session/complete").get_data(as_text=True)
        self.assertIn("2 questions", body)
        self.assertIn("Self-assessment summary", body)
        self.assertEqual(body.count("got-it"), 2)

    def test_start_new_interview_clears_assessments(self):
        self.client.post("/session", data={"role": "devops-engineer", "count": "1"}, follow_redirects=True)
        self.client.post(
            "/session/answer",
            data={"action": "next", "self_assessment": "got-it"},
            follow_redirects=True,
        )
        self.client.post("/session/new", follow_redirects=True)
        self.client.post("/session", data={"role": "devops-engineer", "count": "1"}, follow_redirects=True)
        self.client.post("/session/answer", data={"action": "next"}, follow_redirects=True)
        complete = self.client.get("/session/complete").get_data(as_text=True)
        self.assertNotIn("Self-assessment summary", complete)



class TestInvalidNavigation(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_question_without_session_redirects_home(self):
        response = self.client.get("/session/question")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/")

    def test_answer_without_session_redirects_home(self):
        response = self.client.post("/session/answer", data={"action": "next"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/")

    def test_complete_without_session_redirects_home(self):
        response = self.client.get("/session/complete")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/")

    def test_complete_before_finish_redirects_to_question(self):
        self.client.post("/session", data={"role": "devops-engineer", "count": "2"})
        response = self.client.get("/session/complete")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/session/question", response.headers["Location"])

    def test_unknown_action_keeps_current_question(self):
        self.client.post("/session", data={"role": "devops-engineer", "count": "2"})
        response = self.client.post(
            "/session/answer", data={"action": "bogus"}, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Question 1 of 2", response.get_data(as_text=True))


class TestValidationErrors(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def post(self, **data):
        return self.client.post("/session", data=data)

    def test_missing_role(self):
        response = self.post(count="3")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Please choose a role", response.get_data(as_text=True))

    def test_unknown_role(self):
        response = self.post(role="astronaut", count="3")
        self.assertEqual(response.status_code, 400)
        self.assertIn("role from the list", response.get_data(as_text=True))

    def test_unknown_difficulty(self):
        response = self.post(role="devops-engineer", difficulty="expert", count="3")
        self.assertEqual(response.status_code, 400)
        self.assertIn("difficulty from the list", response.get_data(as_text=True))

    def test_non_numeric_count(self):
        response = self.post(role="devops-engineer", count="abc")
        self.assertEqual(response.status_code, 400)
        self.assertIn("whole number", response.get_data(as_text=True))

    def test_count_out_of_range(self):
        for count in ("0", "101"):
            response = self.post(role="devops-engineer", count=count)
            self.assertEqual(response.status_code, 400, count)
            self.assertIn("between 1 and 100", response.get_data(as_text=True))

    def test_no_matching_questions(self):
        response = self.post(role="devops-engineer", difficulty="senior", count="3")
        self.assertEqual(response.status_code, 400)
        self.assertIn("No questions match", response.get_data(as_text=True))

    def test_submitted_values_are_preserved_on_error(self):
        response = self.post(role="devops-engineer", count="abc")
        self.assertIn('value="devops-engineer" selected', response.get_data(as_text=True))


class TestSessionRequestValidation(unittest.TestCase):
    def setUp(self):
        self.catalog = Catalog(
            roles=[make_role("r1", "Role One"), make_role("r2", "Role Two")],
            companies=[],
        )

    def test_valid_role_request_is_built(self):
        request, errors = parse_session_request(
            {"role": "r1", "difficulty": "", "count": "5"},
            self.catalog,
        )
        self.assertEqual(errors, [])
        self.assertIsNotNone(request)
        self.assertEqual(request.role.id, "r1")
        self.assertIsNone(request.difficulty)
        self.assertEqual(request.count, 5)

    def test_role_request_does_not_need_company(self):
        request, errors = parse_session_request(
            {"role": "r1", "difficulty": "junior", "count": "2"},
            self.catalog,
        )
        self.assertEqual(errors, [])
        self.assertEqual(request.difficulty, "junior")

    def test_company_field_is_ignored_when_submitted(self):
        request, errors = parse_session_request(
            {"role": "r1", "company": "unknown", "count": "2"},
            self.catalog,
        )
        self.assertEqual(errors, [])
        self.assertEqual(request.role.id, "r1")


if __name__ == "__main__":
    unittest.main()
