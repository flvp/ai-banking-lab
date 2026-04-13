"""Utilities to generate readable synthetic identifiers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


PREFIXES = {
    "clientes": ("CLI", 6),
    "contas": ("CTA", 6),
    "transacoes": ("TRX", 8),
    "tickets": ("TCK", 6),
    "produtos": ("PRD", 4),
}


@dataclass
class IdFactory:
    """Generate deterministic sequential identifiers for each entity."""

    counters: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize the internal counters."""

        for entity in PREFIXES:
            self.counters.setdefault(entity, 0)

    def next_id(self, entity: str) -> str:
        """Return the next identifier for a given entity."""

        if entity not in PREFIXES:
            valid = ", ".join(sorted(PREFIXES))
            raise ValueError(f"Unknown entity '{entity}'. Valid values: {valid}.")
        prefix, width = PREFIXES[entity]
        self.counters[entity] += 1
        value = self.counters[entity]
        return f"{prefix}{value:0{width}d}"

    def snapshot(self) -> Dict[str, int]:
        """Return a copy of the current counter state."""

        return dict(self.counters)
