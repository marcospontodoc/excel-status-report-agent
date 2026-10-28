# Arquitetura do QA Status Report Agent

## Entrada vigente

O fluxo usa o workbook fixo definido em `config/workbook_schema.yaml`, com abas `Projeto`, `Funcionalidades`, `Cenários` e `Bugs`. O modelo vazio está em `inputs/templates/qa_status_report_template.xlsx`; o exemplo contém somente dados sintéticos para testes. A entrada adaptativa do ADR 0001 foi substituída pelo modelo fixo; o pacote `discovery/` permanece histórico e não é chamado pelo novo fluxo.

## Componentes implementados

### Leitura e validação

`data/fixed_workbook.py` abre `.xlsx` e `.xlsm` em modo somente leitura e valida abas, cabeçalhos, tipos, período, campos obrigatórios, IDs únicos e referências explícitas. Linhas inteiramente vazias são ignoradas; linhas parcialmente preenchidas são validadas. Fórmulas não são recalculadas: cache disponível é utilizado com ressalva, e valores sem cache não são inferidos. Todos os registros guardam aba, coluna, linha e coordenada.

### Métricas

`metrics/fixed_report.py` calcula total de cenários cadastrados, distribuição dos cinco status, progresso e status por funcionalidade e contagem de bugs por ID distinto. Status vazio de cenário equivale a `Em Andamento`. Progresso = (`Aprovado` + `Falha`) / cenários não ignorados; denominador zero resulta em indisponível. A aba Bugs vazia resulta em zero bugs conforme confirmação do usuário. O arredondamento de progresso para exibição é percentual inteiro, metade para cima. Os resultados carregam fórmula/regra e proveniência.

### Observações

O slide 3 agrupa, por funcionalidade, as observações não vazias dos cenários e prefixa cada texto com o ID do cenário. A composição é determinística e preserva os textos sem parafrasear, acrescentar causas ou escolher entre relatos divergentes. As referências de origem ficam nas notas do slide. Nenhum modelo de IA é chamado e não há subagente executável para essa tarefa.

### Apresentação e CLI

`cli.py` coordena leitura, validação, cálculos e geração. `presentation/generate_presentation.mjs` cria quatro slides editáveis: capa com projeto/período; gráfico de pizza dos cinco status e total planejado ao lado; tabela de progresso por funcionalidade; tabela de bugs. Tabelas e gráfico são objetos nativos do PowerPoint. O gerador inclui as referências às linhas nas notas do apresentador e não refaz cálculos.

O gerador usa Artifact Tool no runtime Codex. Por padrão busca o runtime em `~/.cache/codex-runtimes/codex-primary-runtime/dependencies/node`; `QA_NODE_EXECUTABLE` e `QA_ARTIFACT_TOOL_MODULE` permitem definir os caminhos. A CLI grava em `outputs/` por padrão, não sobrescreve saídas existentes e verifica que o hash da entrada permanece igual.

## Regras aprovadas

- Categorias: `Falha`, `Ignorado`, `Bloqueado`, `Em Andamento`, `Aprovado`; total planejado não é fatia.
- Status vazio: `Em Andamento`, sem gravar no Excel.
- Status funcional: precedência `Falha` > `Bloqueado` > `Em Andamento` > `Aprovado` quando todos os aplicáveis aprovados > `Ignorado` quando todos ignorados. Funcionalidade sem cenários recebe `Sem cenários` na apresentação.
- Bugs por funcionalidade: IDs distintos com vínculo explícito para funcionalidade e cenário; aba vazia conta como zero, conforme decisão do usuário.
- Ausência, dado inválido e fórmula sem cache continuam distintos. Uma inconsistência estrutural ou referência quebrada interrompe a criação do relatório.
- A apresentação não inventa conteúdo nem interpreta os dados além dos cálculos fornecidos.

## Limitações e decisões futuras

- Identidade visual corporativa e inclusão de logotipo ainda não foram definidos; a apresentação atual usa estilo profissional neutro.
- O layout mantém exatamente quatro slides, suporta até 20 linhas de dados em cada tabela e também verifica a altura real com base nos textos. Se o conteúdo não couber com leitura adequada, a geração falha com mensagem clara em vez de omitir registros.
- Instalação/distribuição do Node e Artifact Tool fora do runtime Codex ainda precisa ser definida.
- Análise de riscos e orquestração multiagente não estão implementadas; as instruções em `instructions/` descrevem papéis, mas não iniciam subagentes.

