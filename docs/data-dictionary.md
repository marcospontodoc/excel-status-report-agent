# Dicionário de dados do template fixo de QA

O workbook principal segue `config/workbook_schema.yaml`. Abas e colunas são fixas. O modelo vazio está em `inputs/templates/qa_status_report_template.xlsx`; o workbook em `inputs/examples/` contém exclusivamente dados sintéticos para testes. Linhas de dados totalmente vazias em qualquer aba são espaços para preenchimento e não representam registros; linhas parcialmente preenchidas devem ser validadas e não descartadas silenciosamente.

## Abas e campos

### `Projeto`

| Coluna | Tipo | Obrigatório | Uso |
|---|---|---:|---|
| `Nome do Projeto` | texto | sim | Título da capa |
| `Início do Período` | data | sim | Início do período exibido na capa |
| `Fim do Período` | data | sim | Fim do período exibido na capa |

### `Funcionalidades`

| Coluna | Tipo | Obrigatório | Uso |
|---|---|---:|---|
| `ID da Funcionalidade` | identificador | sim | Chave única e vínculo com cenários/bugs |
| `Nome da Funcionalidade` | texto | sim | Linha da tabela de progresso |

Status, progresso, quantidade de bugs e observação do slide são derivados de cenários/bugs e não são digitados nesta aba.

### `Cenários`

| Coluna | Tipo | Obrigatório | Uso |
|---|---|---:|---|
| `ID da Funcionalidade` | referência | sim | Vínculo com uma funcionalidade existente |
| `ID do Cenário` | identificador | sim | Chave única do cenário |
| `Descrição do Cenário` | texto | sim | Identificação legível do cenário |
| `Pré-requisitos` | texto | não | Contexto do teste; não aparece no resumo salvo quando necessário |
| `Passo a Passo` | texto | não | Procedimento; não aparece no resumo executivo |
| `Status` | enum | não | `Falha`, `Ignorado`, `Bloqueado`, `Em Andamento`, `Aprovado`; vazio é interpretado como `Em Andamento` |
| `Responsável` | texto | não | Responsável pelo cenário |
| `Observações` | texto | não | Evidência textual para futura síntese por funcionalidade |

Cada cenário pertence a uma funcionalidade. O agente deve validar a referência. Não inferir relações pelo texto.

### `Bugs`

| Coluna | Tipo | Obrigatório | Uso |
|---|---|---:|---|
| `ID do Bug` | identificador | sim | Chave única e deduplicação |
| `ID da Funcionalidade` | referência | sim | Vínculo explícito com funcionalidade |
| `ID do Cenário` | referência | sim | Vínculo explícito com cenário |
| `Descrição do Bug` | texto | sim | Descrição da tabela de bugs |
| `Status` | texto | sim | Status bruto do bug, sem normalização não aprovada |
| `Severidade` | texto | sim | Severidade bruta |
| `Responsável` | texto | sim | Responsável pelo bug |
| `Data de Abertura` | data | sim | Data exibida na tabela de bugs |

IDs de funcionalidade e cenário precisam existir e o cenário precisa pertencer à funcionalidade informada. Bugs por funcionalidade são contados por IDs distintos.

## Regras derivadas aprovadas

- Total planejado: contagem de todas as linhas válidas da aba `Cenários`; mostrado ao lado da pizza, sem fatia própria.
- Pizza: contagem de cenários pelos cinco status aprovados; `Ignorado` participa.
- Status vazio: contado como `Em Andamento` para agregações, sem gravar de volta no Excel.
- Progresso funcional: cenários `Aprovado` ou `Falha` divididos pelos cenários não ignorados. Se não houver denominador, a métrica fica `unavailable`.
- Status funcional: `Falha` se qualquer cenário falhar; senão `Bloqueado` se houver bloqueio; senão `Em Andamento` se houver andamento/status vazio; senão `Aprovado` se todos os aplicáveis forem aprovados; `Ignorado` quando todos forem ignorados.
- Bug count funcional: IDs distintos vinculados explicitamente à funcionalidade.
- Se a aba Bugs não tiver registros preenchidos, a contagem é zero, conforme decisão explícita do usuário.
- Observação de slide: agrupamento determinístico das observações não vazias vinculadas à funcionalidade, com ID do cenário antes de cada texto; conservar referências de origem, sem paráfrase por IA.


## Proveniência

Valores devem manter workbook, aba, coluna, linha e coordenada. Resultados agregados devem apontar para todas as linhas contribuintes e informar limitações. A planilha original é somente de leitura.









