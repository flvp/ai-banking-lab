"""Load versioned seeds used to expand the synthetic datasets."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from scripts.config import SEEDS_DIR
from scripts.io_utils import read_csv_rows, read_json_file


@dataclass(frozen=True)
class SeedBundle:
    """Represent the versioned seed content required by the generators."""

    first_names: list[dict[str, str]]
    last_names: list[dict[str, str]]
    cities: list[dict[str, str]]
    professions: list[dict[str, str]]
    company_names: list[dict[str, str]]
    merchant_names: list[dict[str, str]]
    ticket_templates: dict
    document_topics: dict


def _load_csv(seed_name: str, base_dir: Path = SEEDS_DIR) -> list[dict[str, str]]:
    """Load one CSV seed file by its base name."""

    return read_csv_rows(base_dir / f"{seed_name}.csv")


def _load_json(seed_name: str, base_dir: Path = SEEDS_DIR) -> dict:
    """Load one JSON seed file by its base name."""

    content = read_json_file(base_dir / f"{seed_name}.json")
    if not isinstance(content, dict):
        raise ValueError(f"Seed '{seed_name}.json' must contain a top-level object.")
    return content


def load_seed_bundle(base_dir: Path = SEEDS_DIR) -> SeedBundle:
    """Load the complete bundle of CSV and JSON seeds."""

    return SeedBundle(
        first_names=_load_csv("first_names", base_dir),
        last_names=_load_csv("last_names", base_dir),
        cities=_load_csv("cities", base_dir),
        professions=_load_csv("professions", base_dir),
        company_names=_load_csv("company_names", base_dir),
        merchant_names=_load_csv("merchant_names", base_dir),
        ticket_templates=_load_json("ticket_templates", base_dir),
        document_topics=_load_json("document_topics", base_dir),
    )
