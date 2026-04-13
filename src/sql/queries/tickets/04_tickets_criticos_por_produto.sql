SELECT produto_id, COUNT(*) AS tickets_criticos
FROM tickets_atendimento
WHERE prioridade = 'critica' AND produto_id IS NOT NULL
GROUP BY produto_id
ORDER BY tickets_criticos DESC;
