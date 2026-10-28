"""Prepare a JSON-safe payload for the presentation renderer."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qa_status_report.data.fixed_models import QAWorkbook
from qa_status_report.metrics.fixed_report import FixedReportMetrics


def _origin_dict(origin: Any) -> dict[str, Any]:
    return {
        "workbook": origin.workbook,
        "sheet": origin.sheet,
        "column": origin.column,
        "row": origin.row,
        "coordinate": origin.coordinate,
    }


def build_presentation_payload(workbook: QAWorkbook, metrics: FixedReportMetrics) -> dict[str, Any]:
    return {
        "source_workbook": Path(workbook.path).name,
        "project": {
            "name": workbook.project.name,
            "period_start": workbook.project.period_start.isoformat(),
            "period_end": workbook.project.period_end.isoformat(),
            "origins": [_origin_dict(origin) for origin in workbook.project.origins],
        },
        "planned_scenarios": metrics.planned_scenario_total.value,
        "status_distribution": [
            {
                "status": status,
                "count": count,
                "origins": [
                    _origin_dict(origin)
                    for scenario in workbook.scenarios if scenario.status == status
                    for origin in scenario.origins if origin.column == "Status"
                ],
            }
            for status, count in metrics.status_distribution
        ],
        "functionalities": [
            {
                "id": rollup.functionality.id,
                "name": rollup.functionality.name,
                "status": rollup.status,
                "progress_percent": rollup.progress_percent,
                "bug_count": rollup.bug_count,
                "observation_summary": rollup.observation_summary,
                "observation_unavailable": any(
                    note.code == "formula_without_cache"
                    and note.origin is not None
                    and note.origin.sheet == "Cenários"
                    and note.origin.column == "Observações"
                    and note.origin.row in {origin.row for scenario in workbook.scenarios if scenario.functionality_id == rollup.functionality.id for origin in scenario.origins}
                    for note in workbook.notes
                ),
                "scenario_ids": list(rollup.scenario_ids),
                "status_origins": [
                    {"workbook": origin.workbook, "sheet": origin.sheet, "column": origin.column, "row": origin.row, "coordinate": origin.coordinate}
                    for origin in rollup.status_provenance
                ],
                "progress_origins": [
                    {"workbook": item.workbook, "sheet": item.sheet, "column": item.column, "row": item.row, "coordinate": item.coordinate}
                    for item in rollup.progress_metric.provenance
                ],
                "bug_origins": [
                    {"workbook": item.workbook, "sheet": item.sheet, "column": item.column, "row": item.row, "coordinate": item.coordinate}
                    for item in rollup.bug_count_metric.provenance
                ],
                "observation_origins": [
                    {"workbook": item.workbook, "sheet": item.sheet, "column": item.column, "row": item.row, "coordinate": item.coordinate}
                    for scenario in workbook.scenarios if scenario.functionality_id == rollup.functionality.id and scenario.observations
                    for item in scenario.origins if item.column == "Observações"
                ],
            }
            for rollup in metrics.functionalities
        ],
        "bugs": [
            {
                "id": bug.id, "description": bug.description, "status": bug.status,
                "severity": bug.severity, "responsible": bug.responsible,
                "opened_at": bug.opened_at.isoformat(),
                "origins": [_origin_dict(origin) for origin in bug.origins],
            }
            for bug in workbook.bugs
        ],
        "notes": [
            {
                "code": note.code, "message": note.message,
                "origin": _origin_dict(note.origin) if note.origin else None,
            }
            for note in workbook.notes
        ],
    }


__all__ = ["build_presentation_payload"]
