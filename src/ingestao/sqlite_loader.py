"""SQLite loading helpers for the synthetic banking dataset."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

from scripts.config import DATA_DIR
from scripts.io_utils import ensure_directory, parse_bool_text
from src.ingestao.validation import DATASET_FILES, build_validation_report, validate_sqlite_rules


DDL = {
    "produtos_financeiros": """
        CREATE TABLE produtos_financeiros (
            produto_id TEXT PRIMARY KEY,
            nome_produto TEXT NOT NULL,
            categoria_produto TEXT NOT NULL,
            subcategoria_produto TEXT NOT NULL,
            publico_alvo TEXT NOT NULL,
            risco TEXT NOT NULL,
            taxa_base_anual REAL NOT NULL,
            tarifa_manutencao_mensal REAL NOT NULL,
            saldo_minimo REAL NOT NULL,
            prazo_liquidez_dias INTEGER NOT NULL,
            permite_aplicacao_digital INTEGER,
            permite_resgate_digital INTEGER,
            ativo INTEGER,
            data_lancamento TEXT NOT NULL,
            descricao_curta TEXT NOT NULL
        )
    """,
    "clientes": """
        CREATE TABLE clientes (
            cliente_id TEXT PRIMARY KEY,
            nome_completo TEXT NOT NULL,
            sexo TEXT NOT NULL,
            data_nascimento TEXT NOT NULL,
            idade INTEGER NOT NULL,
            estado_civil TEXT NOT NULL,
            uf TEXT NOT NULL,
            cidade TEXT NOT NULL,
            renda_mensal REAL NOT NULL,
            patrimonio_estimado REAL NOT NULL,
            segmento TEXT NOT NULL,
            escolaridade TEXT NOT NULL,
            profissao TEXT NOT NULL,
            score_relacionamento INTEGER NOT NULL,
            perfil_investidor TEXT NOT NULL,
            data_cadastro TEXT NOT NULL,
            canal_aquisicao TEXT NOT NULL,
            cliente_ativo INTEGER,
            possui_app_ativo INTEGER,
            aceita_ofertas_marketing INTEGER
        )
    """,
    "contas": """
        CREATE TABLE contas (
            conta_id TEXT PRIMARY KEY,
            cliente_id TEXT NOT NULL,
            tipo_conta TEXT NOT NULL,
            status_conta TEXT NOT NULL,
            data_abertura TEXT NOT NULL,
            data_encerramento TEXT,
            agencia_codigo TEXT NOT NULL,
            conta_numero TEXT NOT NULL,
            canal_abertura TEXT NOT NULL,
            pacote_tarifario TEXT NOT NULL,
            saldo_atual REAL NOT NULL,
            limite_credito REAL NOT NULL,
            possui_cartao INTEGER,
            possui_cheque_especial INTEGER,
            indicador_salario INTEGER,
            indicador_investimento INTEGER,
            ultima_movimentacao_data TEXT NOT NULL,
            FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)
        )
    """,
    "transacoes": """
        CREATE TABLE transacoes (
            transacao_id TEXT PRIMARY KEY,
            conta_id TEXT NOT NULL,
            cliente_id TEXT NOT NULL,
            data_transacao TEXT NOT NULL,
            tipo_transacao TEXT NOT NULL,
            categoria_transacao TEXT NOT NULL,
            valor REAL NOT NULL,
            sentido TEXT NOT NULL,
            saldo_apos_transacao REAL NOT NULL,
            canal_transacao TEXT NOT NULL,
            estabelecimento_origem TEXT NOT NULL,
            uf_origem TEXT NOT NULL,
            cidade_origem TEXT NOT NULL,
            transacao_suspeita_flag INTEGER,
            produto_relacionado_id TEXT,
            descricao_transacao TEXT NOT NULL,
            status_transacao TEXT NOT NULL,
            FOREIGN KEY (conta_id) REFERENCES contas(conta_id),
            FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id),
            FOREIGN KEY (produto_relacionado_id) REFERENCES produtos_financeiros(produto_id)
        )
    """,
    "tickets_atendimento": """
        CREATE TABLE tickets_atendimento (
            ticket_id TEXT PRIMARY KEY,
            cliente_id TEXT NOT NULL,
            conta_id TEXT,
            data_abertura TEXT NOT NULL,
            data_fechamento TEXT,
            canal_atendimento TEXT NOT NULL,
            categoria_ticket TEXT NOT NULL,
            subcategoria_ticket TEXT NOT NULL,
            prioridade TEXT NOT NULL,
            status_ticket TEXT NOT NULL,
            produto_id TEXT,
            sentimento_cliente TEXT NOT NULL,
            sla_horas INTEGER NOT NULL,
            tempo_resolucao_horas REAL,
            precisou_escalonamento INTEGER,
            resumo_ticket TEXT NOT NULL,
            descricao_ticket TEXT NOT NULL,
            resposta_final TEXT NOT NULL,
            resolvido_no_primeiro_contato INTEGER,
            satisfacao_cliente INTEGER,
            FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id),
            FOREIGN KEY (conta_id) REFERENCES contas(conta_id),
            FOREIGN KEY (produto_id) REFERENCES produtos_financeiros(produto_id)
        )
    """,
}

CREATE_INDEXES = [
    "CREATE INDEX idx_contas_cliente_id ON contas(cliente_id)",
    "CREATE INDEX idx_transacoes_conta_cliente_data ON transacoes(conta_id, cliente_id, data_transacao)",
    "CREATE INDEX idx_tickets_cliente_conta_produto_data ON tickets_atendimento(cliente_id, conta_id, produto_id, data_abertura)",
]

CREATE_VIEWS = [
    """
    CREATE VIEW v_cliente_consolidado AS
    SELECT
        c.cliente_id,
        c.nome_completo,
        c.segmento,
        c.renda_mensal,
        c.patrimonio_estimado,
        COUNT(DISTINCT co.conta_id) AS total_contas,
        COUNT(DISTINCT t.ticket_id) AS total_tickets,
        MAX(tr.data_transacao) AS ultima_transacao
    FROM clientes c
    LEFT JOIN contas co ON co.cliente_id = c.cliente_id
    LEFT JOIN tickets_atendimento t ON t.cliente_id = c.cliente_id
    LEFT JOIN transacoes tr ON tr.cliente_id = c.cliente_id
    GROUP BY c.cliente_id, c.nome_completo, c.segmento, c.renda_mensal, c.patrimonio_estimado
    """,
    """
    CREATE VIEW v_transacoes_mensais AS
    SELECT
        substr(data_transacao, 1, 7) AS ano_mes,
        cliente_id,
        conta_id,
        categoria_transacao,
        SUM(CASE WHEN sentido = 'entrada' THEN valor ELSE 0 END) AS total_entrada,
        SUM(CASE WHEN sentido = 'saida' THEN valor ELSE 0 END) AS total_saida,
        COUNT(*) AS quantidade_transacoes
    FROM transacoes
    GROUP BY substr(data_transacao, 1, 7), cliente_id, conta_id, categoria_transacao
    """,
    """
    CREATE VIEW v_tickets_analitico AS
    SELECT
        t.ticket_id,
        t.cliente_id,
        c.segmento,
        t.categoria_ticket,
        t.prioridade,
        t.status_ticket,
        t.canal_atendimento,
        t.produto_id,
        t.sentimento_cliente,
        t.sla_horas,
        t.tempo_resolucao_horas,
        t.precisou_escalonamento
    FROM tickets_atendimento t
    JOIN clientes c ON c.cliente_id = t.cliente_id
    """,
]


BOOLEAN_COLUMNS = {
    "produtos_financeiros": {"permite_aplicacao_digital", "permite_resgate_digital", "ativo"},
    "clientes": {"cliente_ativo", "possui_app_ativo", "aceita_ofertas_marketing"},
    "contas": {"possui_cartao", "possui_cheque_especial", "indicador_salario", "indicador_investimento"},
    "transacoes": {"transacao_suspeita_flag"},
    "tickets_atendimento": {"precisou_escalonamento", "resolvido_no_primeiro_contato"},
}


def _convert_value(dataset_name: str, column: str, value: str) -> object:
    """Convert one CSV cell into a SQLite-friendly Python value."""

    if value == "":
        return None
    if column in BOOLEAN_COLUMNS.get(dataset_name, set()):
        return parse_bool_text(value)
    if column.endswith("_horas") or column in {
        "renda_mensal",
        "patrimonio_estimado",
        "saldo_atual",
        "limite_credito",
        "valor",
        "saldo_apos_transacao",
        "taxa_base_anual",
        "tarifa_manutencao_mensal",
        "saldo_minimo",
    }:
        return float(value)
    if column in {"idade", "score_relacionamento", "prazo_liquidez_dias", "sla_horas", "satisfacao_cliente"}:
        return int(float(value))
    return value


def connect_sqlite(db_path: Path) -> sqlite3.Connection:
    """Open a SQLite connection with foreign keys enabled."""

    ensure_directory(db_path.parent)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_schema(conn: sqlite3.Connection, drop_existing: bool = False) -> None:
    """Create the canonical SQLite schema, indexes and views."""

    if drop_existing:
        for object_name in ["v_tickets_analitico", "v_transacoes_mensais", "v_cliente_consolidado"]:
            conn.execute(f"DROP VIEW IF EXISTS {object_name}")
        for table_name in reversed(list(DDL)):
            conn.execute(f"DROP TABLE IF EXISTS {table_name}")
    for ddl in DDL.values():
        conn.execute(ddl)
    for index in CREATE_INDEXES:
        conn.execute(index)


def load_dataset(conn: sqlite3.Connection, dataset_name: str, data_dir: Path = DATA_DIR) -> None:
    """Load one CSV dataset into its SQLite table."""

    file_path = data_dir / DATASET_FILES[dataset_name]
    with file_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames or []
        placeholders = ", ".join("?" for _ in columns)
        statement = f"INSERT INTO {dataset_name} ({', '.join(columns)}) VALUES ({placeholders})"
        rows = [
            tuple(_convert_value(dataset_name, column, row[column]) for column in columns)
            for row in reader
        ]
        conn.executemany(statement, rows)


def create_views(conn: sqlite3.Connection) -> None:
    """Create SQLite analytical views."""

    for view in CREATE_VIEWS:
        conn.execute(view)


def load_all_into_sqlite(
    db_path: Path,
    data_dir: Path = DATA_DIR,
    drop_existing: bool = False,
) -> tuple[sqlite3.Connection, dict[str, object]]:
    """Validate data, load it into SQLite and return a summary."""

    report, _ = build_validation_report(data_dir=data_dir, documents_dir=data_dir / "documentos")
    if not report.ok:
        raise ValueError("Dataset validation failed before SQLite load.")
    conn = connect_sqlite(db_path)
    create_schema(conn, drop_existing=drop_existing)
    for dataset_name in ["produtos_financeiros", "clientes", "contas", "transacoes", "tickets_atendimento"]:
        load_dataset(conn, dataset_name, data_dir=data_dir)
    create_views(conn)
    validate_sqlite_rules(conn, report)
    if not report.ok:
        conn.close()
        raise ValueError("SQLite validation failed after load.")
    conn.commit()
    return conn, report.to_dict()
