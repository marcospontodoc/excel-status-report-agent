# QA Status Report Agent

## Objetivo

Gerar um Status Report executivo editável de quatro slides em PowerPoint a partir de um workbook Excel fixo preenchido manualmente.

## Escopo implementado

- Leitura somente de leitura de `.xlsx` e `.xlsm` com validação das quatro abas, cabeçalhos, dados obrigatórios, IDs e relações explícitas.
- Cálculo determinístico da distribuição de status, progresso por funcionalidade, status agregado e bugs distintos.
- PowerPoint editável com capa e período, pizza de cinco status mais total planejado, tabela de progresso por funcionalidade e tabela de bugs.
- Observações reunidas por funcionalidade, mantendo o texto original e os IDs dos cenários; sem integração com modelos de IA.
- Rastreabilidade das fontes nas notas do apresentador.

O modelo vazio está em `inputs/templates/qa_status_report_template.xlsx`. O workbook preenchido em `inputs/examples/` contém somente dados fictícios para teste. A descoberta adaptativa e a extração canônica anteriores permanecem no código, mas não integram o fluxo do template fixo. Análise de riscos e orquestração de subagentes ainda não estão implementadas.

## Executar

Instale o pacote Python no ambiente (`python -m pip install -e .`) e execute:

```text
qa-status-report caminho/para/planilha.xlsx
```

Também é possível usar `python -m qa_status_report caminho/para/planilha.xlsx`. Para escolher o destino:

```text
qa-status-report caminho/para/planilha.xlsx --output outputs/meu-status-report.pptx
```

Por padrão, o arquivo é gravado em `outputs/` com o nome do projeto e período. A CLI não substitui arquivos existentes. O ambiente precisa ter Node.js e o módulo Artifact Tool do runtime Codex; use `QA_NODE_EXECUTABLE` e `QA_ARTIFACT_TOOL_MODULE` para informar caminhos alternativos.

## Regras e limitações

- Status vazio de cenário equivale a `Em Andamento`; categorias: `Falha`, `Ignorado`, `Bloqueado`, `Em Andamento` e `Aprovado`.
- Total planejado = número de cenários cadastrados e não é uma fatia da pizza.
- Progresso = (`Aprovado` + `Falha`) / cenários não ignorados. Sem denominador, exibe indisponível.
- Bugs têm vínculo explícito com funcionalidade e cenário; a aba Bugs vazia conta como zero conforme decisão do usuário.
- A entrada nunca é modificada. Fórmulas não são recalculadas; valor em cache recebe ressalva e fórmula sem cache não é inferida.
- O relatório tem exatamente quatro slides e suporta até 20 registros em cada tabela; conteúdo extenso que exceder o espaço legível gera erro em vez de omitir linhas.
- A apresentação usa um estilo neutro, sem logotipo corporativo configurado.

Consulte `docs/architecture.md`, `docs/data-dictionary.md` e `config/workbook_schema.yaml` para o contrato completo.

