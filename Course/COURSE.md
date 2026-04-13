# Plano de estudos para a vaga de **Analista de Inteligência Artificial / Engenheiro(a) GenAI & ML Full Stack**

## Objetivo do plano

Este plano foi montado para formar alguém com **domínio operacional inicial** dos itens da vaga, não para formar um especialista acadêmico em cada tema.

O alvo é este:

* entender **o que é cada item da vaga**;
* conseguir **implementar versões simples e funcionais** em Python;
* saber **comparar alternativas** e justificar vantagens e desvantagens;
* chegar ao ponto de montar um **produto de IA de ponta a ponta** com ML, LLM, API, banco de dados, versionamento e deploy.

> Como você já domina Python, o plano parte desse ponto e transforma cada bloco em **estudo + prática em Python**.

---

## O que da vaga é “estudável” e o que não é

### Itens técnicos que entram no plano

* Git
* SQL
* Cloud (AWS, GCP ou Azure)
* LLMs de forma programática
* Frameworks de agentes
* NLP
* Machine Learning clássico
* Deep Learning
* FastAPI
* CI/CD e deployment
* Padrões de projeto
* RAG, vector databases e sistemas multi-agente
* Planejamento e análise de experimentos

### Itens que não são exatamente conteúdo de estudo

* Atuação presencial em São Paulo
* Formação superior completa
* Benefícios

Esses não entram no roteiro técnico.

---

## Princípio de ordem do plano

A ordem abaixo foi escolhida por dependência prática:

1. **Git** vem antes de tudo porque toda rotina profissional depende de versionamento.
2. **SQL** vem cedo porque IA aplicada em empresa depende de dados reais.
3. **Engenharia de software e padrões de projeto** vêm antes de APIs, agentes e deploy, porque sem isso o código vira protótipo desorganizado.
4. **Métricas, estatística e experimentação** vêm antes de ML e LLMs, porque você precisa saber comparar abordagens.
5. **ML clássico** vem antes de NLP avançado e LLMs, porque cria a base de modelagem e avaliação.
6. **NLP** vem antes de RAG e LLM apps, porque embeddings, chunking, recuperação e similaridade nascem daí.
7. **LLMs programáticos** vêm antes de agentes, porque agente sem entender tool calling, prompts e saídas estruturadas vira caixa-preta.
8. **RAG e vector DBs** vêm antes de multiagente, porque muitos produtos úteis já se resolvem com um pipeline determinístico bem feito.
9. **Agentes** vêm depois de LLM + RAG, para você aprender a usar agente quando faz sentido, e não por moda.
10. **FastAPI** entra quando já existe algo útil para servir.
11. **Cloud** entra depois do fluxo local, para você subir o que já funciona.
12. **CI/CD e deployment** entram depois que a aplicação já tem testes, estrutura e API.
13. **Deep Learning** entra como diferencial importante, mas não bloqueia a trilha principal de GenAI aplicada.
14. **Projeto final** consolida tudo.

---

## Ordem recomendada de estudo

| Ordem | Bloco                                         | Prioridade | Depende de            |
| ----- | --------------------------------------------- | ---------: | --------------------- |
| 1     | Git e rotina de desenvolvimento               |  Altíssima | —                     |
| 2     | SQL e acesso a dados                          |  Altíssima | —                     |
| 3     | Engenharia de software + padrões de projeto   |  Altíssima | Git                   |
| 4     | Estatística aplicada, métricas e experimentos |       Alta | SQL                   |
| 5     | Machine Learning clássico                     |  Altíssima | Estatística           |
| 6     | NLP                                           |  Altíssima | ML clássico           |
| 7     | LLMs programáticos                            |  Altíssima | NLP                   |
| 8     | RAG + vector databases                        |       Alta | LLMs + NLP            |
| 9     | Frameworks de agentes + multiagente           |       Alta | LLMs + RAG            |
| 10    | FastAPI                                       | Média/Alta | Eng. software         |
| 11    | Cloud (AWS/GCP/Azure)                         |       Alta | FastAPI + LLMs        |
| 12    | CI/CD + deployment                            | Média/Alta | FastAPI + Cloud + Git |
| 13    | Deep Learning (PyTorch/TensorFlow)            |      Média | ML + NLP              |
| 14    | Projeto integrador final                      |  Altíssima | Todos os anteriores   |

---

## Contexto prático único para o plano inteiro

Para evitar estudar tudo de forma solta, use **um único projeto-base** ao longo de toda a trilha.

### Tema sugerido

**Assistente interno de IA para operações/analytics de um banco fictício**

### Dados sintéticos que você vai criar em Python

* `clientes.csv`
* `contas.csv`
* `transacoes.csv`
* `tickets_atendimento.csv`
* `produtos_financeiros.csv`
* pasta `documentos/` com políticas, FAQs, manuais e regras internas em `.txt` ou `.md`

### Estrutura do repositório

```bash
ai-banking-lab/
├─ src/
├─ tests/
├─ notebooks/
├─ data/
├─ documents/
├─ api/
├─ prompts/
├─ evals/
├─ scripts/
├─ Dockerfile
├─ pyproject.toml
└─ README.md
```

A vantagem disso é que cada módulo reaproveita o anterior.

---

# Plano detalhado

## Módulo 1 — Git e rotina de desenvolvimento

### O que estudar

* `init`, `clone`, `add`, `commit`, `status`, `diff`, `log`
* branches
* merge e noção de rebase
* resolução de conflitos
* pull request
* tags e versionamento
* `.gitignore`
* boas mensagens de commit
* noção de fluxo com `main`, `dev` e branches de feature

### Por que vem primeiro

Porque toda entrega real de IA é feita em equipe, com histórico, revisão e rollback.

### Exercícios em Python

1. Criar o repositório do projeto-base e fazer commits pequenos:

   * geração de dados sintéticos;
   * primeiro notebook;
   * primeira função utilitária.
2. Abrir uma branch `feature/sql-ingestion` para criar scripts Python que carregam CSVs em SQLite.
3. Criar outra branch com alteração no mesmo arquivo e forçar um conflito de merge.
4. Criar uma tag `v0.1.0` após a primeira versão funcional do projeto.

### Saída esperada

Ao final, você deve conseguir trabalhar com um repositório Python sem medo de branch, merge e conflito.

---

## Módulo 2 — SQL e acesso a dados

### O que estudar

* `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`
* `JOIN`
* `GROUP BY`, `HAVING`
* `CASE WHEN`
* subqueries
* CTEs
* window functions
* modelagem relacional básica
* índices
* views
* noção de qualidade de dados

### Por que vem agora

A vaga pede domínio de SQL, e quase toda solução de IA corporativa depende de consultar, agregar e validar dados estruturados.

### Ferramentas em Python

* `sqlite3`
* `SQLAlchemy`
* `pandas.read_sql`
* opcional: `duckdb`

### Exercícios em Python

1. Gerar dados sintéticos e gravá-los em SQLite usando Python.
2. Escrever consultas para responder perguntas de negócio, por exemplo:

   * clientes com maior volume transacionado;
   * evolução mensal por produto;
   * tickets por categoria e severidade;
   * taxa de churn sintética por segmento.
3. Criar um script Python que execute queries e devolva DataFrames.
4. Criar views SQL para relatórios recorrentes.

### Saída esperada

Você deve conseguir pegar uma pergunta de negócio e transformá-la em consulta SQL correta, consumindo o resultado em Python.

---

## Módulo 3 — Engenharia de software para produtos de IA + padrões de projeto

### O que estudar

* organização de projeto Python
* ambientes virtuais
* empacotamento básico
* tipagem
* logging
* tratamento de erros
* configuração com `.env`
* testes unitários
* separação entre camada de domínio, serviço e infraestrutura
* padrões de projeto úteis para IA:

  * **Strategy**
  * **Adapter**
  * **Factory**
  * **Repository**
  * **Dependency Injection**
  * **Facade**

### Por que vem antes de FastAPI, agentes e cloud

Porque sem uma base de engenharia, o código de IA fica acoplado demais ao provedor, difícil de testar e difícil de trocar.

### Exercícios em Python

1. Criar uma interface `LLMClient` e adaptadores para dois provedores fictícios.
2. Criar uma `Factory` para escolher o provedor com base em variável de ambiente.
3. Criar um `Repository` para ler documentos e outro para ler dados SQL.
4. Escrever testes com `pytest` para cada camada.
5. Implementar logging estruturado para chamadas ao modelo.

### Saída esperada

Você deve ser capaz de explicar por que um código com `Adapter + Strategy` é melhor do que espalhar chamadas diretas ao provedor pelo projeto.

---

## Módulo 4 — Estatística aplicada, métricas e análise de experimentos

### O que estudar

* estatística descritiva
* média, mediana, desvio padrão, quantis
* amostragem
* viés e variância
* treino/validação/teste
* métricas para classificação e regressão
* intervalo de confiança
* hipótese nula
* testes A/B
* noção de significância prática vs. estatística
* comparação de prompts, modelos e pipelines
* noção de benchmark e avaliação offline

### Por que vem aqui

Porque o profissional da vaga precisa justificar vantagens e desvantagens de tecnologias e metodologias. Sem experimento, isso vira opinião.

### Ferramentas em Python

* `pandas`
* `numpy`
* `scipy`
* `statsmodels`
* `matplotlib`

### Exercícios em Python

1. Simular um experimento A/B de duas versões de resposta de um assistente.
2. Comparar duas versões de modelo de classificação com métricas e intervalo de confiança.
3. Criar um notebook que compare:

   * um prompt simples;
   * um prompt com contexto;
   * um pipeline com RAG.
4. Montar uma tabela de decisão com custo, latência, qualidade e complexidade.

### Saída esperada

Você deve conseguir dizer: “essa abordagem é melhor por este conjunto de métricas, com esta limitação”.

---

## Módulo 5 — Machine Learning clássico

### O que estudar

* problemas de regressão e classificação
* feature engineering
* pipelines
* normalização/padronização
* overfitting e underfitting
* cross-validation
* baseline
* regressão logística
* árvores de decisão
* random forest
* gradient boosting
* clustering
* PCA
* detecção de anomalias
* interpretação básica de modelos

### Por que vem antes de LLMs

Porque a vaga mistura GenAI com ML clássico. Você precisa saber quando um problema é resolvido melhor por um modelo tradicional do que por LLM.

### Ferramentas em Python

* `scikit-learn`
* `xgboost` ou `lightgbm` como extra

### Exercícios em Python

1. Criar um classificador para prever categoria de ticket.
2. Criar um modelo de propensão/churn sintético.
3. Fazer comparação entre baseline, regressão logística e árvore.
4. Criar um pipeline `scikit-learn` com pré-processamento + modelo.
5. Escrever um relatório curto dizendo por que o modelo escolhido venceu os demais.

### Saída esperada

Você deve saber responder: “esse problema é tabular, então vale começar com ML clássico antes de pensar em LLM”.

---

## Módulo 6 — NLP (Processamento de Linguagem Natural)

### O que estudar

* tokenização
* normalização
* stemming e lemmatization
* bag-of-words
* TF-IDF
* similaridade textual
* classificação de texto
* clustering textual
* NER
* embeddings
* busca semântica
* visão geral de transformers
* o que muda entre NLP clássico e NLP baseado em embeddings/transformers

### Por que vem antes de LLM, RAG e agentes

Porque RAG, busca vetorial, embeddings e boa parte da prática com LLMs dependem de fundamentos de NLP.

### Ferramentas em Python

* `nltk`
* `spaCy`
* `scikit-learn`
* `sentence-transformers`

### Exercícios em Python

1. Criar um classificador de texto com TF-IDF + regressão logística.
2. Extrair entidades de textos de atendimento usando `spaCy`.
3. Criar busca semântica entre tickets e documentos.
4. Medir similaridade entre perguntas frequentes para detectar duplicatas.
5. Comparar TF-IDF vs embeddings em uma tarefa de recuperação simples.

### Saída esperada

Você deve entender por que embeddings e transformers melhoram certas tarefas em relação ao NLP clássico.

---

## Módulo 7 — LLMs de forma programática

### O que estudar

* chamadas a APIs de modelos
* mensagens `system`, `user`, `assistant`
* prompt design
* structured output
* JSON schema / validação com Pydantic
* tool calling / function calling
* streaming
* retries
* rate limit
* custo por token
* latência
* segurança básica
* avaliação de saídas
* abstração entre provedores

### Provedores a estudar

* começar por **um provedor simples via API**;
* depois entender como os conceitos se mapeiam para:

  * **OpenAI**
  * **Anthropic**
  * **Vertex AI**
  * **Bedrock**

### Ordem interna correta

1. chamar o modelo;
2. controlar prompt e saída;
3. exigir JSON estruturado;
4. usar tools;
5. comparar provedores;
6. medir custo/latência/qualidade.

### Exercícios em Python

1. Criar um script que receba um texto e devolva um JSON estruturado com:

   * categoria;
   * urgência;
   * resumo;
   * ação recomendada.
2. Validar a saída com Pydantic.
3. Implementar fallback entre dois provedores.
4. Implementar tool calling para consultar SQL.
5. Registrar logs de latência, tokens e falhas.

### Saída esperada

Você deve conseguir construir um pequeno serviço Python orientado a LLM sem depender de framework de agente.

---

## Módulo 8 — RAG e vector databases

### O que estudar

* o que é RAG
* chunking
* embeddings
* indexação vetorial
* top-k retrieval
* filtros por metadata
* reranking
* grounded generation
* avaliação de retrieval
* alucinação e fontes
* diferenças entre FAISS, Chroma, Qdrant, pgvector, Weaviate

### Por que vem antes de agentes

Porque muitos problemas corporativos se resolvem melhor com um pipeline:
**recuperar contexto + chamar LLM**, sem precisar de agente autônomo.

### Ferramentas em Python

* `sentence-transformers`
* `faiss` ou `chromadb`
* `qdrant-client` ou `pgvector`
* SDK do provedor LLM escolhido

### Exercícios em Python

1. Indexar documentos internos do projeto em um vector store.
2. Criar um pipeline que:

   * recebe pergunta;
   * busca trechos relevantes;
   * chama o LLM com contexto;
   * devolve resposta com fontes.
3. Comparar duas estratégias de chunking.
4. Medir precisão de recuperação com um conjunto pequeno de perguntas-resposta.
5. Criar um script de reindexação.

### Saída esperada

Você deve saber montar um RAG funcional e explicar quando usar FAISS local e quando usar um banco vetorial gerenciado.

---

## Módulo 9 — Frameworks de agentes e sistemas multi-agente

### O que estudar

* diferença entre workflow e agente
* tool calling
* estado
* memória
* planejamento
* limites de iteração
* guardrails
* recuperação de falhas
* human-in-the-loop
* observabilidade de agentes
* quando **não** usar multiagente

### Ordem correta

1. primeiro fazer workflows determinísticos;
2. depois single-agent;
3. depois multi-agent.

### Framework recomendado para começar

* **LangGraph** primeiro, porque ajuda a entender fluxo, estado e transições.
* Depois comparar com **CrewAI** e outro framework de agentes.

### Exercícios em Python

1. Criar um agente com acesso a:

   * ferramenta SQL;
   * ferramenta RAG;
   * ferramenta de sumarização.
2. Criar um grafo simples com estados:

   * classificar pedido;
   * decidir ferramenta;
   * executar;
   * revisar resposta.
3. Criar uma versão multiagente com papéis:

   * pesquisador;
   * analista;
   * revisor.
4. Limitar número de passos e criar timeout.
5. Comparar o desempenho do agente com um workflow fixo.

### Saída esperada

Você deve saber dizer: “neste caso um fluxo fixo basta; neste outro, um agente agrega valor”.

---

## Módulo 10 — FastAPI para servir produtos de IA

### O que estudar

* fundamentos HTTP/REST
* rotas
* request/response models
* Pydantic
* validação
* injeção de dependência
* async básico
* tratamento de erro
* middleware
* autenticação básica
* documentação automática
* health check
* versionamento de API

### Por que entra aqui

Porque agora você já tem coisas úteis para publicar: um classificador, um RAG e um agente.

### Exercícios em Python

1. Criar uma API com rotas:

   * `POST /classify-ticket`
   * `POST /ask-docs`
   * `POST /agent-run`
   * `GET /health`
2. Separar camadas de API, serviço e infraestrutura.
3. Validar entrada e saída com Pydantic.
4. Retornar erros padronizados.
5. Criar testes da API.

### Saída esperada

Você deve conseguir transformar um experimento em um serviço consumível por outra aplicação.

---

## Módulo 11 — Cloud (AWS, GCP ou Azure)

### Estratégia recomendada

Escolha **um cloud principal** para estudar de verdade e só depois faça o mapeamento conceitual para os outros.

### Sugestão prática

* **AWS** como trilha principal, porque conecta bem com Bedrock.
* Depois mapear equivalentes em GCP e Azure.

### O que estudar

* IAM e permissões
* storage de objetos
* compute
* serverless
* containers
* secrets
* logs e monitoramento
* filas/eventos
* banco gerenciado
* noções de rede
* deploy de API
* serviços de IA gerenciada

### Mapeamento conceitual entre clouds

* armazenamento: **S3 / GCS / Blob Storage**
* funções: **Lambda / Cloud Functions / Azure Functions**
* identidade: **IAM / Service Accounts / Managed Identities**
* LLM gerenciado: **Bedrock / Vertex AI / Azure OpenAI**

### Exercícios em Python

1. Script Python para subir documentos para object storage.
2. Script para ler segredo de ambiente/secret manager.
3. Script para disparar uma inferência via serviço gerenciado.
4. Deploy de uma API simples em ambiente cloud.
5. Criar um pequeno batch job em Python para reprocessar embeddings.

### Saída esperada

Você deve entender como um sistema local vira um sistema executando em nuvem com segurança e observabilidade básica.

---

## Módulo 12 — CI/CD e deployment

### O que estudar

* lint
* formatter
* testes automatizados
* type checking
* build de imagem
* Docker
* pipeline de CI
* variáveis de ambiente
* promoção entre ambientes
* rollback básico
* deploy automatizado
* noção de infraestrutura como código como bônus

### Ferramentas em Python / ecossistema

* `pytest`
* `ruff`
* `mypy`
* `Docker`
* GitHub Actions ou GitLab CI

### Exercícios em Python

1. Dockerizar a API FastAPI.
2. Criar pipeline para:

   * instalar dependências;
   * rodar testes;
   * rodar lint;
   * validar tipagem;
   * construir imagem.
3. Adicionar workflow que roda a cada push na branch principal.
4. Criar script de smoke test em Python após deploy.

### Saída esperada

Você deve ser capaz de sair do “funciona na minha máquina” para “funciona de forma reproduzível”.

---

## Módulo 13 — Deep Learning (diferencial importante)

### O que estudar

* tensores
* autograd
* função de perda
* otimizadores
* training loop
* embeddings
* MLP
* noção de fine-tuning
* visão geral de transformers
* inferência com modelos pré-treinados

### Framework recomendado

* **PyTorch** primeiro
  Ele costuma ser a opção mais útil para quem quer transitar entre pesquisa aplicada e GenAI.

### O que não precisa aprofundar agora

* treinar LLM do zero
* treinamento distribuído
* otimizações de baixo nível
* arquitetura de transformer em profundidade matemática completa

### Exercícios em Python

1. Implementar um MLP simples em PyTorch para um problema tabular.
2. Implementar um classificador de texto simples.
3. Fazer inferência com um modelo pré-treinado para embeddings ou classificação.
4. Comparar uma solução `scikit-learn` com uma solução em PyTorch.

### Saída esperada

Você deve sair sabendo o suficiente para conversar com propriedade sobre DL e usar modelos pré-treinados sem depender só de API fechada.

---

# Projeto integrador final

## Objetivo

Montar um produto pequeno, mas completo, alinhado à vaga.

## Projeto sugerido

**Assistente corporativo de analytics e conhecimento interno**

### Funcionalidades

* recebe perguntas em linguagem natural;
* decide se responde com:

  * SQL,
  * RAG,
  * ou workflow orientado por agente;
* expõe tudo via FastAPI;
* registra logs;
* mede latência e qualidade;
* roda com CI/CD;
* pode ser implantado em cloud.

### Componentes mínimos

* Git
* SQL
* ML clássico em pelo menos uma tarefa
* NLP
* LLM com structured output
* RAG com fontes
* agente com pelo menos 2 ferramentas
* API FastAPI
* Docker
* pipeline CI
* documentação técnica curta com trade-offs

### Entregáveis

1. Repositório organizado.
2. README com arquitetura.
3. API rodando localmente.
4. Conjunto pequeno de testes.
5. Relatório de comparação entre:

   * resposta sem RAG;
   * resposta com RAG;
   * resposta com agente.
6. Documento curto justificando escolhas tecnológicas.

---

# Hábitos obrigatórios durante todo o plano

## 1. Sempre produzir evidência prática

Para cada bloco, entregue uma destas coisas:

* script Python;
* notebook;
* API;
* teste automatizado;
* relatório curto.

## 2. Sempre registrar trade-offs

Ao escolher tecnologia, escreva 5 linhas com:

* quando usar;
* quando não usar;
* custo;
* complexidade;
* limitação.

## 3. Sempre estudar com contexto de produto

Não pensar só em “rodar modelo”, mas em:

* entrada;
* validação;
* logs;
* erros;
* custo;
* deploy;
* manutenção.

## 4. Sempre comparar uma solução simples com uma solução mais sofisticada

Exemplo:

* SQL fixo vs agente SQL;
* TF-IDF vs embeddings;
* workflow fixo vs multiagente.

Esse hábito vale ouro para a parte da vaga que fala em justificar tecnologias e metodologias.

---

# O que não deve virar prioridade agora

Para o objetivo desta vaga, **não vale começar por aqui**:

* treinar LLM do zero;
* estudar matemática pesada de transformers antes de construir aplicações;
* Kubernetes avançado antes de saber servir uma API simples;
* multiagente complexo antes de dominar RAG;
* MLOps corporativo avançado antes de ter projeto local limpo;
* estudar três clouds a fundo ao mesmo tempo.

A melhor estratégia é:

* **aprofundar um stack principal**;
* entender como os conceitos se mapeiam para os demais.

---

# Checklist final da vaga, item por item

| Item da vaga                           | Onde estudar                       |
| -------------------------------------- | ---------------------------------- |
| Python                                 | já dominado; usado em todo o plano |
| Cloud (AWS, GCP ou Azure)              | Módulo 11                          |
| LLMs programáticos                     | Módulo 7                           |
| Frameworks de agentes                  | Módulo 9                           |
| SQL                                    | Módulo 2                           |
| NLP                                    | Módulo 6                           |
| Git                                    | Módulo 1                           |
| Deep Learning                          | Módulo 13                          |
| FastAPI                                | Módulo 10                          |
| Deployment e CI/CD                     | Módulo 12                          |
| Padrões de projeto                     | Módulo 3                           |
| RAG e vector databases                 | Módulo 8                           |
| Sistemas multi-agente                  | Módulo 9                           |
| Planejamento e análise de experimentos | Módulo 4                           |
| Escolha de tecnologias com trade-offs  | Módulos 3, 4, 11 e projeto final   |
| Construção de produto completo         | Módulos 10 a 14                    |

---

# Sequência final resumida

```text
Git
→ SQL
→ Engenharia de software + padrões
→ Estatística, métricas e experimentos
→ ML clássico
→ NLP
→ LLMs via API
→ RAG + vector databases
→ Agentes e multiagente
→ FastAPI
→ Cloud
→ CI/CD e deployment
→ Deep Learning
→ Projeto integrador final
```

---

# Conclusão

A trilha mais eficiente para essa vaga não é começar por “agentes” ou “LLMs” diretamente. O caminho mais sólido é:

1. organizar sua base de engenharia;
2. dominar dados e avaliação;
3. aprender ML e NLP;
4. construir aplicações com LLM;
5. evoluir para RAG e agentes;
6. transformar isso em produto com API, cloud e deploy.

Esse caminho te leva ao perfil que a vaga quer: alguém que não só usa IA, mas **constrói soluções reais, entende trade-offs e consegue colocar sistemas em produção**.

Posso transformar esse plano em uma versão **semana a semana**, com um cronograma progressivo e lista de projetos por etapa.
