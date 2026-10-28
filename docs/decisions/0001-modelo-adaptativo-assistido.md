# ADR 0001 — Modelo adaptativo assistido para planilhas

- **Estado:** substituída pela ADR 0002 — Workbook fixo de Status Report QA
- **Data:** 2026-10-26

Esta decisão registrou a proposta inicial de aceitar planilhas de estruturas variáveis e solicitar confirmação para mapeamentos ambíguos. A decisão de produto mudou: o fluxo principal adotará um workbook fixo, descrito em `config/workbook_schema.yaml` e distribuído como modelo em `inputs/templates/`.

O código adaptativo das Fases 3/4A permanece no repositório como implementação anterior e não deve ser confundido com o contrato atual do workbook. A ADR 0002 é a referência vigente.
