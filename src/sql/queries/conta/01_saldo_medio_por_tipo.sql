SELECT tipo_conta, AVG(saldo_atual) AS saldo_medio
FROM contas
GROUP BY tipo_conta
ORDER BY saldo_medio DESC;
