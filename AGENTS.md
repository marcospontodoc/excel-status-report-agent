# Instruções do projeto

## Objetivo

Este projeto lê o workbook Excel fixo de QA e gera um Status Report executivo editável de quatro slides em PowerPoint. O modelo vazio e o exemplo preenchido exclusivamente sintético estão em `inputs/`.

## Escopo e limites

- A planilha Excel padronizada será a fonte central dos dados; abas e colunas seguem o contrato em `config/workbook_schema.yaml` e em `inputs/templates/`.
- O discovery adaptativo continua no código histórico, mas não define o novo contrato fixo de entrada e precisa ser alinhado antes de integrar a leitura final do template.
- Validações estruturais e cálculos futuros devem ser determinísticos. Ausência de dados não significa zero, sucesso nem ausência de defeitos, exceto pela regra aprovada de que a aba Bugs vazia conta como zero.
- Não invente dados, métricas, datas, bugs ou conclusões. Diferencie fatos, inferências e informações ausentes.
- A descoberta/mapeamento/validação da planilha, os cálculos, a análise de riscos e a apresentação são responsabilidades distintas, descritas em `instructions/`.
- Métricas devem ser definidas e calculadas deterministicamente por código. Modelos de IA não são fonte de cálculo.
- A apresentação consome métricas aprovadas e não pode recalculá-las nem alterar seus significados.
- Os resultados e slides devem manter rastreabilidade às linhas de origem; métricas guardam coordenadas e a apresentação registra referências nas notas do apresentador.
- Nunca sobrescreva a planilha de entrada. A saída planejada é `outputs/`.
- A leitura fixa valida abas, colunas, tipos, IDs e vínculos; os cálculos de status, distribuição, progresso e bugs são determinísticos.
- A CLI gera um PowerPoint em `outputs/`; o relatório não modifica o Excel de origem e não sobrescreve arquivos de saída existentes.
- A síntese das observações agrupa o texto original por funcionalidade e identifica o ID do cenário; não reescreve observações nem usa modelos de IA.
- A apresentação usa o gerador Artifact Tool disponível no runtime Codex. Configure `QA_NODE_EXECUTABLE` e `QA_ARTIFACT_TOOL_MODULE` se o runtime não estiver no caminho padrão.
- A descoberta aceita `.xlsx` e `.xlsm`, abre os workbooks somente para leitura e não recalcula fórmulas.
- Candidatos a identificadores e relações são evidências heurísticas, nunca confirmação semântica.
- A representação de descoberta não é o JSON de decisões confirmadas por análise.
- Não implemente Jira, integrações externas ou chamadas a modelos de IA sem decisão aprovada.
- Arquivos de instrução descrevem papéis e limites; eles não executam nem iniciam subagentes por conta própria. A orquestração ainda não existe.
- O exemplo preenchido aprovado é exclusivamente sintético e serve somente para testes; não reutilize dados reais, arquivos de referência ou entradas exploratórias. Não crie outros dados fictícios sem necessidade documentada.

## Componentes planejados

Consulte `docs/architecture.md` para responsabilidades, contratos conceituais e fluxo. Consulte o arquivo de `instructions/` correspondente antes de alterar a definição de um papel especializado. O coordenador planejado é responsável por ordenar etapas, consolidar resultados e bloquear a publicação quando houver inconsistências relevantes; ele ainda não é executável.

## Estado da implementação

`src/qa_status_report/discovery/` implementa discovery adaptativo histórico. `data/fixed_workbook.py` valida e lê o workbook fixo. `metrics/fixed_report.py` calcula os indicadores aprovados. `cli.py` coordena a leitura e a geração, e `presentation/generate_presentation.mjs` cria quatro slides editáveis com tabelas e gráfico nativos. Análise de riscos e integração executável de subagentes ainda não existem. Consulte `docs/architecture.md` e `instructions/` antes de alterar contratos.



