SELECT tipo_conta, AVG(limite_credito) AS limite_credito_medio
FROM contas
GROUP BY tipo_conta
ORDER BY limite_credito_medio DESC;
