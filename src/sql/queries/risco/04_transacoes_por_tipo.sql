SELECT tipo_transacao, COUNT(*) AS quantidade, AVG(valor) AS valor_medio
FROM transacoes
GROUP BY tipo_transacao
ORDER BY quantidade DESC;
