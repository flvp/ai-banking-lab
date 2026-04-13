"""Build reusable customer-level features from SQLite tables."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

from scripts.io_utils import ensure_directory


FEATURE_QUERY = """
WITH trans_30d AS (
    SELECT
        cliente_id,
        SUM(valor) AS total_transacionado_30d,
        SUM(CASE WHEN sentido = 'saida' THEN valor ELSE 0 END) AS total_saida_30d,
        AVG(CASE WHEN sentido = 'saida' THEN valor END) AS ticket_medio_saida_30d,
        SUM(CASE WHEN tipo_transacao LIKE 'pix%%' THEN 1 ELSE 0 END) AS qtd_pix_30d,
        SUM(CASE WHEN categoria_transacao = 'investimento' THEN 1 ELSE 0 END) AS qtd_investimentos_30d,
        COUNT(*) AS qtd_transacoes_30d,
        MAX(data_transacao) AS ultima_transacao
    FROM transacoes
    WHERE date(substr(data_transacao, 1, 10)) >= date(?, '-30 day')
    GROUP BY cliente_id
),
tickets_agg AS (
    SELECT
        cliente_id,
        COUNT(*) AS numero_tickets,
        SUM(CASE WHEN precisou_escalonamento = 1 THEN 1 ELSE 0 END) AS numero_escalonamentos,
        AVG(satisfacao_cliente) AS media_satisfacao,
        AVG(tempo_resolucao_horas) AS media_tempo_resolucao
    FROM tickets_atendimento
    GROUP BY cliente_id
),
channels AS (
    SELECT
        cliente_id,
        AVG(CASE WHEN canal_atendimento IN ('chat', 'app') THEN 1.0 ELSE 0.0 END) AS proxy_uso_digital
    FROM tickets_atendimento
    GROUP BY cliente_id
)
SELECT
    c.cliente_id,
    ? AS data_referencia,
    c.segmento,
    c.perfil_investidor,
    c.possui_app_ativo,
    COALESCE(t.total_transacionado_30d, 0) AS total_transacionado_30d,
    COALESCE(t.total_saida_30d, 0) AS total_saida_30d,
    COALESCE(t.ticket_medio_saida_30d, 0) AS ticket_medio_saida_30d,
    COALESCE(t.qtd_pix_30d, 0) AS qtd_pix_30d,
    COALESCE(t.qtd_investimentos_30d, 0) AS qtd_investimentos_30d,
    COALESCE(t.qtd_transacoes_30d, 0) AS qtd_transacoes_30d,
    CASE
        WHEN t.ultima_transacao IS NULL THEN NULL
        ELSE CAST(julianday(?) - julianday(date(substr(t.ultima_transacao, 1, 10))) AS INTEGER)
    END AS dias_desde_ultima_movimentacao,
    COALESCE(k.numero_tickets, 0) AS numero_tickets,
    COALESCE(k.numero_escalonamentos, 0) AS numero_escalonamentos,
    COALESCE(k.media_satisfacao, 0) AS media_satisfacao,
    COALESCE(k.media_tempo_resolucao, 0) AS media_tempo_resolucao,
    COALESCE(ch.proxy_uso_digital, CASE WHEN c.possui_app_ativo = 1 THEN 1.0 ELSE 0.0 END) AS proxy_uso_digital
FROM clientes c
LEFT JOIN trans_30d t ON t.cliente_id = c.cliente_id
LEFT JOIN tickets_agg k ON k.cliente_id = c.cliente_id
LEFT JOIN channels ch ON ch.cliente_id = c.cliente_id
ORDER BY c.cliente_id
"""


FEATURE_COLUMNS = [
    "cliente_id",
    "data_referencia",
    "segmento",
    "perfil_investidor",
    "possui_app_ativo",
    "total_transacionado_30d",
    "total_saida_30d",
    "ticket_medio_saida_30d",
    "qtd_pix_30d",
    "qtd_investimentos_30d",
    "qtd_transacoes_30d",
    "dias_desde_ultima_movimentacao",
    "numero_tickets",
    "numero_escalonamentos",
    "media_satisfacao",
    "media_tempo_resolucao",
    "proxy_uso_digital",
]


def build_features_rows(
    conn: sqlite3.Connection,
    reference_date: str,
) -> list[dict[str, object]]:
    """Query customer-level analytical features from SQLite."""

    cursor = conn.execute(FEATURE_QUERY, (reference_date, reference_date, reference_date))
    rows = cursor.fetchall()
    return [dict(zip(FEATURE_COLUMNS, row)) for row in rows]


def persist_features(
    conn: sqlite3.Connection,
    rows: list[dict[str, object]],
    output_csv: Path,
) -> None:
    """Persist features both to SQLite and to a CSV file."""

    ensure_directory(output_csv.parent)
    conn.execute("DROP TABLE IF EXISTS features_clientes")
    columns_sql = ", ".join(
        f"{column} TEXT" if column in {"cliente_id", "data_referencia", "segmento", "perfil_investidor"} else f"{column} REAL"
        for column in FEATURE_COLUMNS
    )
    conn.execute(f"CREATE TABLE features_clientes ({columns_sql}, PRIMARY KEY (cliente_id))")
    insert_sql = (
        f"INSERT INTO features_clientes ({', '.join(FEATURE_COLUMNS)}) "
        f"VALUES ({', '.join('?' for _ in FEATURE_COLUMNS)})"
    )
    conn.executemany(insert_sql, [tuple(row[column] for column in FEATURE_COLUMNS) for row in rows])
    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FEATURE_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    conn.commit()
