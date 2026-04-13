"""Tests for the readable synthetic identifier factory."""

from __future__ import annotations

import unittest

from scripts.id_factory import IdFactory


class IdFactoryTestCase(unittest.TestCase):
    """Validate sequential readable identifiers."""

    def test_generates_expected_prefixes_and_widths(self) -> None:
        """Each entity type should follow the declared prefix pattern."""

        factory = IdFactory()
        self.assertEqual(factory.next_id("clientes"), "CLI000001")
        self.assertEqual(factory.next_id("contas"), "CTA000001")
        self.assertEqual(factory.next_id("transacoes"), "TRX00000001")
        self.assertEqual(factory.next_id("tickets"), "TCK000001")
        self.assertEqual(factory.next_id("produtos"), "PRD0001")

    def test_snapshot_keeps_current_state(self) -> None:
        """The snapshot should expose the current counters safely."""

        factory = IdFactory()
        _ = factory.next_id("clientes")
        snapshot = factory.snapshot()
        self.assertEqual(snapshot["clientes"], 1)
        self.assertEqual(snapshot["contas"], 0)


if __name__ == "__main__":
    unittest.main()
