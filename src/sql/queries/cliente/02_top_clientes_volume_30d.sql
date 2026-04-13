SELECT cliente_id, total_transacionado_30d
FROM features_clientes
ORDER BY total_transacionado_30d DESC
LIMIT 20;
