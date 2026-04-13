"""Validation helpers for CSV contracts, integrity rules and SQLite checks."""

from __future__ import annotations

import csv
import sqlite3
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Callable

from scripts.config import DATA_DIR, DOCUMENTS_DIR
from scripts.schema import SCHEMAS, get_schema


DATASET_FILES = {
    "produtos_financeiros": "produtos_financeiros.csv",
    "clientes": "clientes.csv",
    "contas": "contas.csv",
    "transacoes": "transacoes.csv",
    "tickets_atendimento": "tickets_atendimento.csv",
}

PRIMARY_KEYS = {
    "produtos_financeiros": "produto_id",
    "clientes": "cliente_id",
    "contas": "conta_id",
    "transacoes": "transacao_id",
    "tickets_atendimento": "ticket_id",
}

EXPECTED_NULLABLE = {
    "produtos_financeiros": set(),
    "clientes": set(),
    "contas": {"data_encerramento"},
    "transacoes": {"produto_relacionado_id"},
    "tickets_atendimento": {
        "conta_id",
        "data_fechamento",
        "produto_id",
        "tempo_resolucao_horas",
        "satisfacao_cliente",
    },
}

DATE_COLUMNS: dict[str, dict[str, Callable[[str], object]]] = {
    "produtos_financeiros": {"data_lancamento": date.fromisoformat},
    "clientes": {
        "data_nascimento": date.fromisoformat,
        "data_cadastro": date.fromisoformat,
    },
    "contas": {
        "data_abertura": date.fromisoformat,
        "data_encerramento": date.fromisoformat,
        "ultima_movimentacao_data": date.fromisoformat,
    },
    "transacoes": {"data_transacao": datetime.fromisoformat},
    "tickets_atendimento": {
        "data_abertura": datetime.fromisoformat,
        "data_fechamento": datetime.fromisoformat,
    },
}

REQUIRED_DOCUMENT_KEYWORDS = {
    "pix": ["pix"],
    "fraude": ["fraude"],
    "investimento": ["invest"],
    "cartao": ["cartao"],
    "acesso": ["acesso", "atendimento"],
}

NULL_RATE_COLUMN_LIMITS = {
    "clientes": {},
    "contas": {"data_encerramento": 0.90},
    "transacoes": {"produto_relacionado_id": 0.95},
    "tickets_atendimento": {
        "conta_id": 0.50,
        "data_fechamento": 0.40,
        "produto_id": 0.70,
        "tempo_resolucao_horas": 0.40,
        "satisfacao_cliente": 0.80,
    },
}


@dataclass
class ValidationReport:
    """Collect validation errors, warnings and summary metrics."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: dict[str, object] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        """Return whether the validation found no blocking errors."""

        return not self.errors

    def add_error(self, message: str) -> None:
        """Append one blocking validation message."""

        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        """Append one non-blocking validation message."""

        self.warnings.append(message)

    def to_dict(self) -> dict[str, object]:
        """Serialize the report into a JSON-friendly structure."""

        return {
            "status": "ok" if self.ok and not self.warnings else "warning" if self.ok else "error",
            "errors": self.errors,
            "warnings": self.warnings,
            "metrics": self.metrics,
        }


def _dataset_path(data_dir: Path, dataset_name: str) -> Path:
    """Resolve the canonical CSV path for one dataset."""

    return data_dir / DATASET_FILES[dataset_name]


def read_csv_header(path: Path) -> list[str]:
    """Read only the first header row from a CSV file."""

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        return next(reader)


def read_dataset_rows(path: Path) -> list[dict[str, str]]:
    """Load one dataset as a list of dictionary rows."""

    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_headers(data_dir: Path, report: ValidationReport) -> None:
    """Validate dataset headers against the canonical schema."""

    for dataset_name in SCHEMAS:
        path = _dataset_path(data_dir, dataset_name)
        if not path.exists():
            report.add_error(f"Missing dataset file: {path}")
            continue
        actual = read_csv_header(path)
        expected = get_schema(dataset_name)
        if actual != expected:
            report.add_error(
                f"Schema mismatch for {path.name}. Expected {expected}, received {actual}. "
                "Regenerate the dataset with scripts/build_all.py before loading into SQLite."
            )


def _validate_dates(dataset_name: str, row: dict[str, str], report: ValidationReport, row_number: int) -> None:
    """Validate date and datetime fields for one row."""

    for column, parser in DATE_COLUMNS[dataset_name].items():
        value = row.get(column, "")
        if not value:
            continue
        try:
            parser(value)
        except ValueError:
            report.add_error(
                f"Invalid date value in {dataset_name}.{column} at row {row_number}: {value}"
            )


def _null_rate(dataset_name: str, rows: list[dict[str, str]]) -> dict[str, float]:
    """Compute null rates per dataset based on empty strings."""

    if not rows:
        return {}
    counter = Counter()
    for row in rows:
        for column, value in row.items():
            if value == "":
                counter[column] += 1
    total = len(rows)
    return {column: count / total for column, count in counter.items()}


def validate_python_rules(data_dir: Path, report: ValidationReport) -> dict[str, list[dict[str, str]]]:
    """Run Python-side integrity checks across all datasets."""

    datasets = {
        dataset_name: read_dataset_rows(_dataset_path(data_dir, dataset_name))
        for dataset_name in SCHEMAS
        if _dataset_path(data_dir, dataset_name).exists()
    }
    if set(datasets) != set(SCHEMAS):
        return datasets

    key_sets: dict[str, set[str]] = {}
    for dataset_name, rows in datasets.items():
        primary_key = PRIMARY_KEYS[dataset_name]
        ids = [row[primary_key] for row in rows]
        if len(ids) != len(set(ids)):
            report.add_error(f"Duplicate primary key detected in {dataset_name}.{primary_key}.")
        key_sets[dataset_name] = set(ids)
        for row_number, row in enumerate(rows, start=2):
            _validate_dates(dataset_name, row, report, row_number)
        null_rates = _null_rate(dataset_name, rows)
        for column, rate in null_rates.items():
            if column not in EXPECTED_NULLABLE[dataset_name]:
                report.add_error(
                    f"Unexpected nulls found in {dataset_name}.{column}: {rate:.2%}."
                )
            elif rate > NULL_RATE_COLUMN_LIMITS.get(dataset_name, {}).get(column, 1):
                report.add_warning(
                    f"Null rate above threshold in {dataset_name}.{column}: {rate:.2%}."
                )
        report.metrics[f"{dataset_name}_rows"] = len(rows)

    clients = key_sets["clientes"]
    accounts = key_sets["contas"]
    products = key_sets["produtos_financeiros"]
    account_close_dates = {
        row["conta_id"]: row["data_encerramento"] for row in datasets["contas"]
    }

    for row in datasets["contas"]:
        if row["cliente_id"] not in clients:
            report.add_error(f"Account {row['conta_id']} references missing cliente_id {row['cliente_id']}.")
        if row["status_conta"] == "encerrada" and not row["data_encerramento"]:
            report.add_error(f"Account {row['conta_id']} is encerrada without data_encerramento.")
        if row["status_conta"] != "encerrada" and row["data_encerramento"]:
            report.add_error(f"Account {row['conta_id']} has unexpected data_encerramento.")

    for row in datasets["transacoes"]:
        if row["cliente_id"] not in clients:
            report.add_error(
                f"Transaction {row['transacao_id']} references missing cliente_id {row['cliente_id']}."
            )
        if row["conta_id"] not in accounts:
            report.add_error(
                f"Transaction {row['transacao_id']} references missing conta_id {row['conta_id']}."
            )
        if row["produto_relacionado_id"] and row["produto_relacionado_id"] not in products:
            report.add_error(
                "Transaction "
                f"{row['transacao_id']} references missing produto_id {row['produto_relacionado_id']}."
            )
        closing_date = account_close_dates.get(row["conta_id"], "")
        if closing_date and row["data_transacao"][:10] > closing_date:
            report.add_error(
                f"Transaction {row['transacao_id']} occurs after account closure for {row['conta_id']}."
            )

    for row in datasets["tickets_atendimento"]:
        if row["cliente_id"] not in clients:
            report.add_error(f"Ticket {row['ticket_id']} references missing cliente_id {row['cliente_id']}.")
        if row["conta_id"] and row["conta_id"] not in accounts:
            report.add_error(f"Ticket {row['ticket_id']} references missing conta_id {row['conta_id']}.")
        if row["produto_id"] and row["produto_id"] not in products:
            report.add_error(f"Ticket {row['ticket_id']} references missing produto_id {row['produto_id']}.")

    return datasets


def validate_documents(documents_dir: Path, report: ValidationReport) -> None:
    """Validate whether required document themes exist on disk."""

    stems = [path.stem.lower() for path in documents_dir.rglob("*") if path.is_file()]
    for topic, keywords in REQUIRED_DOCUMENT_KEYWORDS.items():
        if not any(any(keyword in stem for keyword in keywords) for stem in stems):
            report.add_warning(f"Documents for theme '{topic}' were not found in {documents_dir}.")


def validate_sqlite_rules(conn: sqlite3.Connection, report: ValidationReport) -> None:
    """Run SQL-side validation checks after the datasets are loaded."""

    queries = {
        "missing_account_clients": """
            SELECT COUNT(*) FROM contas c
            LEFT JOIN clientes cli ON cli.cliente_id = c.cliente_id
            WHERE cli.cliente_id IS NULL
        """,
        "missing_transaction_accounts": """
            SELECT COUNT(*) FROM transacoes t
            LEFT JOIN contas c ON c.conta_id = t.conta_id
            WHERE c.conta_id IS NULL
        """,
        "missing_ticket_clients": """
            SELECT COUNT(*) FROM tickets_atendimento t
            LEFT JOIN clientes c ON c.cliente_id = t.cliente_id
            WHERE c.cliente_id IS NULL
        """,
        "closed_account_transactions": """
            SELECT COUNT(*) FROM transacoes t
            JOIN contas c ON c.conta_id = t.conta_id
            WHERE c.data_encerramento IS NOT NULL
              AND substr(t.data_transacao, 1, 10) > c.data_encerramento
        """,
    }
    for name, query in queries.items():
        count = conn.execute(query).fetchone()[0]
        report.metrics[f"sqlite_{name}"] = count
        if count:
            report.add_error(f"SQLite validation failed for {name}: {count} offending rows.")


def build_validation_report(
    data_dir: Path = DATA_DIR,
    documents_dir: Path = DOCUMENTS_DIR,
) -> tuple[ValidationReport, dict[str, list[dict[str, str]]]]:
    """Build a full validation report without mutating repository data."""

    report = ValidationReport()
    validate_headers(data_dir, report)
    datasets = {}
    if report.ok:
        datasets = validate_python_rules(data_dir, report)
        validate_documents(documents_dir, report)
    return report, datasets
