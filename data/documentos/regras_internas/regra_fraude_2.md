# Regra Fraude

## Objetivo
Definir como a fila interna trata eventos de fraude ligados ao produto Cartao Black Infinite.

## Escopo
Aplica-se a times de risco, fraude e atendimento.

## Regras
- Casos criticos entram imediatamente em fila dedicada.
- Bloqueio preventivo pode ser aplicado antes da conclusao da triagem.
- Toda fraude exige rastreabilidade de evidencias.

## Excecoes
- Contingencias podem redistribuir o backlog.
- Clientes premium podem receber contato proativo.

## Procedimento
1. Classificar a severidade da suspeita.
2. Aplicar a fila e o protocolo corretos.
3. Acompanhar SLA ate o encerramento.

## Exemplos
- PIX suspeito com valor elevado.
- Conta acessada em padrao atipico.

## Observacoes
- Registrar toda mudanca de status no protocolo.
