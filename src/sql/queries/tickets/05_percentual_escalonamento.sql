SELECT
    ROUND(
        100.0 * SUM(CASE WHEN precisou_escalonamento = 1 THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS percentual_escalonamento
FROM tickets_atendimento;
