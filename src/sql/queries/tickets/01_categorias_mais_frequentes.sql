SELECT categoria_ticket, COUNT(*) AS total_tickets
FROM tickets_atendimento
GROUP BY categoria_ticket
ORDER BY total_tickets DESC;
