"""Randomness helpers with deterministic per-stage reproducibility."""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from typing import Sequence, TypeVar


T = TypeVar("T")


def stable_seed(base_seed: int, namespace: str) -> int:
    """Build a deterministic derived seed for a namespace."""

    payload = f"{base_seed}:{namespace}".encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    return int(digest[:16], 16)


@dataclass
class SeededRandom:
    """Expose deterministic random helpers scoped by namespace."""

    base_seed: int
    namespace: str

    def __post_init__(self) -> None:
        """Initialize the internal random generator."""

        self.seed = stable_seed(self.base_seed, self.namespace)
        self.random = random.Random(self.seed)

    def choice(self, values: Sequence[T]) -> T:
        """Choose one item from a non-empty sequence."""

        if not values:
            raise ValueError("Cannot choose from an empty sequence.")
        return self.random.choice(list(values))

    def choices(self, values: Sequence[T], weights: Sequence[float]) -> T:
        """Choose one item from a weighted sequence."""

        return self.random.choices(list(values), weights=list(weights), k=1)[0]

    def chance(self, probability: float) -> bool:
        """Return true according to the given probability."""

        return self.random.random() < probability

    def uniform(self, start: float, end: float) -> float:
        """Return a floating-point number inside a range."""

        return self.random.uniform(start, end)

    def randint(self, start: int, end: int) -> int:
        """Return an integer inside an inclusive range."""

        return self.random.randint(start, end)

    def sample(self, values: Sequence[T], count: int) -> list[T]:
        """Return a sample of unique items."""

        if count > len(values):
            raise ValueError("Sample size cannot exceed population size.")
        return self.random.sample(list(values), count)
