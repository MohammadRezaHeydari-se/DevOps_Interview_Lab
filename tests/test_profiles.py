from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.core.loader import load_questions
from src.core.profile_loader import load_profiles
from src.core.profile_models import RoleProfile
from src.core.profile_validators import validate_profile

INITIAL_ROLES = {
    "DevOps Engineer",
    "Cloud / Azure",
    "IT Infrastructure",
    "IT Support",
    "Linux / System Administration",
}


def valid_profile(**overrides) -> dict:
    data = {
        "id": "devops-engineer",
        "role": "DevOps Engineer",
        "areas": {"Docker": 1.0, "Git / CI/CD": 0.8},
    }
    data.update(overrides)
    return data


class TestProfileValidation(unittest.TestCase):
    def test_accepts_valid_profile(self):
        ok, errors = validate_profile(valid_profile())
        self.assertTrue(ok)
        self.assertEqual(errors, [])

    def test_rejects_non_object(self):
        ok, errors = validate_profile(["not", "an", "object"])
        self.assertFalse(ok)
        self.assertTrue(errors)

    def test_rejects_missing_fields(self):
        ok, errors = validate_profile({"id": "x", "role": "X"})
        self.assertFalse(ok)
        self.assertEqual(errors, ["Missing field: areas"])

    def test_rejects_empty_profile(self):
        ok, errors = validate_profile({})
        self.assertFalse(ok)
        self.assertEqual(len(errors), 3)

    def test_rejects_empty_id_or_role(self):
        for field in ("id", "role"):
            ok, errors = validate_profile(valid_profile(**{field: "  "}))
            self.assertFalse(ok)
            self.assertTrue(errors)

    def test_rejects_empty_areas(self):
        ok, errors = validate_profile(valid_profile(areas={}))
        self.assertFalse(ok)
        self.assertTrue(any("areas" in error for error in errors))

    def test_rejects_non_object_areas(self):
        ok, errors = validate_profile(valid_profile(areas=["Docker"]))
        self.assertFalse(ok)
        self.assertTrue(any("areas" in error for error in errors))

    def test_rejects_non_positive_weight(self):
        for weight in (0, -0.5):
            ok, errors = validate_profile(valid_profile(areas={"Docker": weight}))
            self.assertFalse(ok)
            self.assertTrue(any("Docker" in error for error in errors))

    def test_rejects_non_numeric_weight(self):
        for weight in ("high", None, True):
            ok, errors = validate_profile(valid_profile(areas={"Docker": weight}))
            self.assertFalse(ok)
            self.assertTrue(errors)

    def test_accepts_integer_weight(self):
        ok, errors = validate_profile(valid_profile(areas={"Docker": 1}))
        self.assertTrue(ok)
        self.assertEqual(errors, [])


class TestProfileLoading(unittest.TestCase):
    def test_loads_initial_roles(self):
        profiles = load_profiles()
        self.assertGreaterEqual(len(profiles), len(INITIAL_ROLES))
        for profile in profiles:
            self.assertIsInstance(profile, RoleProfile)
        self.assertTrue(INITIAL_ROLES.issubset({p.role for p in profiles}))

    def test_profile_ids_are_unique(self):
        ids = [p.id for p in load_profiles()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_schema_file_is_not_loaded_as_a_profile(self):
        self.assertNotIn("schema", [p.id for p in load_profiles()])

    def test_weights_are_normalized_to_floats(self):
        for profile in load_profiles():
            for weight in profile.areas.values():
                self.assertIsInstance(weight, float)

    def test_missing_directory_returns_no_profiles(self):
        self.assertEqual(load_profiles("data/does-not-exist"), [])

    def test_invalid_files_are_skipped(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            (base / "good.json").write_text(json.dumps(valid_profile()), encoding="utf-8")
            (base / "bad_weight.json").write_text(
                json.dumps(valid_profile(areas={"Docker": 0})), encoding="utf-8"
            )
            (base / "not_an_object.json").write_text(json.dumps([1, 2]), encoding="utf-8")
            (base / "broken.json").write_text("{not json", encoding="utf-8")
            profiles = load_profiles(str(base))
        self.assertEqual([p.id for p in profiles], ["devops-engineer"])


class TestProfileData(unittest.TestCase):
    def test_areas_reference_existing_question_categories(self):
        categories = {q.category for q in load_questions()}
        for profile in load_profiles():
            for area in profile.areas:
                self.assertIn(area, categories, f"{profile.id} references unknown area {area}")

    def test_every_profile_defines_at_least_one_area(self):
        for profile in load_profiles():
            self.assertTrue(profile.areas)


if __name__ == "__main__":
    unittest.main()