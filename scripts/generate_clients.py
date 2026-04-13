"""Generate the synthetic client base from versioned name seeds."""

from __future__ import annotations

from datetime import date

from scripts.config import DATE_RANGES, RunConfig
from scripts.id_factory import IdFactory
from scripts.io_utils import write_csv_rows
from scripts.random_utils import SeededRandom
from scripts.rules import (
    calculate_age,
    clip_money,
    derive_relationship_score,
    infer_investor_profile,
    infer_segment,
    normalize_bool,
)
from scripts.schema import CLIENT_COLUMNS
from scripts.seed_loader import SeedBundle


STATE_CIVIL_OPTIONS = ["solteiro", "casado", "divorciado", "viuvo"]
ACQUISITION_CHANNELS = ["digital", "agencia", "indicacao", "parceria"]


def _pick_weighted_name(rows: list[dict[str, str]], key: str, rng: SeededRandom) -> str:
    """Choose one value from a weighted CSV seed."""

    values = [row[key] for row in rows]
    weights = [int(float(row["peso"])) for row in rows]
    return rng.choices(values, weights)


def generate_clients(
    run_config: RunConfig,
    id_factory: IdFactory,
    seeds: SeedBundle,
) -> list[dict[str, str]]:
    """Generate clients using combinatorial expansion from small seed sets."""

    rng = SeededRandom(run_config.seed, "clients")
    reference_date = date(2026, 4, 1)
    city_values = [(row["cidade"], row["uf"], int(float(row["peso"]))) for row in seeds.cities]
    rows: list[dict[str, str]] = []
    used_keys: set[tuple[str, str, str]] = set()
    while len(rows) < run_config.scale.clients:
        first_seed = rng.choice(seeds.first_names)
        sobrenome_1 = _pick_weighted_name(seeds.last_names, "sobrenome", rng)
        sobrenome_2 = _pick_weighted_name(seeds.last_names, "sobrenome", rng)
        nome_completo = f"{first_seed['nome']} {sobrenome_1}"
        if rng.chance(0.58):
            nome_completo = f"{nome_completo} {sobrenome_2}"
        city, uf, _ = rng.choices(city_values, [weight for _, _, weight in city_values])
        birth_year = rng.randint(1948, 2005)
        birth_month = rng.randint(1, 12)
        birth_day = rng.randint(1, 28)
        birth_date = date(birth_year, birth_month, birth_day)
        uniqueness = (nome_completo, birth_date.isoformat(), city)
        if uniqueness in used_keys:
            continue
        used_keys.add(uniqueness)
        profession = rng.choice(seeds.professions)
        renda_base = rng.uniform(2_300, 22_000) * float(profession["renda_multiplicador"])
        patrimonio = renda_base * rng.uniform(8, 42)
        segmento = infer_segment(renda_base, patrimonio, rng)
        if segmento == "private":
            renda_base *= rng.uniform(1.4, 2.4)
            patrimonio *= rng.uniform(1.8, 3.2)
        elif segmento == "alta_renda":
            renda_base *= rng.uniform(1.1, 1.5)
            patrimonio *= rng.uniform(1.1, 1.8)
        idade = calculate_age(birth_date, reference_date)
        possui_app = rng.chance(0.87 if idade < 60 else 0.63)
        ativo = rng.chance(0.90)
        canal = rng.choice(ACQUISITION_CHANNELS)
        perfil = infer_investor_profile(idade, segmento, patrimonio, rng)
        rows.append(
            {
                "cliente_id": id_factory.next_id("clientes"),
                "nome_completo": nome_completo,
                "sexo": first_seed["sexo"],
                "data_nascimento": birth_date.isoformat(),
                "idade": str(idade),
                "estado_civil": rng.choice(STATE_CIVIL_OPTIONS),
                "uf": uf,
                "cidade": city,
                "renda_mensal": f"{clip_money(renda_base):.2f}",
                "patrimonio_estimado": f"{clip_money(patrimonio):.2f}",
                "segmento": segmento,
                "escolaridade": profession["escolaridade_base"],
                "profissao": profession["profissao"],
                "score_relacionamento": str(
                    derive_relationship_score(segmento, possui_app, ativo, rng)
                ),
                "perfil_investidor": perfil,
                "data_cadastro": date(
                    rng.randint(2018, 2026),
                    rng.randint(1, 12),
                    rng.randint(1, 28),
                ).isoformat(),
                "canal_aquisicao": canal,
                "cliente_ativo": normalize_bool(ativo),
                "possui_app_ativo": normalize_bool(possui_app),
                "aceita_ofertas_marketing": normalize_bool(
                    ativo and possui_app and rng.chance(0.72)
                ),
            }
        )
    write_csv_rows(
        path=run_config.output_dir / "clientes.csv",
        fieldnames=CLIENT_COLUMNS,
        rows=rows,
    )
    return rows
