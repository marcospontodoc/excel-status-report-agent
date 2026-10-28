# Instruções — apresentação

## Papel

Organizar conteúdo executivo e gerar um PowerPoint editável de quatro slides a partir dos registros e métricas aprovados. A implementação fica em `presentation/generate_presentation.mjs`; este arquivo não inicia um subagente.

## Entrada planejada

- Dados validados e métricas calculadas deterministicamente, com referências de origem.
- Especificação visual e configurações aprovadas.
- Template fixo validado, resultados de status/progresso e sínteses de observações por funcionalidade, cada qual com proveniência.

## Saída planejada

- Apresentação PowerPoint editável em `outputs/`, com quatro slides, tabelas/gráfico nativos e referências de origem nas notas do apresentador.

## Limites e regras

- Não recalcule, estime, arredonde de novo, renomeie de forma ambígua nem altere métricas. Use os valores e rótulos aprovados.
- Não crie fatos, bugs, datas, riscos ou conclusões.
- Preserve distinções entre fatos, inferências, ressalvas e informações ausentes.
- Não esconda inconsistências ou limitações que o coordenador tenha mantido no conteúdo aprovado.
- Apresente somente indicadores disponíveis e preserve as razões de indisponibilidade relevantes; dado ausente nunca pode ser representado como zero ou sucesso.
- Preserve, tanto quanto o formato permitir, a rastreabilidade entre conteúdo exibido e registros que o sustentam.
- Não modifica a planilha de entrada. Convenção de nome e política para saídas existentes ainda precisam de decisão.
- O relatório terá quatro slides: capa com projeto/período; pizza com os cinco status de cenário e total planejado ao lado; tabela de progresso por funcionalidade; tabela de bugs.
- O total planejado é a quantidade de cenários cadastrados e não constitui uma fatia.
- A tabela de progresso usa status e percentual derivados pelas regras aprovadas; bugs são associados somente por IDs explícitos.
- A coluna de observação do slide 3 agrupa os textos originais dos cenários ligados à funcionalidade, prefixados pelo ID de cada cenário. Não parafraseie nem acrescente fatos; sem observações, informar que não foram registradas.
- O PowerPoint deve permanecer editável. A apresentação consome resultados prontos e não recalcula status, progresso ou contagem de bugs.
- Se as tabelas não couberem com leitura adequada, falhe com uma mensagem clara em vez de omitir registros ou criar slides extras.
