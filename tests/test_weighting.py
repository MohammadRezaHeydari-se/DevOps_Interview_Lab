from __future__ import annotations

import unittest

from src.core.weighting import allocate_quota, combine_weights


class TestCombineWeights(unittest.TestCase):
    def test_without_company_returns_role_weights(self):
        weights = combine_weights({"Docker": 1.0, "Linux": 0.5})
        self.assertEqual(weights, {"Docker": 1.0, "Linux": 0.5})

    def test_company_focus_adjusts_role_weights(self):
        weights = combine_weights({"Docker": 1.0, "Linux": 1.0}, {"Docker": 1.0, "Linux": 0.5})
        self.assertEqual(weights, {"Docker": 1.0, "Linux": 0.5})

    def test_role_area_missing_from_company_keeps_role_weight(self):
        weights = combine_weights({"Docker": 1.0, "Linux": 0.8}, {"Docker": 0.5})
        self.assertEqual(weights, {"Docker": 0.5, "Linux": 0.8})

    def test_company_extra_area_never_replaces_role_areas(self):
        weights = combine_weights({"Docker": 1.0}, {"Docker": 1.0, "Kubernetes": 9.0})
        self.assertEqual(set(weights), {"Docker"})

    def test_casts_integer_weights_to_float(self):
        weights = combine_weights({"Docker": 1}, {"Docker": 2})
        self.assertEqual(weights, {"Docker": 2.0})
        self.assertIsInstance(weights["Docker"], float)


class TestAllocateQuota(unittest.TestCase):
    def test_sums_to_total(self):
        counts = allocate_quota({"A": 1.0, "B": 0.7, "C": 0.3}, 10)
        self.assertEqual(sum(counts.values()), 10)

    def test_largest_remainder_is_used(self):
        counts = allocate_quota({"A": 1.0, "B": 0.1}, 10)
        self.assertEqual(counts, {"A": 9, "B": 1})

    def test_ties_break_on_category_name(self):
        counts = allocate_quota({"B": 1.0, "A": 1.0}, 3)
        self.assertEqual(counts, {"A": 2, "B": 1})

    def test_is_deterministic_regardless_of_order(self):
        first = allocate_quota({"A": 1.0, "B": 1.0, "C": 1.0}, 5)
        second = allocate_quota({"C": 1.0, "B": 1.0, "A": 1.0}, 5)
        self.assertEqual(first, second)

    def test_non_positive_weights_are_ignored(self):
        counts = allocate_quota({"A": 1.0, "B": 0.0, "C": -2.0}, 4)
        self.assertEqual(counts, {"A": 4})

    def test_zero_or_negative_total_returns_empty(self):
        self.assertEqual(allocate_quota({"A": 1.0}, 0), {})
        self.assertEqual(allocate_quota({"A": 1.0}, -3), {})

    def test_no_positive_weights_returns_empty(self):
        self.assertEqual(allocate_quota({"A": 0.0}, 5), {})
        self.assertEqual(allocate_quota({}, 5), {})


if __name__ == "__main__":
    unittest.main()
