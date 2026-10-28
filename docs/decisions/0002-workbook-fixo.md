# ADR 0002 — Workbook fixo para Status Report QA

- **Estado:** aprovada pelo usuário
- **Data:** 2026-10-27

## Contexto

O formato adaptativo dificultava garantir os campos e relações necessários para um status report de quatro slides. O usuário definiu um modelo Excel preenchido manualmente, com funcionalidades, cenários, status controlado e bugs ligados por IDs explícitos.

## Decisão

O fluxo principal receberá um workbook fixo com quatro abas: `Projeto`, `Funcionalidades`, `Cenários` e `Bugs`, conforme `config/workbook_schema.yaml` e `inputs/templates/qa_status_report_template.xlsx`.

Um exemplo preenchido em `inputs/examples/qa_status_report_fake_example.xlsx` conterá somente dados sintéticos para testes. Não usar dados do ODP de referência nem da planilha exploratória anterior.

Status de cenário aceitos: `Falha`, `Ignorado`, `Bloqueado`, `Em Andamento` e `Aprovado`. Campo vazio é tratado como `Em Andamento`. O total de cenários é exibido ao lado do gráfico, sem fatia `Planejado`; todas as cinco categorias, inclusive `Ignorado`, compõem a distribuição.

Progresso funcional = (`Aprovado` + `Falha`) / cenários aplicáveis, excluindo `Ignorado`. Status funcional segue a precedência: `Falha`, `Bloqueado`, `Em Andamento` (inclui vazio), `Aprovado` (todos os aplicáveis) e `Ignorado` (todos ignorados). Bugs são associados explicitamente à funcionalidade e ao cenário e contados por ID distinto em cada funcionalidade.

Observações registradas por cenário são agrupadas pela funcionalidade para gerar a coluna de observação no slide 3. A síntese deve preservar a proveniência, não inventar fatos e expor divergências. O método de agrupamento determinístico, sem reescrita por IA, foi definido em ADR 0003.

## Consequências

- A validação principal passa de descoberta de mapeamentos para validação determinística do template e das referências.
- O código das Fases 3/4A precisa ser alinhado ao novo contrato antes de entrar no fluxo principal.
- A planilha vazia não terá registros fictícios; o exemplo preenchido será explicitamente sintético.
- Esta ADR define o contrato do workbook; as regras de métricas e a apresentação editável foram implementadas posteriormente, mantendo este contrato como fonte.
- Observações de cenário precisam manter vínculos para rastreabilidade da síntese por funcionalidade.

