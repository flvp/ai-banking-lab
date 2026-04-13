SELECT
    f.cliente_id,
    f.numero_escalonamentos,
    f.qtd_transacoes_30d,
    f.total_saida_30d,
    f.media_tempo_resolucao
FROM features_clientes f
ORDER BY
    f.numero_escalonamentos DESC,
    f.total_saida_30d DESC,
    f.media_tempo_resolucao DESC
LIMIT 20;
