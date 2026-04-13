SELECT segmento, COUNT(*) AS total_clientes
FROM clientes
GROUP BY segmento
ORDER BY total_clientes DESC;
