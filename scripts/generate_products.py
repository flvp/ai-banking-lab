"""Generate the synthetic product catalog."""

from __future__ import annotations

from datetime import date

from scripts.config import DATE_RANGES, RunConfig
from scripts.id_factory import IdFactory
from scripts.io_utils import write_csv_rows
from scripts.random_utils import SeededRandom
from scripts.rules import choose_product_activity_date, clip_money, normalize_bool
from scripts.schema import PRODUCT_COLUMNS


PRODUCT_CATALOG = [
    ("conta_corrente", "conta_digital", "Conta Digital Essencial", "varejo", "baixo"),
    ("conta_corrente", "conta_premium", "Conta Premium Signature", "alta_renda", "baixo"),
    ("cartao_credito", "cartao_gold", "Cartao Gold Mais", "varejo", "medio"),
    ("cartao_credito", "cartao_black", "Cartao Black Infinite", "private", "medio"),
    ("investimento_renda_fixa", "cdb", "CDB Liquidez Diaria", "varejo", "baixo"),
    ("investimento_renda_fixa", "lci_lca", "LCI Safra Flex", "alta_renda", "baixo"),
    ("investimento_fundos", "fundo_multimercado", "Fundo Multi Estrategia", "alta_renda", "medio"),
    ("investimento_fundos", "fundo_rf", "Fundo Renda Fixa Horizonte", "varejo", "baixo"),
    ("previdencia", "previdencia_pgb", "Previdencia Futuro PGBL", "alta_renda", "medio"),
    ("previdencia", "previdencia_vgb", "Previdencia Futuro VGBL", "varejo", "medio"),
    ("credito_pessoal", "emprestimo_pf", "Credito Pessoal Flex", "varejo", "alto"),
    ("credito_empresarial", "capital_giro_pj", "Capital de Giro Pro", "empreendedor", "alto"),
    ("cambio", "cambio_digital", "Cambio Digital Global", "alta_renda", "medio"),
    ("seguros", "seguro_vida", "Seguro Vida Protecao", "varejo", "baixo"),
    ("seguros", "seguro_residencial", "Seguro Residencial Plus", "alta_renda", "baixo"),
    ("atendimento_premium", "gerente_dedicado", "Atendimento Signature", "private", "baixo"),
]


def generate_products(run_config: RunConfig, id_factory: IdFactory) -> list[dict[str, str]]:
    """Generate products and persist the resulting CSV file."""

    rng = SeededRandom(run_config.seed, "products")
    start = date.fromisoformat(DATE_RANGES["products_start"])
    end = date.fromisoformat(DATE_RANGES["products_end"])
    rows: list[dict[str, str]] = []
    index = 0
    while len(rows) < run_config.scale.products:
        categoria, subcategoria, base_name, publico, risco = PRODUCT_CATALOG[
            index % len(PRODUCT_CATALOG)
        ]
        suffix = index // len(PRODUCT_CATALOG) + 1
        name = base_name if suffix == 1 else f"{base_name} {suffix}"
        taxa = clip_money(rng.uniform(6.2, 22.5))
        tarifa = clip_money(0 if "premium" in subcategoria else rng.uniform(0, 69))
        saldo_minimo = clip_money(0 if publico == "varejo" else rng.uniform(100, 25_000))
        liquidez = 0 if "cdb" in subcategoria or "conta" in categoria else rng.randint(1, 30)
        permite_aplicacao = categoria.startswith("investimento") or categoria == "cambio"
        permite_resgate = categoria.startswith("investimento")
        ativo = rng.chance(0.82)
        launch_date = choose_product_activity_date(start, end, rng)
        rows.append(
            {
                "produto_id": id_factory.next_id("produtos"),
                "nome_produto": name,
                "categoria_produto": categoria,
                "subcategoria_produto": subcategoria,
                "publico_alvo": publico,
                "risco": risco,
                "taxa_base_anual": f"{taxa:.2f}",
                "tarifa_manutencao_mensal": f"{tarifa:.2f}",
                "saldo_minimo": f"{saldo_minimo:.2f}",
                "prazo_liquidez_dias": str(liquidez),
                "permite_aplicacao_digital": normalize_bool(permite_aplicacao),
                "permite_resgate_digital": normalize_bool(permite_resgate),
                "ativo": normalize_bool(ativo),
                "data_lancamento": launch_date.isoformat(),
                "descricao_curta": (
                    f"{name} com foco em {publico} e suporte ao segmento "
                    f"{categoria.replace('_', ' ')}."
                ),
            }
        )
        index += 1
    write_csv_rows(
        path=run_config.output_dir / "produtos_financeiros.csv",
        fieldnames=PRODUCT_COLUMNS,
        rows=rows,
    )
    return rows
