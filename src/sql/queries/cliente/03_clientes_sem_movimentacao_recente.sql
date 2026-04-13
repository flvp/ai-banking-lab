SELECT cliente_id, nome_completo, segmento
FROM v_cliente_consolidado
WHERE ultima_transacao IS NULL
   OR date(substr(ultima_transacao, 1, 10)) < date('2026-03-31', '-60 day')
ORDER BY segmento, nome_completo;
