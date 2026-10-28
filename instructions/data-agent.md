# Instruções — dados

## Papel

Ler e validar o workbook fixo definido em `config/workbook_schema.yaml`. Este arquivo descreve responsabilidades e não inicia subagentes.

## Entrada e saída

- Entrada: caminho para um `.xlsx` ou `.xlsm` existente.
- Saída: registros tipados validados, com origem por arquivo, aba, coluna, linha e coordenada, consumidos pelos cálculos e pela apresentação.
- A implementação fica em `data/fixed_workbook.py`; a CLI não usa os mapeamentos adaptativos históricos.

## Validações

- Exigir abas e cabeçalhos fixos de `Projeto`, `Funcionalidades`, `Cenários` e `Bugs`.
- Validar campos obrigatórios, tipos, datas, IDs únicos e referências explícitas entre cenários, funcionalidades e bugs.
- Ignorar somente linhas de dados totalmente vazias; validar linhas parcialmente preenchidas.
- Interpretar status vazio de cenário como `Em Andamento`; não gravar na planilha.
- Abrir em modo somente leitura. Não recalcular fórmulas; usar valor em cache com ressalva e bloquear campo obrigatório sem cache.
- Dados inválidos, ausentes e fórmula sem cache não são intercambiáveis. Não inventar valores.

## Limites

Não calcula métricas, não interpreta riscos, não resume observações, não modifica o arquivo e não usa IA, Jira ou serviços externos.
