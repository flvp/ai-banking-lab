"""Tests for dataset schemas."""

from __future__ import annotations

import unittest

from scripts.schema import CLIENT_COLUMNS, get_schema, missing_required_columns


class SchemaTestCase(unittest.TestCase):
    """Validate column order and required field coverage."""

    def test_client_schema_starts_with_primary_identifier(self) -> None:
        """Client schema should expose the expected primary key first."""

        self.assertEqual(get_schema("clientes")[0], "cliente_id")
        self.assertEqual(get_schema("clientes"), CLIENT_COLUMNS)

    def test_required_columns_report_missing_fields(self) -> None:
        """Schema helpers should point out missing required columns."""

        missing = missing_required_columns("contas", ["conta_id", "cliente_id"])
        self.assertIn("status_conta", missing)


if __name__ == "__main__":
    unittest.main()
