"""Deterministic profiling of columns, missing values, and identifier candidates."""

from __future__ import annotations

import re
import unicodedata

from .models import ColumnProfile, FormulaObservation, IdentifierCandidate, SheetProfile, SourceRef
from .reader import ColumnData, WorkbookData

_ID_HEADER_TERMS = {"id", "key", "chave", "codigo", "code", "identificador"}


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.casefold())
    without_marks = "".join(char for char in normalized if not unicodedata.combining(char))
    return " ".join(re.findall(r"[a-z0-9]+", without_marks))


def _source(workbook: str, sheet: str, column: ColumnData, row: int | None = None) -> SourceRef:
    coordinate = f"{column.letter}{row}" if row is not None else None
    return SourceRef(workbook, sheet, column.header or column.letter, row, coordinate)


def _identifier_candidate(workbook: str, sheet: str, column: ColumnData) -> IdentifierCandidate | None:
    non_empty = column.non_empty_count
    if not non_empty:
        return None
    distinct_count = len(column.distinct_value_hashes)
    uniqueness = distinct_count / non_empty
    header_tokens = set(normalize_text(column.header or "").split())
    header_signal = bool(header_tokens & _ID_HEADER_TERMS)
    known_count = non_empty + column.missing_count
    completeness = non_empty / max(known_count, 1)
    if not header_signal and (uniqueness < 0.98 or completeness < 0.9 or non_empty < 3):
        return None

    evidence: list[str] = []
    if header_signal:
        evidence.append("Cabeçalho contém termo associado a identificador.")
    if completeness >= 0.9:
        evidence.append(f"Preenchimento observado: {completeness:.0%}.")
    if uniqueness >= 0.98:
        evidence.append(f"Unicidade observada: {uniqueness:.0%}.")
    evidence.append("Candidato heurístico; estas evidências isoladamente não comprovam identidade semântica.")
    confidence = "medium" if header_signal and uniqueness >= 0.98 and completeness >= 0.9 else "low"
    return IdentifierCandidate(
        source=_source(workbook, sheet, column, column.header_row),
        confidence=confidence,
        evidence=evidence,
        non_empty_count=non_empty,
        distinct_value_count=distinct_count,
        uniqueness_ratio=uniqueness,
        is_confirmed_identifier=False,
    )


def profile_workbook(workbook: WorkbookData) -> tuple[list[SheetProfile], list[IdentifierCandidate]]:
    sheet_profiles: list[SheetProfile] = []
    all_identifiers: list[IdentifierCandidate] = []
    for sheet in workbook.sheets:
        profiles: list[ColumnProfile] = []
        for column in sheet.columns:
            types = column.observed_types
            formula_count = len(column.formula_observations)
            unavailable_rows = [row for row, cached, _ in column.formula_observations if not cached]
            formula_observations = [
                FormulaObservation(
                    source=SourceRef(
                        workbook.path.name,
                        sheet.name,
                        column.header or column.letter,
                        row,
                        f"{column.letter}{row}",
                    ),
                    formula_present=True,
                    cached_value_available=cached,
                    cached_value_type=cached_type,
                )
                for row, cached, cached_type in column.formula_observations
            ]
            candidate = _identifier_candidate(workbook.path.name, sheet.name, column)
            if candidate:
                all_identifiers.append(candidate)
            profiles.append(
                ColumnProfile(
                    source=_source(workbook.path.name, sheet.name, column, column.header_row),
                    header_row=column.header_row,
                    header_present=column.header is not None,
                    data_row_count=sheet.data_row_count,
                    non_empty_count=column.non_empty_count,
                    missing_count=column.missing_count,
                    observed_types=dict(sorted(types.items())),
                    formula_count=formula_count,
                    formula_cached_value_count=sum(1 for _, cached, _ in column.formula_observations if cached),
                    formula_without_cached_value_count=len(unavailable_rows),
                    formula_observations=formula_observations,
                    identifier_candidate=candidate,
                )
            )
        state = "empty" if sheet.empty else "no_header_detected" if sheet.header_row is None else "profiled"
        sheet_profiles.append(
            SheetProfile(
                name=sheet.name,
                state=state,
                header_row=sheet.header_row,
                columns=profiles,
                data_row_count=sheet.data_row_count,
                source=SourceRef(workbook.path.name, sheet.name),
            )
        )
    return sheet_profiles, all_identifiers


__all__ = ["normalize_text", "profile_workbook"]
