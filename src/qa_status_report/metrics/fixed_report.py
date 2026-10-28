"""Approved deterministic rollups for the fixed QA status report."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from qa_status_report.data.fixed_models import CellOrigin, Functionality, QAWorkbook
from qa_status_report.data.models import Provenance
from qa_status_report.metrics.models import MetricResult

STATUS_ORDER = ("Falha", "Ignorado", "Bloqueado", "Em Andamento", "Aprovado")


def _provenance(origins: tuple[CellOrigin, ...]) -> tuple[Provenance, ...]:
    return tuple(Provenance(origin.workbook, origin.sheet, origin.column, origin.row, origin.coordinate) for origin in origins)


@dataclass(frozen=True)
class FunctionalityRollup:
    functionality: Functionality
    status: str | None
    progress_percent: int | None
    bug_count: int
    observation_summary: str | None
    status_provenance: tuple[Provenance, ...]
    progress_metric: MetricResult
    bug_count_metric: MetricResult
    scenario_ids: tuple[str, ...]


@dataclass(frozen=True)
class FixedReportMetrics:
    planned_scenario_total: MetricResult
    status_distribution: tuple[tuple[str, int], ...]
    status_distribution_metric: MetricResult
    functionalities: tuple[FunctionalityRollup, ...]


def calculate_fixed_report_metrics(workbook: QAWorkbook) -> FixedReportMetrics:
    """Calculate only metrics defined in the approved workbook contract."""
    scenario_origin = tuple(origin for item in workbook.scenarios for origin in item.origins if origin.column == "ID do Cenário")
    planned = MetricResult(
        "planned_scenario_total", "calculated", len(workbook.scenarios), "count_valid_scenario_records",
        "Contagem de registros válidos na aba Cenários.", ("test_scenario.id",), _provenance(scenario_origin),
    )
    counts = {status: 0 for status in STATUS_ORDER}
    for scenario in workbook.scenarios:
        counts[scenario.status] += 1
    distribution_metric = MetricResult(
        "scenario_status_distribution", "calculated", len(workbook.scenarios), "count_scenarios_by_status",
        "Contagem de cenários em cada status controlado; status vazio foi interpretado como Em Andamento.",
        ("test_scenario.status_raw",), _provenance(tuple(o for s in workbook.scenarios for o in s.origins if o.column == "Status")),
    )

    scenario_groups: dict[str, list] = {functionality.id: [] for functionality in workbook.functionalities}
    bug_groups: dict[str, set[str]] = {functionality.id: set() for functionality in workbook.functionalities}
    bugs_by_functionality: dict[str, list] = {functionality.id: [] for functionality in workbook.functionalities}
    for scenario in workbook.scenarios:
        scenario_groups[scenario.functionality_id].append(scenario)
    for bug in workbook.bugs:
        bug_groups[bug.functionality_id].add(bug.id)
        bugs_by_functionality[bug.functionality_id].append(bug)

    rollups: list[FunctionalityRollup] = []
    for functionality in workbook.functionalities:
        scenarios = scenario_groups[functionality.id]
        statuses = {scenario.status for scenario in scenarios}
        if "Falha" in statuses:
            status = "Falha"
        elif "Bloqueado" in statuses:
            status = "Bloqueado"
        elif "Em Andamento" in statuses:
            status = "Em Andamento"
        elif statuses and statuses == {"Ignorado"}:
            status = "Ignorado"
        elif any(scenario.status != "Ignorado" for scenario in scenarios):
            status = "Aprovado"
        elif scenarios:
            status = "Ignorado"
        else:
            status = None

        applicable = [scenario for scenario in scenarios if scenario.status != "Ignorado"]
        if applicable:
            completed = sum(scenario.status in {"Aprovado", "Falha"} for scenario in applicable)
            percent = int((Decimal(completed) * 100 / Decimal(len(applicable))).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
            progress_metric = MetricResult(
                f"functionality_progress:{functionality.id}", "calculated", percent,
                "(count_approved + count_failed) / count_non_ignored * 100",
                "Percentual concluído; cenários Ignorado excluídos do denominador.",
                ("test_scenario.status_raw", "test_scenario.functionality_id"),
                _provenance(tuple(o for s in scenarios for o in s.origins)),
            )
        else:
            percent = None
            progress_metric = MetricResult(
                f"functionality_progress:{functionality.id}", "unavailable", None, None, None,
                ("test_scenario.status_raw", "test_scenario.functionality_id"),
                _provenance(tuple(o for s in scenarios for o in s.origins)),
                reason="Não há cenários aplicáveis; todos estão ignorados ou não há cenários vinculados à funcionalidade.",
            )

        scenario_origins = tuple(o for item in scenarios for o in item.origins)
        status_provenance = _provenance(scenario_origins)
        feature_bugs = bugs_by_functionality[functionality.id]
        bug_origins = tuple(o for item in feature_bugs for o in item.origins)
        bug_metric = MetricResult(
            f"functionality_bug_count:{functionality.id}", "calculated", len(bug_groups[functionality.id]),
            "count_distinct_bug_ids_by_functionality", "Contagem de IDs distintos de bugs com vínculos explícitos.",
            ("bug.id", "bug.functionality_id", "bug.scenario_id"), _provenance(bug_origins),
            limitations=("A aba Bugs está vazia; a contagem 0 segue a decisão de produto do usuário.",) if not workbook.bugs else (),
        )
        notes = [f"{s.id}: {s.observations.strip()}" for s in scenarios if s.observations and s.observations.strip()]
        rollups.append(FunctionalityRollup(
            functionality, status, percent, len(bug_groups[functionality.id]),
            "\n".join(notes) if notes else None, status_provenance, progress_metric, bug_metric,
            tuple(s.id for s in scenarios),
        ))
    return FixedReportMetrics(planned, tuple((status, counts[status]) for status in STATUS_ORDER), distribution_metric, tuple(rollups))


__all__ = ["FixedReportMetrics", "FunctionalityRollup", "calculate_fixed_report_metrics"]
