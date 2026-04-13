SELECT conta_id, COUNT(*) AS total_suspeitas
FROM transacoes
WHERE transacao_suspeita_flag = 1
GROUP BY conta_id
ORDER BY total_suspeitas DESC
LIMIT 20;
