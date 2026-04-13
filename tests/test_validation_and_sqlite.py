"""Tests for validation, SQLite loading and feature generation."""

from __future__ import annotations

import csv
import tempfile
import unittest
from collections import defaultdict
from pathlib import Path

from scripts.config import RunConfig, ScaleConfig
from scripts.generate_accounts import generate_accounts
from scripts.generate_clients import generate_clients
from scripts.generate_documents import generate_documents
from scripts.generate_products import generate_products
from scripts.generate_tickets import generate_tickets
from scripts.generate_transactions import generate_transactions
from scripts.id_factory import IdFactory
from scripts.seed_loader import load_seed_bundle
from src.features.build_features import build_features_rows, persist_features
from src.ingestao.sqlite_loader import load_all_into_sqlite
from src.ingestao.validation import build_validation_report


def build_small_dataset(output_dir: Path) -> None:
    """Generate a small canonical dataset into a temporary directory."""

    config = RunConfig(
        scale_name="test",
        scale=ScaleConfig(
            clients=100,
            accounts=140,
            transactions=500,
            tickets=160,
            products=16,
            documents=12,
        ),
        seed=42,
        chunk_size=50,
        output_dir=output_dir,
    )
    id_factory = IdFactory()
    seeds = load_seed_bundle()
    products = generate_products(config, id_factory)
    clients = generate_clients(config, id_factory, seeds)
    accounts = generate_accounts(config, id_factory, clients)
    clients_by_id = {row["cliente_id"]: row for row in clients}
    accounts_by_client: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in accounts:
        accounts_by_client[row["cliente_id"]].append(row)
    generate_transactions(config, id_factory, accounts, clients_by_id, products, seeds)
    generate_tickets(config, id_factory, clients, accounts_by_client, products, seeds)
    generate_documents(config, products, seeds)


class ValidationAndSQLiteTestCase(unittest.TestCase):
    """Validate the post-generation operational workflow."""

    def test_validation_load_and_features_workflow(self) -> None:
        """Canonical datasets should validate, load and materialize features."""

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)
            build_small_dataset(output_dir)
            report, _ = build_validation_report(
                data_dir=output_dir,
                documents_dir=output_dir / "documentos",
            )
            self.assertTrue(report.ok, msg=report.errors)
            db_path = output_dir / "banco.db"
            conn, summary = load_all_into_sqlite(db_path, data_dir=output_dir, drop_existing=True)
            self.assertEqual(summary["status"], "ok")
            feature_rows = build_features_rows(conn, "2026-03-31")
            persist_features(conn, feature_rows, output_dir / "features_clientes.csv")
            feature_count = conn.execute("SELECT COUNT(*) FROM features_clientes").fetchone()[0]
            client_count = conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
            self.assertEqual(feature_count, client_count)
            view_count = conn.execute("SELECT COUNT(*) FROM v_cliente_consolidado").fetchone()[0]
            self.assertEqual(view_count, client_count)
            conn.close()

    def test_schema_mismatch_blocks_validation_and_load(self) -> None:
        """Schema mismatches should fail preflight before SQLite ingestion."""

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)
            build_small_dataset(output_dir)
            transacoes_path = output_dir / "transacoes.csv"
            rows = transacoes_path.read_text(encoding="utf-8").splitlines()
            rows[0] = "id,conta_id,valor,tipo,descricao,data_transacao,referencia"
            transacoes_path.write_text("\n".join(rows) + "\n", encoding="utf-8")
            report, _ = build_validation_report(
                data_dir=output_dir,
                documents_dir=output_dir / "documentos",
            )
            self.assertFalse(report.ok)
            self.assertTrue(any("Schema mismatch" in item for item in report.errors))
            with self.assertRaises(ValueError):
                load_all_into_sqlite(output_dir / "broken.db", data_dir=output_dir, drop_existing=True)


if __name__ == "__main__":
    unittest.main()
