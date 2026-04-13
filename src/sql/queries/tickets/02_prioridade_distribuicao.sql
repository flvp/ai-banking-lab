SELECT prioridade, COUNT(*) AS total_tickets
FROM tickets_atendimento
GROUP BY prioridade
ORDER BY total_tickets DESC;
