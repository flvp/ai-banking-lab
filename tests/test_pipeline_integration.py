"""Integration tests for the end-to-end synthetic generation pipeline."""

from __future__ import annotations

import csv
import tempfile
import unittest
from collections import Counter, defaultdict
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


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a generated CSV file as a list of rows."""

    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class PipelineIntegrationTestCase(unittest.TestCase):
    """Validate referential integrity and quality rules on a small run."""

    def test_small_pipeline_generation(self) -> None:
        """A reduced run should still produce coherent linked datasets."""

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)
            config = RunConfig(
                scale_name="test",
                scale=ScaleConfig(
                    clients=120,
                    accounts=180,
                    transactions=700,
                    tickets=220,
                    products=18,
                    documents=12,
                ),
                seed=42,
                chunk_size=75,
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
            documents = generate_documents(config, products, seeds)

            products_rows = read_csv(output_dir / "produtos_financeiros.csv")
            client_rows = read_csv(output_dir / "clientes.csv")
            account_rows = read_csv(output_dir / "contas.csv")
            transaction_rows = read_csv(output_dir / "transacoes.csv")
            ticket_rows = read_csv(output_dir / "tickets_atendimento.csv")

            self.assertEqual(len(products_rows), 18)
            self.assertEqual(len(client_rows), 120)
            self.assertEqual(len(account_rows), 180)
            self.assertEqual(len(transaction_rows), 700)
            self.assertEqual(len(ticket_rows), 220)
            self.assertEqual(len(documents), 12)

            client_ids = {row["cliente_id"] for row in client_rows}
            account_ids = {row["conta_id"] for row in account_rows}
            product_ids = {row["produto_id"] for row in products_rows}
            self.assertEqual(len(client_ids), len(client_rows))
            self.assertEqual(len(account_ids), len(account_rows))

            for row in account_rows:
                self.assertIn(row["cliente_id"], client_ids)
                if row["status_conta"] == "encerrada":
                    self.assertTrue(row["data_encerramento"])
                else:
                    self.assertFalse(row["data_encerramento"])

            balances_by_account: dict[str, list[tuple[str, float]]] = defaultdict(list)
            for row in transaction_rows:
                self.assertIn(row["cliente_id"], client_ids)
                self.assertIn(row["conta_id"], account_ids)
                if row["produto_relacionado_id"]:
                    self.assertIn(row["produto_relacionado_id"], product_ids)
                balances_by_account[row["conta_id"]].append(
                    (row["data_transacao"], float(row["saldo_apos_transacao"]))
                )

            for values in balances_by_account.values():
                ordered_dates = [item[0] for item in values]
                self.assertEqual(ordered_dates, sorted(ordered_dates))

            valid_ticket_product_categories = {"cartao", "investimento"}
            category_counter = Counter()
            for row in ticket_rows:
                self.assertIn(row["cliente_id"], client_ids)
                if row["conta_id"]:
                    self.assertIn(row["conta_id"], account_ids)
                if row["produto_id"]:
                    self.assertIn(row["produto_id"], product_ids)
                    self.assertIn(row["categoria_ticket"], valid_ticket_product_categories)
                category_counter[row["categoria_ticket"]] += 1

            self.assertGreaterEqual(category_counter["fraude"], 5)
            self.assertGreaterEqual(category_counter["pix"], 10)


if __name__ == "__main__":
    unittest.main()
