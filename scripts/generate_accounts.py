"""Generate accounts from the synthetic customer base."""

from __future__ import annotations

from datetime import date, timedelta

from scripts.config import RunConfig
from scripts.id_factory import IdFactory
from scripts.io_utils import write_csv_rows
from scripts.random_utils import SeededRandom
from scripts.rules import (
    assign_status_with_null,
    clip_money,
    determine_account_count,
    normalize_bool,
)
from scripts.schema import ACCOUNT_COLUMNS


ACCOUNT_TYPE_WEIGHTS = {
    "corrente": 0.45,
    "investimento": 0.25,
    "salario": 0.15,
    "premium": 0.10,
    "pj": 0.05,
}

PACKAGE_BY_TYPE = {
    "corrente": "basico",
    "investimento": "isento",
    "salario": "isento",
    "premium": "premium",
    "pj": "premium",
}


def _pick_account_type(segmento: str, rng: SeededRandom) -> str:
    """Choose one account type with segment-aware biases."""

    if segmento == "private":
        return rng.choices(["premium", "investimento", "corrente"], [0.45, 0.35, 0.20])
    if segmento == "empreendedor":
        return rng.choices(["pj", "corrente", "investimento"], [0.40, 0.40, 0.20])
    return rng.choices(
        list(ACCOUNT_TYPE_WEIGHTS),
        list(ACCOUNT_TYPE_WEIGHTS.values()),
    )


def generate_accounts(
    run_config: RunConfig,
    id_factory: IdFactory,
    clients: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Generate accounts and keep them linked to existing clients."""

    rng = SeededRandom(run_config.seed, "accounts")
    rows: list[dict[str, str]] = []
    account_targets = run_config.scale.accounts
    client_index = 0
    while len(rows) < account_targets:
        client = clients[client_index % len(clients)]
        client_index += 1
        planned_accounts = determine_account_count(client["segmento"], rng)
        for _ in range(planned_accounts):
            if len(rows) >= account_targets:
                break
            account_type = _pick_account_type(client["segmento"], rng)
            status = assign_status_with_null(
                rng,
                active_probability=0.88 if client["cliente_ativo"] == "true" else 0.35,
            )
            opening_date = date.fromisoformat(client["data_cadastro"]) + timedelta(
                days=rng.randint(0, 180)
            )
            closing_date = ""
            if status == "encerrada":
                closing_date = (
                    opening_date + timedelta(days=rng.randint(120, 900))
                ).isoformat()
            base_saldo = float(client["renda_mensal"]) * rng.uniform(0.4, 3.2)
            if account_type == "investimento":
                base_saldo *= rng.uniform(2.8, 7.0)
            if account_type in {"salario", "corrente"} and rng.chance(0.04):
                base_saldo *= -0.12
            rows.append(
                {
                    "conta_id": id_factory.next_id("contas"),
                    "cliente_id": client["cliente_id"],
                    "tipo_conta": account_type,
                    "status_conta": status,
                    "data_abertura": opening_date.isoformat(),
                    "data_encerramento": closing_date,
                    "agencia_codigo": f"{rng.randint(1, 9999):04d}",
                    "conta_numero": f"{rng.randint(100000, 999999)}-{rng.randint(0, 9)}",
                    "canal_abertura": rng.choice(["app", "gerente", "agencia", "parceiro"]),
                    "pacote_tarifario": PACKAGE_BY_TYPE[account_type],
                    "saldo_atual": f"{clip_money(base_saldo):.2f}",
                    "limite_credito": f"{clip_money(max(0, float(client['renda_mensal']) * rng.uniform(0.5, 2.5))):.2f}",
                    "possui_cartao": normalize_bool(account_type != "investimento"),
                    "possui_cheque_especial": normalize_bool(
                        account_type in {"corrente", "premium"} and rng.chance(0.55)
                    ),
                    "indicador_salario": normalize_bool(account_type == "salario"),
                    "indicador_investimento": normalize_bool(account_type == "investimento"),
                    "ultima_movimentacao_data": (
                        closing_date
                        if closing_date
                        else date(2026, rng.randint(1, 3), rng.randint(1, 28)).isoformat()
                    ),
                }
            )
    write_csv_rows(
        path=run_config.output_dir / "contas.csv",
        fieldnames=ACCOUNT_COLUMNS,
        rows=rows,
    )
    return rows
