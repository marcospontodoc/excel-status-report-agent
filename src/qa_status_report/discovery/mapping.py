"""Rule-based suggestions for mapping workbook headers to canonical QA fields."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable

from .models import MappingEvidence, MappingSuggestion, RelationCandidate, SourceRef
from .profiler import normalize_text
from .reader import ColumnData, WorkbookData


@dataclass(frozen=True)
class CanonicalField:
    name: str
    aliases: tuple[str, ...]
    expected_types: tuple[str, ...]


# Explicit deterministic synonym registry, synchronized with entities/fields in workbook_schema.yaml.
CANONICAL_FIELDS = (
    CanonicalField("project.id", ("project id", "id do projeto", "identificador do projeto", "project key", "chave do projeto"), ("string", "integer")),
    CanonicalField("project.name", ("project name", "nome do projeto", "projeto", "product name", "produto"), ("string",)),
    CanonicalField("project.reference_period_start", ("reference period start", "início do período de referência", "data inicial do relatório", "report start date"), ("date", "datetime")),
    CanonicalField("project.reference_period_end", ("reference period end", "fim do período de referência", "data final do relatório", "report end date"), ("date", "datetime")),
    CanonicalField("sprint.id", ("sprint id", "id da sprint", "sprint key", "chave da sprint"), ("string", "integer")),
    CanonicalField("sprint.project_id", ("sprint project id", "id do projeto da sprint"), ("string", "integer")),
    CanonicalField("sprint.name", ("sprint name", "nome da sprint", "sprint", "iteração", "iteration"), ("string",)),
    CanonicalField("sprint.start_date", ("sprint start date", "início da sprint", "data inicial da sprint"), ("date", "datetime")),
    CanonicalField("sprint.end_date", ("sprint end date", "fim da sprint", "data final da sprint"), ("date", "datetime")),
    CanonicalField("release.id", ("release id", "id da versão", "version id", "release key"), ("string", "integer")),
    CanonicalField("release.project_id", ("release project id", "id do projeto da versão"), ("string", "integer")),
    CanonicalField("release.name", ("release name", "version name", "nome da versão", "versão", "release"), ("string",)),
    CanonicalField("release.start_date", ("release start date", "início da versão", "data inicial da versão"), ("date", "datetime")),
    CanonicalField("release.target_date", ("target release date", "release target date", "data alvo da versão", "previsão da versão"), ("date", "datetime")),
    CanonicalField("release.released_at", ("released at", "release date", "data de lançamento", "data de release"), ("date", "datetime")),
    CanonicalField("requirement.id", ("requirement id", "id do requisito", "requirement key", "chave do requisito"), ("string", "integer")),
    CanonicalField("requirement.project_id", ("requirement project id", "id do projeto do requisito"), ("string", "integer")),
    CanonicalField("requirement.title", ("requirement title", "requirement name", "título do requisito", "nome do requisito", "requisito"), ("string",)),
    CanonicalField("requirement.status_raw", ("requirement status", "status do requisito", "estado do requisito"), ("string", "integer", "decimal", "boolean")),
    CanonicalField("test_scenario.id", ("test case id", "test scenario id", "scenario id", "id do cenário", "id do cenário de teste", "id do caso de teste", "test id"), ("string", "integer")),
    CanonicalField("test_scenario.project_id", ("scenario project id", "id do projeto do cenário"), ("string", "integer")),
    CanonicalField("test_scenario.title", ("test case title", "test case name", "scenario name", "test scenario", "cenário de teste", "caso de teste", "nome do cenário"), ("string",)),
    CanonicalField("test_scenario.requirement_ids", ("requirement ids", "linked requirements", "requisitos associados", "ids dos requisitos"), ("string",)),
    CanonicalField("test_execution.id", ("execution id", "test execution id", "id da execução", "id da execução de teste", "run id", "test run id"), ("string", "integer")),
    CanonicalField("test_execution.scenario_id", ("execution scenario id", "test case id for execution", "id do cenário executado", "scenario reference"), ("string", "integer")),
    CanonicalField("test_execution.executed_at", ("executed at", "execution date", "data da execução", "data/hora da execução", "run date"), ("date", "datetime")),
    CanonicalField("test_execution.sprint_id", ("execution sprint id", "sprint id for execution", "id da sprint da execução"), ("string", "integer")),
    CanonicalField("test_execution.release_id", ("execution release id", "release id for execution", "id da versão da execução"), ("string", "integer")),
    CanonicalField("test_execution.status_raw", ("execution status", "test execution status", "status da execução", "resultado da execução", "test result", "resultado do teste"), ("string", "integer", "decimal", "boolean")),
    CanonicalField("test_execution.outcome", ("normalized outcome", "resultado normalizado"), ("string",)),
    CanonicalField("test_execution.attempt_number", ("attempt number", "execution attempt", "número da tentativa", "tentativa"), ("integer", "string")),
    CanonicalField("test_execution.retest_of_id", ("retest of id", "previous execution id", "id da execução retestada", "id da execução anterior"), ("string", "integer")),
    CanonicalField("bug.id", ("bug id", "defect id", "id do bug", "id do defeito", "bug key", "chave do bug"), ("string", "integer")),
    CanonicalField("bug.project_id", ("bug project id", "id do projeto do bug"), ("string", "integer")),
    CanonicalField("bug.title", ("bug title", "defect title", "bug summary", "resumo do bug", "título do bug", "descrição do bug"), ("string",)),
    CanonicalField("bug.status_raw", ("bug status", "defect status", "status do bug", "estado do defeito"), ("string", "integer", "decimal", "boolean")),
    CanonicalField("bug.severity_raw", ("bug severity", "defect severity", "severidade do bug", "gravidade do defeito"), ("string", "integer", "decimal")),
    CanonicalField("bug.priority_raw", ("bug priority", "defect priority", "prioridade do bug", "prioridade do defeito"), ("string", "integer", "decimal")),
    CanonicalField("bug.release_ids", ("bug release ids", "affected version", "found in version", "versão afetada", "versão encontrada", "versão do bug"), ("string", "integer")),
    CanonicalField("bug.scenario_ids", ("bug scenario ids", "related test cases", "cenários relacionados ao bug", "casos de teste relacionados"), ("string", "integer")),
    CanonicalField("bug.execution_ids", ("bug execution ids", "related executions", "execuções relacionadas ao bug"), ("string", "integer")),
)


def _field_type(column: ColumnData) -> tuple[str, ...]:
    return tuple(sorted(column.observed_types))


def _score(header: str, aliases: Iterable[str]) -> tuple[float, str] | None:
    normalized = normalize_text(header)
    if not normalized:
        return None
    normalized_aliases = [normalize_text(alias) for alias in aliases]
    if normalized in normalized_aliases:
        return 1.0, "Cabeçalho corresponde exatamente a um sinônimo documentado."
    header_tokens = set(normalized.split())
    best = 0.0
    for alias in normalized_aliases:
        alias_tokens = set(alias.split())
        if not alias_tokens:
            continue
        overlap = len(header_tokens & alias_tokens) / len(header_tokens | alias_tokens)
        contains = 0.72 if alias in normalized or normalized in alias else 0.0
        best = max(best, overlap, contains)
    if best >= 0.5:
        return best, "Cabeçalho tem correspondência parcial com sinônimo documentado."
    return None


def suggest_mappings(workbook: WorkbookData) -> list[MappingSuggestion]:
    candidates: dict[str, list[tuple[float, ColumnData, str, tuple[str, ...]]]] = {
        field.name: [] for field in CANONICAL_FIELDS
    }
    header_targets: dict[tuple[str, str], list[tuple[str, float]]] = {}
    for sheet in workbook.sheets:
        for column in sheet.columns:
            if not column.header:
                continue
            for field in CANONICAL_FIELDS:
                scored = _score(column.header, field.aliases)
                if scored:
                    score, reason = scored
                    observed_types = _field_type(column)
                    compatible = not observed_types or set(observed_types).issubset(set(field.expected_types))
                    adjusted = score if compatible else min(score, 0.45)
                    candidates[field.name].append((adjusted, column, reason, observed_types))
                    header_targets.setdefault((sheet.name, column.letter), []).append((field.name, adjusted))

    results: list[MappingSuggestion] = []
    for field in CANONICAL_FIELDS:
        options = sorted(candidates[field.name], key=lambda item: item[0], reverse=True)
        if not options:
            results.append(
                MappingSuggestion(
                    canonical_field=field.name,
                    state="missing",
                    confidence="low",
                    sources=[],
                    justification="Nenhum cabeçalho corresponde aos sinônimos documentados; ausência de sugestão não prova ausência do conceito na fonte.",
                    evidence=[],
                )
            )
            continue

        best_score = options[0][0]
        best_options = [option for option in options if option[0] == best_score]
        targets_by_source: dict[tuple[str, str], list[str]] = {}
        for _, column, _, _ in best_options:
            sheet = next(sheet for sheet in workbook.sheets if any(candidate is column for candidate in sheet.columns))
            competitive_targets = [
                target for target, score in header_targets.get((sheet.name, column.letter), [])
                if score >= best_score - 0.15
            ]
            targets_by_source[(sheet.name, column.letter)] = competitive_targets
        tied_sources = len(targets_by_source) > 1
        source_has_multiple_targets = any(len(targets) > 1 for targets in targets_by_source.values())
        ambiguous = tied_sources or source_has_multiple_targets
        selected = best_options if ambiguous else [best_options[0]]
        source_refs: list[SourceRef] = []
        evidence: list[MappingEvidence] = []
        for score, column, reason, observed_types in selected:
            sheet = next(sheet for sheet in workbook.sheets if any(candidate is column for candidate in sheet.columns))
            source = SourceRef(workbook.path.name, sheet.name, column.header or column.letter, column.header_row, f"{column.letter}{column.header_row}" if column.header_row else None)
            source_refs.append(source)
            evidence.append(MappingEvidence(reason, source))
            if observed_types:
                evidence.append(MappingEvidence(f"Tipos observados: {', '.join(observed_types)}.", source))
            else:
                evidence.append(MappingEvidence("Não foi possível inferir tipo a partir de valores preenchidos.", source))
            evidence.append(
                MappingEvidence(
                    f"Perfil: {column.non_empty_count} preenchidos, {column.missing_count} ausentes e {len(column.distinct_value_hashes)} distintos; valores individuais não são incluídos no resultado.",
                    source,
                )
            )

        selected_column = best_options[0][1]
        selected_types = set(_field_type(selected_column))
        compatible_best = best_score >= 0.72 and (not selected_types or selected_types.issubset(set(field.expected_types)))
        if ambiguous:
            state = "ambiguous"
            confidence = "low"
            justification = "Há mais de uma interpretação/candidato igualmente plausível; requer confirmação semântica."
        elif best_score == 1.0 and compatible_best and bool(selected_types):
            state = "recognized"
            confidence = "high"
            justification = "Sinônimo exato, tipo e perfil observados compatíveis e nenhum conflito concorrente detectado; ainda é apenas sugestão."
        elif compatible_best:
            state = "inferred"
            confidence = "medium"
            justification = "Correspondência parcial ou evidência incompleta; requer revisão."
        else:
            state = "ambiguous"
            confidence = "low"
            justification = "O cabeçalho sugere o conceito, mas os tipos observados são incompatíveis ou conflitantes."
        results.append(
            MappingSuggestion(
                canonical_field=field.name,
                state=state,
                confidence=confidence,
                sources=source_refs,
                justification=justification,
                evidence=evidence,
            )
        )
    return results


def _normalized_values(column: ColumnData) -> set[str]:
    return column.distinct_value_hashes


def suggest_relations(workbook: WorkbookData, identifiers: list) -> list[RelationCandidate]:
    def find_column(candidate) -> ColumnData | None:
        sheet = next((item for item in workbook.sheets if item.name == candidate.source.sheet), None)
        if sheet is None:
            return None
        match = re.match(r"([A-Z]+)", candidate.source.coordinate or "")
        if match:
            return next((column for column in sheet.columns if column.letter == match.group(1)), None)
        return next((column for column in sheet.columns if (column.header or column.letter) == candidate.source.column), None)

    candidates: list[RelationCandidate] = []
    for source_candidate in identifiers:
        source_column = find_column(source_candidate)
        if source_column is None:
            continue
        source_values = _normalized_values(source_column)
        if not source_values:
            continue
        for target_candidate in identifiers:
            if source_candidate is target_candidate or source_candidate.source.sheet == target_candidate.source.sheet:
                continue
            target_column = find_column(target_candidate)
            if target_column is None:
                continue
            target_values = _normalized_values(target_column)
            if not target_values:
                continue
            shared = source_values & target_values
            coverage = len(shared) / len(source_values)
            target_unique = len(target_values) / max(target_candidate.non_empty_count, 1)
            if len(shared) < 2 or coverage < 0.8:
                continue
            evidence = [
                f"{len(shared)} valores distintos coincidem (não são exportados).",
                f"Cobertura dos valores distintos da origem: {coverage:.0%}.",
                f"Unicidade observada no alvo: {target_unique:.0%}.",
                "Coincidência e unicidade são evidências candidatas, não comprovam relação semântica.",
            ]
            header_signal = any(token in normalize_text(source_candidate.source.column or "").split() for token in ("id", "key", "chave", "codigo", "code"))
            confidence = "medium" if header_signal and target_unique >= 0.9 else "low"
            candidates.append(
                RelationCandidate(
                    source=source_candidate.source,
                    target=target_candidate.source,
                    confidence=confidence,
                    evidence=evidence,
                    source_value_coverage=round(coverage, 4),
                    shared_distinct_value_count=len(shared),
                )
            )
    return candidates


__all__ = ["CANONICAL_FIELDS", "suggest_mappings", "suggest_relations"]
