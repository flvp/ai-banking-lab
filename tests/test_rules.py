"""Tests for synthetic data domain rules."""

from __future__ import annotations

import unittest
from datetime import date

from scripts.random_utils import SeededRandom
from scripts.rules import (
    calculate_age,
    compute_sla_hours,
    derive_relationship_score,
    infer_investor_profile,
    infer_segment,
)


class RulesTestCase(unittest.TestCase):
    """Validate deterministic rule helpers."""

    def test_calculate_age(self) -> None:
        """Age calculation should respect whether the birthday already happened."""

        age = calculate_age(date(1990, 10, 20), date(2026, 4, 1))
        self.assertEqual(age, 35)

    def test_segment_inference_biases_high_income_profiles(self) -> None:
        """High income customers should not fall into low-value segments often."""

        segment = infer_segment(60_000, 2_000_000, SeededRandom(42, "segment"))
        self.assertIn(segment, {"private", "alta_renda"})

    def test_investor_profile_for_seniors(self) -> None:
        """Older clients should be biased toward safer profiles."""

        profile = infer_investor_profile(68, "varejo", 350_000, SeededRandom(7, "profile"))
        self.assertIn(profile, {"conservador", "moderado"})

    def test_relationship_score_stays_in_bounds(self) -> None:
        """Relationship scores must remain inside the defined range."""

        score = derive_relationship_score("private", True, True, SeededRandom(10, "score"))
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_sla_is_shorter_for_private_clients(self) -> None:
        """Premium segments should receive shorter SLAs."""

        self.assertLess(compute_sla_hours("alta", "private"), compute_sla_hours("alta", "varejo"))


if __name__ == "__main__":
    unittest.main()
