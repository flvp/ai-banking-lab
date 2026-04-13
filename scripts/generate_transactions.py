"""Generate synthetic account transactions in deterministic chunks."""

from __future__ import annotations

from datetime import datetime, timedelta

from scripts.config import DATE_RANGES, RunConfig
from scripts.id_factory import IdFactory
from scripts.io_utils import write_csv_rows
from scripts.random_utils import SeededRandom
from scripts.rules import clip_money, normalize_bool, sample_datetime
from scripts.schema import TRANSACTION_COLUMNS
from scripts.seed_loader import SeedBundle


TRANSACTION_FAMILIES = {
    "pix": [("pix_recebido", "recebimento", "entrada"), ("pix_enviado", "transferencia", "saida")],
    "compras": [("compra_debito", "pagamento", "saida"), ("compra_credito", "pagamento", "saida")],
    "boletos": [("boleto_pago", "pagamento", "saida"), ("boleto_recebido", "recebimento", "entrada")],
    "ted": [("ted_recebida", "recebimento", "entrada"), ("ted_enviada", "transferencia", "saida")],
    "investimentos": [
        ("aplicacao_cdb", "investimento", "saida"),
        ("resgate_cdb", "investimento", "entrada"),
        ("aplicacao_fundo", "investimento", "saida"),
        ("resgate_fundo", "investimento", "entrada")
    ],
    "tarifas": [("tarifa_mensal", "tarifa", "saida"), ("pagamento_emprestimo", "credito", "saida")],
    "outros": [("saque", "saque", "saida"), ("deposito", "recebimento", "entrada")],
}

FAMILY_WEIGHTS = [0.35, 0.20, 0.15, 0.10, 0.10, 0.05, 0.05]


def generate_transactions(
    run_config: RunConfig,
    id_factory: IdFactory,
    accounts: list[dict[str, str]],
    clients_by_id: dict[str, dict[str, str]],
    products: list[dict[str, str]],
    seeds: SeedBundle,
) -> None:
    """Generate transactions and stream them to CSV in chunks."""

    rng = SeededRandom(run_config.seed, "transactions")
    start = datetime.fromisoformat(DATE_RANGES["transactions_start"] + "T08:00:00")
    end = datetime.fromisoformat(DATE_RANGES["transactions_end"] + "T20:00:00")
    output_path = run_config.output_dir / "transacoes.csv"
    chunk: list[dict[str, str]] = []
    product_ids = [row["produto_id"] for row in products if row["categoria_produto"].startswith("investimento")]
    merchant_rows = seeds.merchant_names
    account_balances = {row["conta_id"]: float(row["saldo_atual"]) for row in accounts}
    active_accounts = [row for row in accounts if row["status_conta"] != "bloqueada"]
    account_last_time = {
        row["conta_id"]: datetime.fromisoformat(row["data_abertura"] + "T09:00:00")
        for row in accounts
    }
    generated = 0
    while generated < run_config.scale.transactions:
        account = rng.choice(active_accounts)
        client = clients_by_id[account["cliente_id"]]
        family = rng.choices(list(TRANSACTION_FAMILIES), FAMILY_WEIGHTS)
        transaction_type, category, direction = rng.choice(TRANSACTION_FAMILIES[family])
        if account["tipo_conta"] == "investimento" and family not in {"investimentos", "pix"}:
            family = "investimentos" if rng.chance(0.60) else family
            transaction_type, category, direction = rng.choice(TRANSACTION_FAMILIES[family])
        last_time = max(account_last_time[account["conta_id"]], start)
        event_time = last_time + timedelta(minutes=rng.randint(5, 1_200))
        closing_date = account["data_encerramento"]
        account_end = end
        if closing_date:
            account_end = min(account_end, datetime.fromisoformat(closing_date + "T18:00:00"))
        if event_time > account_end:
            event_time = sample_datetime(last_time, account_end, rng) if last_time < account_end else account_end
        account_last_time[account["conta_id"]] = event_time
        merchant = rng.choice(merchant_rows)
        base_value = float(client["renda_mensal"]) * rng.uniform(0.03, 0.35)
        if family == "investimentos":
            base_value *= rng.uniform(1.2, 3.5)
        if family == "tarifas":
            base_value = rng.uniform(8, 420)
        amount = clip_money(base_value)
        current_balance = account_balances[account["conta_id"]]
        if direction == "entrada":
            updated_balance = clip_money(current_balance + amount)
        else:
            updated_balance = clip_money(current_balance - amount)
        account_balances[account["conta_id"]] = updated_balance
        is_suspicious = family in {"pix", "ted"} and amount > float(client["renda_mensal"]) * 1.2
        product_id = ""
        if family == "investimentos" and product_ids:
            product_id = rng.choice(product_ids)
        chunk.append(
            {
                "transacao_id": id_factory.next_id("transacoes"),
                "conta_id": account["conta_id"],
                "cliente_id": account["cliente_id"],
                "data_transacao": event_time.strftime("%Y-%m-%d %H:%M:%S"),
                "tipo_transacao": transaction_type,
                "categoria_transacao": category,
                "valor": f"{amount:.2f}",
                "sentido": direction,
                "saldo_apos_transacao": f"{updated_balance:.2f}",
                "canal_transacao": rng.choice(["app", "web", "agencia", "api"]),
                "estabelecimento_origem": merchant["nome"],
                "uf_origem": client["uf"],
                "cidade_origem": client["cidade"],
                "transacao_suspeita_flag": normalize_bool(is_suspicious and rng.chance(0.55)),
                "produto_relacionado_id": product_id,
                "descricao_transacao": (
                    f"{transaction_type.replace('_', ' ')} processada em {merchant['nome']}"
                ),
                "status_transacao": rng.choices(
                    ["concluida", "pendente", "estornada", "falha"],
                    [0.92, 0.03, 0.03, 0.02],
                ),
            }
        )
        generated += 1
        if len(chunk) >= run_config.chunk_size:
            write_csv_rows(
                path=output_path,
                fieldnames=TRANSACTION_COLUMNS,
                rows=chunk,
                append=output_path.exists(),
            )
            chunk = []
    if chunk:
        write_csv_rows(
            path=output_path,
            fieldnames=TRANSACTION_COLUMNS,
            rows=chunk,
            append=output_path.exists(),
        )
