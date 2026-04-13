SELECT produto_id, COUNT(*) AS total_citacoes
FROM tickets_atendimento
WHERE produto_id IS NOT NULL
GROUP BY produto_id
ORDER BY total_citacoes DESC
LIMIT 20;
