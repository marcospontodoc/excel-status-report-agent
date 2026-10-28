# Instruções — métricas

## Papel

Calcular deterministicamente os resultados usados no Status Report a partir dos registros validados do workbook fixo. Este arquivo documenta regras e não executa subagentes.

## Regras implementadas

- Status de cenário permitido: `Falha`, `Ignorado`, `Bloqueado`, `Em Andamento`, `Aprovado`; campo vazio equivale a `Em Andamento`.
- Total planejado: quantidade de cenários válidos, exibida ao lado do gráfico sem fatia própria.
- Distribuição: contagem dos cinco status, incluindo `Ignorado`.
- Progresso funcional: `(Aprovado + Falha) / cenários não ignorados * 100`; sem denominador, indisponível. Exibição arredondada para inteiro usando metade para cima.
- Status funcional: `Falha` se houver falha; senão `Bloqueado` se houver bloqueio; senão `Em Andamento` se houver andamento; senão `Aprovado` se os cenários aplicáveis estiverem todos aprovados; `Ignorado` se todos forem ignorados. Sem cenários: sem status derivável.
- Bugs por funcionalidade: quantidade de IDs distintos com vínculos explícitos. Aba Bugs vazia significa 0 bugs, conforme decisão do usuário.
- Cada resultado preserva fórmula/regra, campos de origem, proveniência e limitações.

## Limites

Sem métricas baseadas em dados inválidos, sem tratar ausências como zero (exceto aba Bugs vazia conforme a regra aprovada), sem redefinir fórmulas ou normalizar status de bugs.
