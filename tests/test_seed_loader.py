"""Tests for loading versioned generation seeds."""

from __future__ import annotations

import unittest

from scripts.seed_loader import load_seed_bundle


class SeedLoaderTestCase(unittest.TestCase):
    """Ensure seed files are readable and complete."""

    def test_loads_all_seed_groups(self) -> None:
        """The full seed bundle should contain all required collections."""

        bundle = load_seed_bundle()
        self.assertGreaterEqual(len(bundle.first_names), 20)
        self.assertGreaterEqual(len(bundle.last_names), 10)
        self.assertGreaterEqual(len(bundle.cities), 10)
        self.assertIn("acesso_app", bundle.ticket_templates)
        self.assertIn("politicas", bundle.document_topics)


if __name__ == "__main__":
    unittest.main()
