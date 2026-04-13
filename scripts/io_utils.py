"""I/O helpers for writing deterministic CSV and text outputs."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Iterable, Sequence


def ensure_directory(path: Path) -> None:
    """Create a directory when it does not exist yet."""

    path.mkdir(parents=True, exist_ok=True)


def reset_file(path: Path) -> None:
    """Remove an output file if it already exists."""

    if path.exists():
        path.unlink()


def reset_directory(path: Path, keep_gitkeep: bool = True) -> None:
    """Delete files inside a directory while keeping the directory itself."""

    if not path.exists():
        return
    for child in path.iterdir():
        if keep_gitkeep and child.name == ".gitkeep":
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def write_csv_rows(
    path: Path,
    fieldnames: Sequence[str],
    rows: Iterable[dict],
    append: bool = False,
) -> None:
    """Write rows to CSV, optionally appending without duplicating headers."""

    ensure_directory(path.parent)
    mode = "a" if append and path.exists() else "w"
    write_header = mode == "w"
    with path.open(mode, encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read a CSV file into a list of dictionaries."""

    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json_file(path: Path) -> dict | list:
    """Load a JSON file and return its content."""

    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_text_file(path: Path, content: str) -> None:
    """Write text content using UTF-8 encoding."""

    ensure_directory(path.parent)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def parse_bool_text(value: str) -> int | None:
    """Convert canonical boolean text values into SQLite-friendly integers."""

    normalized = value.strip().lower()
    if normalized == "":
        return None
    if normalized == "true":
        return 1
    if normalized == "false":
        return 0
    raise ValueError(f"Unsupported boolean value '{value}'.")
