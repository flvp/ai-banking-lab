SELECT c.segmento, COUNT(*) AS contas_encerradas
FROM contas co
JOIN clientes c ON c.cliente_id = co.cliente_id
WHERE co.status_conta = 'encerrada'
GROUP BY c.segmento
ORDER BY contas_encerradas DESC;
