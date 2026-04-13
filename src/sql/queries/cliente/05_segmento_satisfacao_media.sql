SELECT c.segmento, AVG(t.satisfacao_cliente) AS satisfacao_media
FROM tickets_atendimento t
JOIN clientes c ON c.cliente_id = t.cliente_id
WHERE t.satisfacao_cliente IS NOT NULL
GROUP BY c.segmento
ORDER BY satisfacao_media DESC;
