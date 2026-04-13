SELECT substr(data_transacao, 1, 7) AS ano_mes, SUM(valor) AS volume_total
FROM transacoes
GROUP BY substr(data_transacao, 1, 7)
ORDER BY ano_mes;
