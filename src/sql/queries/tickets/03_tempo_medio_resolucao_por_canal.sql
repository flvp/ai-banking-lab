SELECT canal_atendimento, AVG(tempo_resolucao_horas) AS tempo_medio_resolucao
FROM tickets_atendimento
WHERE tempo_resolucao_horas IS NOT NULL
GROUP BY canal_atendimento
ORDER BY tempo_medio_resolucao DESC;
