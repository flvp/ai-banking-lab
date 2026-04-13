# AI Banking Lab

Laboratório prático para estudar SQL, analytics, ML, NLP, RAG, agentes e FastAPI usando um banco fictício e uma base sintética coerente. O arquivo [COURSE.md](/Users/tripaulx/dev/AIA/ai-banking-lab/COURSE.md) continua sendo o plano macro da trilha; este `README.md` passa a ser o guia operacional do estado atual do repositório.

## Estado atual

- dataset sintético canônico gerado em `data/`
- validação automatizada com status `ok`
- SQLite carregado em `db/banco.db`
- features iniciais materializadas em `data/features_clientes.csv` e `features_clientes`
- notebooks iniciais de validação, EDA e SQL já disponíveis

## O que já foi implementado

### Geração de dados

O projeto já gera uma base bancária sintética completa com scripts Python em `scripts/`, incluindo:

- `clientes.csv`
- `contas.csv`
- `transacoes.csv`
- `tickets_atendimento.csv`
- `produtos_financeiros.csv`
- `data/documentos/` para uso posterior em RAG

Volumes atuais da base validada:

- `clientes.csv`: 5.000 linhas
- `contas.csv`: 7.000 linhas
- `transacoes.csv`: 250.000 linhas
- `tickets_atendimento.csv`: 18.000 linhas
- `produtos_financeiros.csv`: 50 linhas
- `features_clientes.csv`: 5.000 linhas

### Validação

A base é validada por contrato, integridade relacional e regras de negócio usando `scripts/validar_dados.py`.

Estado verificado atualmente:

- PKs e FKs consistentes
- nenhuma transação após encerramento de conta
- nenhuma referência órfã crítica detectada no SQLite
- relatório salvo em `reports/validation_summary.json`

### Ingestão SQLite

O projeto já carrega os CSVs canônicos em `db/banco.db` com:

- tabelas `clientes`, `contas`, `transacoes`, `tickets_atendimento`, `produtos_financeiros`
- índices analíticos
- views:
  - `v_cliente_consolidado`
  - `v_transacoes_mensais`
  - `v_tickets_analitico`

### Analytics SQL

Já existe uma base inicial para exploração analítica:

- notebooks `notebooks/01_validacao.ipynb`, `02_eda.ipynb`, `03_sql_analytics.ipynb`
- queries versionadas em `src/sql/queries/`
- consultas separadas por domínio:
  - cliente
  - conta
  - tickets
  - risco

### Feature engineering

O projeto já materializa uma tabela analítica por cliente com:

- total transacionado nos últimos 30 dias
- total de saída e ticket médio de saída
- contagem de PIX e investimentos
- quantidade de tickets e escalonamentos
- média de satisfação
- média de tempo de resolução
- proxy de uso digital

### Testes

A suíte atual cobre:

- geração do pipeline de dados
- schema e IDs
- regras de negócio
- templates textuais
- preflight de schema
- validação + carga SQLite
- materialização de `features_clientes`

## Estrutura atual do projeto

```text
ai-banking-lab/
├─ COURSE.md
├─ README.md
├─ data/
│  ├─ clientes.csv
│  ├─ contas.csv
│  ├─ transacoes.csv
│  ├─ tickets_atendimento.csv
│  ├─ produtos_financeiros.csv
│  ├─ features_clientes.csv
│  ├─ documentos/
│  └─ seeds/
├─ db/
│  └─ banco.db
├─ reports/
│  └─ validation_summary.json
├─ notebooks/
│  ├─ 01_validacao.ipynb
│  ├─ 02_eda.ipynb
│  └─ 03_sql_analytics.ipynb
├─ scripts/
│  ├─ build_all.py
│  ├─ validar_dados.py
│  ├─ carregar_sqlite.py
│  ├─ gerar_features.py
│  └─ geradores auxiliares
├─ src/
│  ├─ ingestao/
│  ├─ features/
│  └─ sql/queries/
└─ tests/
```

## Fluxo recomendado de uso

### 1. Regenerar os dados

```bash
python3 scripts/build_all.py --scale full --seed 42 --chunksize 10000
```

### 2. Validar a base

```bash
python3 scripts/validar_dados.py --data-dir data --output-report reports/validation_summary.json
```

### 3. Carregar tudo no SQLite

```bash
python3 scripts/carregar_sqlite.py --data-dir data --db-path db/banco.db --drop-existing
```

### 4. Gerar features por cliente

```bash
python3 scripts/gerar_features.py --db-path db/banco.db --output-csv data/features_clientes.csv --reference-date 2026-03-31
```

### 5. Explorar notebooks e queries

- abrir `notebooks/01_validacao.ipynb`
- abrir `notebooks/02_eda.ipynb`
- abrir `notebooks/03_sql_analytics.ipynb`
- consultar `src/sql/queries/`

## Papel de cada script principal

- `scripts/build_all.py`: gera ou regenera toda a base sintética canônica
- `scripts/validar_dados.py`: valida schema, integridade e regras de negócio antes do uso analítico
- `scripts/carregar_sqlite.py`: cria e popula `db/banco.db`
- `scripts/gerar_features.py`: materializa a tabela `features_clientes` no SQLite e em CSV

Observação importante: `data/documentos/` permanece no filesystem para a futura trilha de RAG. Ele não é carregado no SQLite.

## Próximos passos do curso

O projeto já saiu da fase de preparação. A sequência mais inteligente agora é usar a base pronta para consolidar a camada analítica e então avançar para ML, NLP e RAG.

### Próximo módulo recomendado agora

Foco principal neste momento:

- SQL + EDA + queries de negócio

Esse é o ponto mais maduro do projeto hoje, porque os dados já estão:

- gerados
- validados
- carregados no SQLite
- acompanhados por queries e features iniciais

### Sequência prática recomendada

1. consolidar SQL analítico em SQLite
2. expandir a EDA nos notebooks
3. aprofundar feature engineering em `src/features/`
4. iniciar ML clássico com targets já presentes no dataset
5. iniciar NLP com `tickets_atendimento.csv`
6. iniciar RAG com `data/documentos/`
7. combinar SQL + RAG em um agente
8. só depois expor isso via FastAPI

### Mapeamento dos próximos passos para o repositório

- SQL e analytics:
  - `notebooks/02_eda.ipynb`
  - `notebooks/03_sql_analytics.ipynb`
  - `src/sql/queries/`
- features:
  - `src/features/`
  - `data/features_clientes.csv`
- próximos módulos a criar:
  - `src/ml/`
  - `src/nlp/`
  - `src/rag/`
  - `src/api/`

## Ainda não implementado

As próximas etapas do curso ainda não foram construídas neste repositório:

- `notebooks/04_ml_classico.ipynb`
- `notebooks/05_nlp_tickets.ipynb`
- `notebooks/06_rag.ipynb`
- camada `src/ml/`
- camada `src/nlp/`
- camada `src/rag/`
- camada `src/api/`
- agente com ferramentas SQL + documentos
- FastAPI
- CI/CD
- cloud
- deploy

Esses blocos continuam alinhados aos módulos posteriores do [COURSE.md](/Users/tripaulx/dev/AIA/ai-banking-lab/COURSE.md), mas o repositório ainda não chegou nessa fase.

## Relação entre README e COURSE

- `COURSE.md`: trilha completa de formação, do Git até deploy
- `README.md`: estado real do laboratório, como usar o projeto hoje e o próximo bloco prático de estudo

O objetivo é não transformar o README em um changelog nem duplicar o curso inteiro. Ele deve responder quatro coisas:

1. o que este projeto é
2. o que já funciona
3. como usar agora
4. o que estudar a seguir
