# ADR 0003 — Implementação do resumo de observações e aba de bugs vazia

- **Estado:** aprovada pelo usuário
- **Data:** 2026-10-27

## Decisões

- Quando a aba `Bugs` estiver vazia, a quantidade de bugs é exibida como zero.
- As observações são agrupadas deterministicamente por funcionalidade, com o ID do cenário antes do texto original. A implementação não usa IA nem reescreve os textos.
- O projeto pode gerar o relatório sem criar um subagente para esse agrupamento; subagentes continuam sendo papéis documentais, sem execução automática.

## Consequências

- A contagem zero para aba vazia é uma regra de produto explicitamente aprovada, distinta do tratamento geral de ausência de dados.
- A coluna de observações preserva os relatos registrados e mantém proveniência nas notas do slide. Um resumo em prosa gerado por modelo continua fora do escopo.
