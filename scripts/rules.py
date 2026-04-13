"""Domain rules that keep the synthetic banking dataset coherent."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Iterable

from scripts.config import (
    INVESTOR_PROFILE_DISTRIBUTION,
    PRIORITY_DISTRIBUTION,
    SEGMENT_DISTRIBUTION,
)
from scripts.random_utils import SeededRandom


def normalize_bool(value: bool) -> str:
    """Serialize boolean values in a stable lowercase format."""

    return "true" if value else "false"


def weighted_choice(distribution: dict[str, float], rng: SeededRandom) -> str:
    """Choose one value from a simple weight map."""

    values = list(distribution)
    weights = [distribution[key] for key in values]
    return rng.choices(values, weights)


def calculate_age(birth_date: date, reference_date: date) -> int:
    """Compute age using a fixed reference date."""

    years = reference_date.year - birth_date.year
    before_birthday = (reference_date.month, reference_date.day) < (
        birth_date.month,
        birth_date.day,
    )
    return years - int(before_birthday)


def infer_segment(renda_mensal: float, patrimonio: float, rng: SeededRandom) -> str:
    """Infer the customer segment based on financial profile."""

    if patrimonio >= 1_500_000 or renda_mensal >= 50_000:
        return "private" if rng.chance(0.80) else "alta_renda"
    if patrimonio >= 350_000 or renda_mensal >= 15_000:
        return "alta_renda" if rng.chance(0.85) else "varejo"
    if renda_mensal <= 8_000 and rng.chance(0.08):
        return "empreendedor"
    return weighted_choice(SEGMENT_DISTRIBUTION, rng)


def infer_investor_profile(
    idade: int,
    segmento: str,
    patrimonio: float,
    rng: SeededRandom,
) -> str:
    """Infer the investor profile using age, segment and wealth."""

    if segmento == "private" and patrimonio > 1_000_000:
        return "arrojado" if rng.chance(0.45) else "moderado"
    if idade >= 60:
        return "conservador" if rng.chance(0.65) else "moderado"
    if idade <= 30 and patrimonio > 250_000:
        return "arrojado" if rng.chance(0.35) else "moderado"
    return weighted_choice(INVESTOR_PROFILE_DISTRIBUTION, rng)


def derive_relationship_score(
    segmento: str,
    possui_app: bool,
    ativo: bool,
    rng: SeededRandom,
) -> int:
    """Build a relationship score with simple deterministic biases."""

    base = 55
    if segmento == "alta_renda":
        base += 10
    if segmento == "private":
        base += 18
    if possui_app:
        base += 6
    if not ativo:
        base -= 18
    return max(0, min(100, base + rng.randint(-12, 12)))


def determine_account_count(segmento: str, rng: SeededRandom) -> int:
    """Return the number of accounts for one customer."""

    if segmento == "private":
        return rng.choices([2, 3, 4], [0.30, 0.45, 0.25])
    if segmento == "alta_renda":
        return rng.choices([1, 2, 3], [0.35, 0.45, 0.20])
    if segmento == "empreendedor":
        return rng.choices([1, 2, 3], [0.25, 0.50, 0.25])
    return rng.choices([1, 2], [0.70, 0.30])


def determine_ticket_priority(
    categoria: str,
    sentimento: str,
    segmento: str,
    rng: SeededRandom,
) -> str:
    """Determine ticket priority considering category and severity cues."""

    if categoria == "fraude":
        return rng.choices(["alta", "critica"], [0.65, 0.35])
    if categoria == "acesso_app" and sentimento == "negativo":
        return rng.choices(["media", "alta"], [0.35, 0.65])
    if segmento == "private" and rng.chance(0.25):
        return rng.choices(["media", "alta"], [0.40, 0.60])
    return weighted_choice(PRIORITY_DISTRIBUTION, rng)


def compute_sla_hours(prioridade: str, segmento: str) -> int:
    """Return the expected SLA for one ticket."""

    sla_map = {"baixa": 72, "media": 48, "alta": 24, "critica": 4}
    sla = sla_map[prioridade]
    if segmento == "private":
        return max(2, int(sla * 0.75))
    if segmento == "alta_renda":
        return max(4, int(sla * 0.85))
    return sla


def choose_product_activity_date(start: date, end: date, rng: SeededRandom) -> date:
    """Return a random date between two boundaries."""

    delta_days = (end - start).days
    return start + timedelta(days=rng.randint(0, delta_days))


def clip_money(value: float) -> float:
    """Round money values to two decimal places."""

    return round(value, 2)


def assign_status_with_null(
    rng: SeededRandom,
    active_probability: float = 0.85,
    blocked_probability: float = 0.03,
) -> str:
    """Return an account status keeping blocked accounts rare."""

    if rng.chance(blocked_probability):
        return "bloqueada"
    if rng.chance(active_probability):
        return "ativa"
    return "encerrada"


def sample_datetime(
    start: datetime,
    end: datetime,
    rng: SeededRandom,
) -> datetime:
    """Return a random datetime between two boundaries."""

    seconds = int((end - start).total_seconds())
    return start + timedelta(seconds=rng.randint(0, seconds))


def rolling_average(values: Iterable[float]) -> float:
    """Return the arithmetic mean for a non-empty iterable."""

    values = list(values)
    if not values:
        return 0.0
    return sum(values) / len(values)
