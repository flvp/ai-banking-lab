"""Generate support tickets with structured text variation."""

from __future__ import annotations

from datetime import datetime, timedelta

from scripts.config import DATE_RANGES, RunConfig
from scripts.id_factory import IdFactory
from scripts.io_utils import write_csv_rows
from scripts.random_utils import SeededRandom
from scripts.rules import compute_sla_hours, determine_ticket_priority, normalize_bool, sample_datetime
from scripts.schema import TICKET_COLUMNS
from scripts.seed_loader import SeedBundle
from scripts.text_templates import (
    render_ticket_description,
    render_ticket_response,
    render_ticket_summary,
)


CATEGORY_TO_PRODUCT = {
    "acesso_app": None,
    "pix": None,
    "cartao": "cartao_credito",
    "investimento": "investimento_renda_fixa",
    "fraude": None,
}

STATUS_WEIGHTS = [0.08, 0.18, 0.68, 0.06]


def generate_tickets(
    run_config: RunConfig,
    id_factory: IdFactory,
    clients: list[dict[str, str]],
    accounts_by_client: dict[str, list[dict[str, str]]],
    products: list[dict[str, str]],
    seeds: SeedBundle,
) -> None:
    """Generate ticket rows and persist them to CSV in chunks."""

    rng = SeededRandom(run_config.seed, "tickets")
    start = datetime.fromisoformat(DATE_RANGES["tickets_start"])
    end = datetime.fromisoformat(DATE_RANGES["tickets_end"])
    output_path = run_config.output_dir / "tickets_atendimento.csv"
    chunk: list[dict[str, str]] = []
    product_by_category = {}
    for row in products:
        product_by_category.setdefault(row["categoria_produto"], []).append(row)
    categories = list(seeds.ticket_templates)
    generated = 0
    while generated < run_config.scale.tickets:
        client = rng.choice(clients)
        category = rng.choice(categories)
        sentiment = rng.choices(["negativo", "neutro", "positivo"], [0.55, 0.32, 0.13])
        priority = determine_ticket_priority(category, sentiment, client["segmento"], rng)
        sla_hours = compute_sla_hours(priority, client["segmento"])
        resolution_hours = round(rng.uniform(1, sla_hours * 1.6), 1)
        opened_at = sample_datetime(start, end, rng)
        status = rng.choices(
            ["aberto", "em_andamento", "resolvido", "cancelado"],
            STATUS_WEIGHTS,
        )
        if status in {"aberto", "em_andamento"}:
            closed_at = ""
            resolution_value = ""
        else:
            closed_at = (opened_at + timedelta(hours=resolution_hours)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            resolution_value = f"{resolution_hours:.1f}"
        account = ""
        if accounts_by_client.get(client["cliente_id"]) and rng.chance(0.75):
            account = rng.choice(accounts_by_client[client["cliente_id"]])["conta_id"]
        related_product = ""
        product_family = CATEGORY_TO_PRODUCT.get(category)
        if product_family:
            candidates = product_by_category.get(product_family, [])
            if candidates:
                related_product = rng.choice(candidates)["produto_id"]
        placeholders = {
            "valor_formatado": f"R$ {rng.uniform(85, 5200):.2f}",
            "periodo": rng.choice(["ontem", "hoje pela manha", "desde ontem a noite"]),
            "erro": rng.choice(
                ["falha de autenticacao", "acesso temporariamente indisponivel", "codigo invalido"]
            ),
            "evento": rng.choice(["uma atualizacao do aplicativo", "uma tentativa de login", "troca de aparelho"]),
            "prazo": str(sla_hours),
            "momento": opened_at.strftime("%d/%m/%Y %H:%M"),
            "status": rng.choice(["em analise", "concluido", "processando"]),
            "produto": related_product or "produto financeiro",
            "estabelecimento": rng.choice(seeds.merchant_names)["nome"],
        }
        first_contact = status == "resolvido" and rng.chance(0.58 if priority != "critica" else 0.22)
        satisfaction = ""
        if status == "resolvido" and rng.chance(0.72):
            score = rng.randint(4, 5) if first_contact else rng.randint(2, 4)
            satisfaction = str(score)
        chunk.append(
            {
                "ticket_id": id_factory.next_id("tickets"),
                "cliente_id": client["cliente_id"],
                "conta_id": account,
                "data_abertura": opened_at.strftime("%Y-%m-%d %H:%M:%S"),
                "data_fechamento": closed_at,
                "canal_atendimento": rng.choice(["chat", "email", "telefone", "app"]),
                "categoria_ticket": category,
                "subcategoria_ticket": f"{category}_{rng.choice(['geral', 'analise', 'suporte'])}",
                "prioridade": priority,
                "status_ticket": status,
                "produto_id": related_product,
                "sentimento_cliente": sentiment,
                "sla_horas": str(sla_hours),
                "tempo_resolucao_horas": resolution_value,
                "precisou_escalonamento": normalize_bool(
                    priority in {"alta", "critica"} or category == "fraude"
                ),
                "resumo_ticket": render_ticket_summary(
                    seeds.ticket_templates, category, placeholders, rng
                ),
                "descricao_ticket": render_ticket_description(
                    seeds.ticket_templates, category, placeholders, rng
                ),
                "resposta_final": render_ticket_response(
                    seeds.ticket_templates, category, placeholders, rng
                ),
                "resolvido_no_primeiro_contato": normalize_bool(first_contact),
                "satisfacao_cliente": satisfaction,
            }
        )
        generated += 1
        if len(chunk) >= run_config.chunk_size:
            write_csv_rows(
                path=output_path,
                fieldnames=TICKET_COLUMNS,
                rows=chunk,
                append=output_path.exists(),
            )
            chunk = []
    if chunk:
        write_csv_rows(
            path=output_path,
            fieldnames=TICKET_COLUMNS,
            rows=chunk,
            append=output_path.exists(),
        )
