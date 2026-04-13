"""Validate canonical CSV contracts and business rules before analytics."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from scripts.config import DATA_DIR, DOCUMENTS_DIR
from src.ingestao.sqlite_loader import create_schema, create_views, load_dataset
from src.ingestao.validation import build_validation_report, validate_sqlite_rules


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for data validation."""

    parser = argparse.ArgumentParser(description="Validate synthetic banking datasets.")
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--fail-on-warning", action="store_true")
    parser.add_argument("--output-report", type=Path, default=Path("reports/validation_summary.json"))
    return parser.parse_args()


def _print_report(report: dict[str, object]) -> None:
    """Print a concise validation summary to stdout."""

    print(f"Validation status: {report['status']}")
    for error in report["errors"]:
        print(f"ERROR: {error}")
    for warning in report["warnings"]:
        print(f"WARNING: {warning}")
    print("Metrics:")
    for key, value in sorted(report["metrics"].items()):
        print(f"  - {key}: {value}")


def main() -> int:
    """Run Python and SQLite validation and emit a JSON summary."""

    args = parse_args()
    report, _ = build_validation_report(
        data_dir=args.data_dir,
        documents_dir=args.data_dir / "documentos" if (args.data_dir / "documentos").exists() else DOCUMENTS_DIR,
    )
    if report.ok:
        conn = sqlite3.connect(":memory:")
        conn.execute("PRAGMA foreign_keys = ON")
        create_schema(conn, drop_existing=True)
        for dataset_name in ["produtos_financeiros", "clientes", "contas", "transacoes", "tickets_atendimento"]:
            load_dataset(conn, dataset_name, data_dir=args.data_dir)
        create_views(conn)
        validate_sqlite_rules(conn, report)
        conn.close()
    serialized = report.to_dict()
    args.output_report.parent.mkdir(parents=True, exist_ok=True)
    args.output_report.write_text(json.dumps(serialized, indent=2), encoding="utf-8")
    _print_report(serialized)
    if serialized["errors"]:
        return 1
    if args.fail_on_warning and serialized["warnings"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
