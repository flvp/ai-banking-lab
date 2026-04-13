"""Materialize customer-level analytical features from SQLite."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.features.build_features import build_features_rows, persist_features
from src.ingestao.sqlite_loader import connect_sqlite


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for feature generation."""

    parser = argparse.ArgumentParser(description="Generate customer features from SQLite.")
    parser.add_argument("--db-path", type=Path, default=Path("db/banco.db"))
    parser.add_argument("--output-csv", type=Path, default=Path("data/features_clientes.csv"))
    parser.add_argument("--reference-date", default="2026-03-31")
    return parser.parse_args()


def main() -> int:
    """Read the SQLite database and materialize the feature table."""

    args = parse_args()
    if not args.db_path.exists():
        print(f"SQLite database not found at {args.db_path}. Run scripts/carregar_sqlite.py first.")
        return 1
    conn = connect_sqlite(args.db_path)
    rows = build_features_rows(conn, args.reference_date)
    persist_features(conn, rows, args.output_csv)
    conn.close()
    print(f"Generated {len(rows)} feature rows at {args.output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
