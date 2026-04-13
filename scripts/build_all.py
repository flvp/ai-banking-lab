"""CLI entrypoint that orchestrates full synthetic dataset generation."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from scripts.config import build_run_config
from scripts.generate_accounts import generate_accounts
from scripts.generate_clients import generate_clients
from scripts.generate_documents import generate_documents
from scripts.generate_products import generate_products
from scripts.generate_tickets import generate_tickets
from scripts.generate_transactions import generate_transactions
from scripts.id_factory import IdFactory
from scripts.seed_loader import load_seed_bundle


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the dataset build."""

    parser = argparse.ArgumentParser(description="Build the synthetic banking dataset.")
    parser.add_argument("--scale", default="intermediate", choices=["minimal", "intermediate", "full"])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--chunksize", type=int, default=10_000)
    return parser.parse_args()


def main() -> None:
    """Run the complete synthetic generation pipeline."""

    args = parse_args()
    run_config = build_run_config(
        scale_name=args.scale,
        seed=args.seed,
        chunk_size=args.chunksize,
        output_dir=args.output_dir,
    )
    id_factory = IdFactory()
    seeds = load_seed_bundle()
    products = generate_products(run_config, id_factory)
    clients = generate_clients(run_config, id_factory, seeds)
    accounts = generate_accounts(run_config, id_factory, clients)
    clients_by_id = {row["cliente_id"]: row for row in clients}
    accounts_by_client: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in accounts:
        accounts_by_client[row["cliente_id"]].append(row)
    generate_transactions(run_config, id_factory, accounts, clients_by_id, products, seeds)
    generate_tickets(run_config, id_factory, clients, accounts_by_client, products, seeds)
    generate_documents(run_config, products, seeds)


if __name__ == "__main__":
    main()
