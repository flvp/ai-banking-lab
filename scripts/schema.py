"""Dataset schemas and validation helpers."""

from __future__ import annotations

from typing import Dict, List


PRODUCT_COLUMNS = [
    "produto_id",
    "nome_produto",
    "categoria_produto",
    "subcategoria_produto",
    "publico_alvo",
    "risco",
    "taxa_base_anual",
    "tarifa_manutencao_mensal",
    "saldo_minimo",
    "prazo_liquidez_dias",
    "permite_aplicacao_digital",
    "permite_resgate_digital",
    "ativo",
    "data_lancamento",
    "descricao_curta",
]

CLIENT_COLUMNS = [
    "cliente_id",
    "nome_completo",
    "sexo",
    "data_nascimento",
    "idade",
    "estado_civil",
    "uf",
    "cidade",
    "renda_mensal",
    "patrimonio_estimado",
    "segmento",
    "escolaridade",
    "profissao",
    "score_relacionamento",
    "perfil_investidor",
    "data_cadastro",
    "canal_aquisicao",
    "cliente_ativo",
    "possui_app_ativo",
    "aceita_ofertas_marketing",
]

ACCOUNT_COLUMNS = [
    "conta_id",
    "cliente_id",
    "tipo_conta",
    "status_conta",
    "data_abertura",
    "data_encerramento",
    "agencia_codigo",
    "conta_numero",
    "canal_abertura",
    "pacote_tarifario",
    "saldo_atual",
    "limite_credito",
    "possui_cartao",
    "possui_cheque_especial",
    "indicador_salario",
    "indicador_investimento",
    "ultima_movimentacao_data",
]

TRANSACTION_COLUMNS = [
    "transacao_id",
    "conta_id",
    "cliente_id",
    "data_transacao",
    "tipo_transacao",
    "categoria_transacao",
    "valor",
    "sentido",
    "saldo_apos_transacao",
    "canal_transacao",
    "estabelecimento_origem",
    "uf_origem",
    "cidade_origem",
    "transacao_suspeita_flag",
    "produto_relacionado_id",
    "descricao_transacao",
    "status_transacao",
]

TICKET_COLUMNS = [
    "ticket_id",
    "cliente_id",
    "conta_id",
    "data_abertura",
    "data_fechamento",
    "canal_atendimento",
    "categoria_ticket",
    "subcategoria_ticket",
    "prioridade",
    "status_ticket",
    "produto_id",
    "sentimento_cliente",
    "sla_horas",
    "tempo_resolucao_horas",
    "precisou_escalonamento",
    "resumo_ticket",
    "descricao_ticket",
    "resposta_final",
    "resolvido_no_primeiro_contato",
    "satisfacao_cliente",
]

SCHEMAS: Dict[str, List[str]] = {
    "produtos_financeiros": PRODUCT_COLUMNS,
    "clientes": CLIENT_COLUMNS,
    "contas": ACCOUNT_COLUMNS,
    "transacoes": TRANSACTION_COLUMNS,
    "tickets_atendimento": TICKET_COLUMNS,
}

REQUIRED_COLUMNS = {
    "produtos_financeiros": {"produto_id", "nome_produto", "categoria_produto"},
    "clientes": {"cliente_id", "nome_completo", "segmento"},
    "contas": {"conta_id", "cliente_id", "tipo_conta", "status_conta"},
    "transacoes": {"transacao_id", "conta_id", "cliente_id", "tipo_transacao"},
    "tickets_atendimento": {"ticket_id", "cliente_id", "categoria_ticket"},
}


def get_schema(dataset_name: str) -> List[str]:
    """Return the ordered list of columns for a dataset."""

    try:
        return SCHEMAS[dataset_name]
    except KeyError as exc:
        valid = ", ".join(sorted(SCHEMAS))
        raise ValueError(f"Unknown dataset '{dataset_name}'. Valid values: {valid}.") from exc


def validate_columns(dataset_name: str, columns: List[str]) -> None:
    """Validate whether a list of columns matches the dataset contract."""

    expected = get_schema(dataset_name)
    if columns != expected:
        raise ValueError(
            f"Unexpected columns for '{dataset_name}'. "
            f"Expected {expected}, received {columns}."
        )


def missing_required_columns(dataset_name: str, columns: List[str]) -> List[str]:
    """Return missing required columns for a dataset."""

    missing = REQUIRED_COLUMNS[dataset_name] - set(columns)
    return sorted(missing)
