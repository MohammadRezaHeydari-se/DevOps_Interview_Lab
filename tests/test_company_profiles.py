from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.core.company_loader import load_company_profiles
from src.core.company_models import CompanyProfile
from src.core.company_validators import validate_company_profile
from src.core.profile_loader import load_profiles

INITIAL_COMPANIES = {"Kreab", "itm8", "Ductus"}


def valid_company(**overrides) -> dict:
    data = {
        "id": "acme",
        "company": "Acme",
        "roleProfileIds": ["it-support"],
        "focus": {"Troubleshooting": 1.0, "HR / LIA": 0.5},
        "notes": "Generic focus.",
    }
    data.update(overrides)
    return data


class TestCompanyValidation(unittest.TestCase):
    def test_accepts_valid_company(self):
        ok, errors = validate_company_profile(valid_company())
        self.assertTrue(ok)
        self.assertEqual(errors, [])

    def test_notes_are_optional(self):
        data = valid_company()
        del data["notes"]
        ok, errors = validate_company_profile(data)
        self.assertTrue(ok)
        self.assertEqual(errors, [])

    def test_rejects_non_object(self):
        ok, errors = validate_company_profile("kreab")
        self.assertFalse(ok)
        self.assertTrue(errors)

    def test_rejects_missing_fields(self):
        ok, errors = validate_company_profile({"id": "acme", "company": "Acme"})
        self.assertFalse(ok)
        self.assertEqual(len(errors), 2)

    def test_rejects_empty_id_or_company(self):
        for field in ("id", "company"):
            ok, errors = validate_company_profile(valid_company(**{field: " "}))
            self.assertFalse(ok)
            self.assertTrue(any(field in error for error in errors))

    def test_rejects_invalid_role_profile_ids(self):
        for value in ([], "it-support", ["it-support", ""], ["it-support", 3]):
            ok, errors = validate_company_profile(valid_company(roleProfileIds=value))
            self.assertFalse(ok, value)
            self.assertTrue(any("roleProfileIds" in error for error in errors))

    def test_rejects_invalid_focus(self):
        for value in ({}, ["Troubleshooting"], {"": 1.0}):
            ok, errors = validate_company_profile(valid_company(focus=value))
            self.assertFalse(ok, value)
            self.assertTrue(errors)

    def test_rejects_invalid_focus_weight(self):
        for weight in (0, -1, "high", True):
            ok, errors = validate_company_profile(valid_company(focus={"Docker": weight}))
            self.assertFalse(ok, weight)
            self.assertTrue(any("Docker" in error for error in errors))

    def test_rejects_non_string_notes(self):
        ok, errors = validate_company_profile(valid_company(notes=42))
        self.assertFalse(ok)
        self.assertTrue(any("notes" in error for error in errors))


class TestCompanyLoading(unittest.TestCase):
    def test_loads_initial_companies(self):
        profiles = load_company_profiles()
        self.assertGreaterEqual(len(profiles), len(INITIAL_COMPANIES))
        for profile in profiles:
            self.assertIsInstance(profile, CompanyProfile)
        self.assertTrue(INITIAL_COMPANIES.issubset({p.company for p in profiles}))

    def test_profile_ids_are_unique(self):
        ids = [p.id for p in load_company_profiles()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_schema_file_is_not_loaded_as_a_profile(self):
        self.assertNotIn("schema", [p.id for p in load_company_profiles()])

    def test_weights_are_normalized_to_floats(self):
        for profile in load_company_profiles():
            for weight in profile.focus.values():
                self.assertIsInstance(weight, float)

    def test_missing_directory_returns_no_profiles(self):
        self.assertEqual(load_company_profiles("data/does-not-exist"), [])

    def test_invalid_files_are_skipped(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            (base / "good.json").write_text(json.dumps(valid_company()), encoding="utf-8")
            (base / "bad_focus.json").write_text(
                json.dumps(valid_company(focus={"Docker": -1})), encoding="utf-8"
            )
            (base / "not_an_object.json").write_text(json.dumps(["acme"]), encoding="utf-8")
            (base / "broken.json").write_text("{not json", encoding="utf-8")
            profiles = load_company_profiles(str(base))
        self.assertEqual([p.id for p in profiles], ["acme"])


class TestCompanyData(unittest.TestCase):
    def test_role_profile_ids_reference_existing_profiles(self):
        known = {profile.id for profile in load_profiles()}
        for profile in load_company_profiles():
            for role_id in profile.roleProfileIds:
                self.assertIn(role_id, known, f"{profile.id} references unknown role {role_id}")

    def test_profiles_declare_no_question_content(self):
        content_fields = {"question", "shortAnswer", "explanation", "followUps"}
        for profile in load_company_profiles():
            self.assertFalse(content_fields & set(vars(profile)))


if __name__ == "__main__":
    unittest.main()