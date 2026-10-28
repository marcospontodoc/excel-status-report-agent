"""Public, JSON-serializable data structures for workbook discovery."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Confidence = Literal["high", "medium", "low"]
MappingState = Literal["recognized", "inferred", "ambiguous", "missing"]


@dataclass(frozen=True)
class SourceRef:
    workbook: str
    sheet: str
    column: str | None = None
    row: int | None = None
    coordinate: str | None = None


@dataclass(frozen=True)
class FormulaObservation:
    source: SourceRef
    formula_present: bool
    cached_value_available: bool
    cached_value_type: str | None = None


@dataclass(frozen=True)
class IdentifierCandidate:
    source: SourceRef
    confidence: Confidence
    evidence: list[str]
    non_empty_count: int
    distinct_value_count: int
    uniqueness_ratio: float | None
    is_confirmed_identifier: bool = False


@dataclass(frozen=True)
class ColumnProfile:
    source: SourceRef
    header_row: int | None
    header_present: bool
    data_row_count: int
    non_empty_count: int
    missing_count: int
    observed_types: dict[str, int]
    formula_count: int
    formula_cached_value_count: int
    formula_without_cached_value_count: int
    formula_observations: list[FormulaObservation] = field(default_factory=list)
    identifier_candidate: IdentifierCandidate | None = None


@dataclass(frozen=True)
class SheetProfile:
    name: str
    state: Literal["profiled", "no_header_detected", "empty"]
    header_row: int | None
    columns: list[ColumnProfile]
    data_row_count: int
    source: SourceRef


@dataclass(frozen=True)
class MappingEvidence:
    description: str
    source: SourceRef


@dataclass(frozen=True)
class MappingSuggestion:
    canonical_field: str
    state: MappingState
    confidence: Confidence
    sources: list[SourceRef]
    justification: str
    evidence: list[MappingEvidence]
    is_confirmed: bool = False


@dataclass(frozen=True)
class RelationCandidate:
    source: SourceRef
    target: SourceRef
    confidence: Confidence
    evidence: list[str]
    source_value_coverage: float
    shared_distinct_value_count: int
    semantic_confirmation_required: bool = True
    is_confirmed_relation: bool = False


@dataclass(frozen=True)
class DiscoveryResult:
    format_version: int
    workbook: str
    supported_format: str
    sheets: list[SheetProfile]
    mappings: list[MappingSuggestion]
    identifier_candidates: list[IdentifierCandidate]
    relation_candidates: list[RelationCandidate]
    limitations: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible structure, separate from confirmation records."""
        return asdict(self)

    def to_json(self, *, indent: int = 2) -> str:
        import json

        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
