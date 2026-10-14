from __future__ import annotations

import unittest

from src.core.company_models import CompanyProfile
from src.core.profile_models import RoleProfile
from src.web import create_app
from src.web.catalog import Catalog
from src.web.forms import parse_session_request


def make_role(role_id: str, role: str) -> RoleProfile:
    return RoleProfile(id=role_id, role=role, areas={"Linux": 1.0})


def make_company(company_id: str, company: str, role_ids: list) -> CompanyProfile:
    return CompanyProfile(
        id=company_id,
        company=company,
        roleProfileIds=role_ids,
        focus={"Linux": 1.0},
    )


class TestHomePage(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_home_returns_form(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn('name="role"', body)
        self.assertIn('name="company"', body)
        self.assertIn('name="difficulty"', body)
        self.assertIn('name="count"', body)

    def test_home_lists_existing_roles(self):
        body = self.client.get("/").get_data(as_text=True)
        self.assertIn("DevOps Engineer", body)
        self.assertIn("IT Support", body)

    def test_home_lists_existing_companies_and_difficulties(self):
        body = self.client.get("/").get_data(as_text=True)
        self.assertIn("Kreab", body)
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

    def test_valid_request_shows_first_question(self):
        response = self.client.post(
            "/session",
            data={
                "role": "devops-engineer",
                "company": "",
                "difficulty": "",
                "count": "5",
            },
        )
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("Question 1 of 5", body)
        self.assertIn("Short answer", body)
        self.assertIn("Explanation", body)

    def test_request_with_company_shows_company_name(self):
        response = self.client.post(
            "/session",
            data={"role": "devops-engineer", "company": "itm8", "count": "1"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("itm8", response.get_data(as_text=True))

    def test_requested_count_is_reflected(self):
        response = self.client.post(
            "/session",
            data={"role": "devops-engineer", "count": "2"},
        )
        self.assertIn("Question 1 of 2", response.get_data(as_text=True))

    def test_count_larger_than_bank_shows_available(self):
        response = self.client.post(
            "/session",
            data={"role": "devops-engineer", "count": "100"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Question 1 of", response.get_data(as_text=True))


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

    def test_unknown_company(self):
        response = self.post(role="devops-engineer", company="nope", count="3")
        self.assertEqual(response.status_code, 400)
        self.assertIn("company from the list", response.get_data(as_text=True))

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
            companies=[
                make_company("c1", "Company One", ["r1"]),
                make_company("c2", "Company Two", ["r2"]),
            ],
        )

    def test_valid_request_is_built(self):
        request, errors = parse_session_request(
            {"role": "r1", "company": "c1", "difficulty": "", "count": "5"},
            self.catalog,
        )
        self.assertEqual(errors, [])
        self.assertIsNotNone(request)
        self.assertEqual(request.role.id, "r1")
        self.assertEqual(request.company.id, "c1")
        self.assertIsNone(request.difficulty)
        self.assertEqual(request.count, 5)

    def test_company_is_optional(self):
        request, errors = parse_session_request(
            {"role": "r1", "company": "", "difficulty": "junior", "count": "2"},
            self.catalog,
        )
        self.assertEqual(errors, [])
        self.assertIsNone(request.company)
        self.assertEqual(request.difficulty, "junior")

    def test_incompatible_company_is_rejected(self):
        request, errors = parse_session_request(
            {"role": "r1", "company": "c2", "difficulty": "", "count": "5"},
            self.catalog,
        )
        self.assertIsNone(request)
        self.assertEqual(len(errors), 1)
        self.assertIn("does not offer", errors[0])


if __name__ == "__main__":
    unittest.main()
