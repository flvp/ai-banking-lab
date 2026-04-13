SELECT tipo_conta, COUNT(*) AS contas_sem_cartao
FROM contas
WHERE possui_cartao = 0
GROUP BY tipo_conta
ORDER BY contas_sem_cartao DESC;
