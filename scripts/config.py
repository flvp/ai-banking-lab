"""Configuration helpers for synthetic banking data generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
SEEDS_DIR = DATA_DIR / "seeds"
DOCUMENTS_DIR = DATA_DIR / "documentos"

DATE_RANGES = {
    "products_start": "2018-01-01",
    "products_end": "2026-02-28",
    "clients_start": "2018-01-01",
    "clients_end": "2026-03-15",
    "transactions_start": "2025-01-01",
    "transactions_end": "2026-03-31",
    "tickets_start": "2025-01-15T08:00:00",
    "tickets_end": "2026-03-31T20:00:00",
}

DEFAULT_SEED = 42
DEFAULT_CHUNK_SIZE = 10_000

SEGMENT_DISTRIBUTION = {
    "varejo": 0.60,
    "alta_renda": 0.25,
    "private": 0.10,
    "empreendedor": 0.05,
}

INVESTOR_PROFILE_DISTRIBUTION = {
    "conservador": 0.40,
    "moderado": 0.40,
    "arrojado": 0.20,
}

PRIORITY_DISTRIBUTION = {
    "baixa": 0.20,
    "media": 0.50,
    "alta": 0.25,
    "critica": 0.05,
}

TRANSACTION_TYPE_DISTRIBUTION = {
    "pix": 0.35,
    "compras": 0.20,
    "boletos": 0.15,
    "ted": 0.10,
    "investimentos": 0.10,
    "tarifas": 0.05,
    "outros": 0.05,
}

DOCUMENT_TYPE_COUNTS = {
    "politicas": 14,
    "faqs": 16,
    "manuais": 14,
    "regras_internas": 12,
}

NULL_RATE_LIMITS = {
    "clientes": 0.03,
    "contas": 0.06,
    "transacoes": 0.02,
    "tickets": 0.08,
}


@dataclass(frozen=True)
class ScaleConfig:
    """Represent the volume targets for one generation scale."""

    clients: int
    accounts: int
    transactions: int
    tickets: int
    products: int
    documents: int


@dataclass(frozen=True)
class RunConfig:
    """Hold runtime settings for one generator execution."""

    scale_name: str
    scale: ScaleConfig
    seed: int = DEFAULT_SEED
    chunk_size: int = DEFAULT_CHUNK_SIZE
    output_dir: Path = DATA_DIR

    @property
    def documents_dir(self) -> Path:
        """Return the output directory for generated documents."""

        return self.output_dir / "documentos"


SCALES: Dict[str, ScaleConfig] = {
    "minimal": ScaleConfig(
        clients=1_000,
        accounts=1_500,
        transactions=30_000,
        tickets=5_000,
        products=20,
        documents=20,
    ),
    "intermediate": ScaleConfig(
        clients=3_000,
        accounts=4_500,
        transactions=120_000,
        tickets=10_000,
        products=40,
        documents=40,
    ),
    "full": ScaleConfig(
        clients=5_000,
        accounts=7_000,
        transactions=250_000,
        tickets=18_000,
        products=50,
        documents=56,
    ),
}


def build_run_config(
    scale_name: str,
    seed: int = DEFAULT_SEED,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    output_dir: Path | None = None,
) -> RunConfig:
    """Create a validated runtime configuration."""

    if scale_name not in SCALES:
        valid = ", ".join(sorted(SCALES))
        raise ValueError(f"Unknown scale '{scale_name}'. Valid values: {valid}.")
    destination = output_dir or DATA_DIR
    return RunConfig(
        scale_name=scale_name,
        scale=SCALES[scale_name],
        seed=seed,
        chunk_size=chunk_size,
        output_dir=destination,
    )
