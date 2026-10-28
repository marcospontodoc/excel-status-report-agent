# Pacote de aplicação

O fluxo de produto aprovado usa o workbook fixo descrito em `config/workbook_schema.yaml`. A descoberta e a extração atualmente implementadas ainda refletem as fases anteriores e não validam diretamente o template fixo; precisam ser alinhadas antes de processar estes modelos. `metrics/` define `MetricResult`, sem implementar fórmulas. CLI, síntese de observações, riscos, apresentação e orquestração executável permanecem futuros.
