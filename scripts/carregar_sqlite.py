"""Load canonical CSV datasets into SQLite with indexes and views."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from scripts.config import DATA_DIR
from src.ingestao.sqlite_loader import load_all_into_sqlite


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the SQLite loader."""

    parser = argparse.ArgumentParser(description="Load synthetic banking CSVs into SQLite.")
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--db-path", type=Path, default=Path("db/banco.db"))
    parser.add_argument("--drop-existing", action="store_true")
    return parser.parse_args()


def main() -> int:
    """Validate and load the canonical datasets into SQLite."""

    args = parse_args()
    if args.db_path.exists() and not args.drop_existing:
        print(
            f"Database already exists at {args.db_path}. "
            "Use --drop-existing to recreate it from the CSVs."
        )
        return 1
    conn, summary = load_all_into_sqlite(
        db_path=args.db_path,
        data_dir=args.data_dir,
        drop_existing=args.drop_existing,
    )
    conn.close()
    print(json.dumps(summary, indent=2))
    print(f"SQLite database created at {args.db_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
