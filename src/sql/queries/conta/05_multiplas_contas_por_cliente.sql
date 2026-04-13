SELECT cliente_id, COUNT(*) AS total_contas
FROM contas
GROUP BY cliente_id
HAVING COUNT(*) > 1
ORDER BY total_contas DESC, cliente_id
LIMIT 20;
