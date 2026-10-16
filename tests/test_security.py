"""Regression checks for local-only Flask security defaults."""

from __future__ import annotations

import unittest

from src.web import create_app


class TestLocalSecurityDefaults(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_secret_key_is_random_per_app_instance(self):
        self.assertNotEqual(self.app.secret_key, create_app().secret_key)
        self.assertGreaterEqual(len(self.app.secret_key), 32)

    def test_cookie_security_settings_match_local_http(self):
        self.assertTrue(self.app.config["SESSION_COOKIE_HTTPONLY"])
        self.assertEqual(self.app.config["SESSION_COOKIE_SAMESITE"], "Lax")
        self.assertFalse(self.app.config["SESSION_COOKIE_SECURE"])

    def test_request_body_size_is_bounded(self):
        self.assertEqual(self.app.config["MAX_CONTENT_LENGTH"], 16 * 1024)
        response = self.client.post(
            "/session", data={"role": "devops-engineer", "count": "1", "padding": "x" * 20000}
        )
        self.assertEqual(response.status_code, 413)

    def test_session_cookie_is_httponly_and_samesite_lax(self):
        response = self.client.post(
            "/session", data={"role": "devops-engineer", "count": "1"}
        )
        cookies = response.headers.getlist("Set-Cookie")
        self.assertTrue(cookies)
        self.assertTrue(any("HttpOnly" in cookie for cookie in cookies))
        self.assertTrue(any("SameSite=Lax" in cookie for cookie in cookies))


if __name__ == "__main__":
    unittest.main()
