SELECT cliente_id, nome_completo, total_tickets
FROM v_cliente_consolidado
ORDER BY total_tickets DESC, cliente_id
LIMIT 20;
