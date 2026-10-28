"""Typed contracts for confirmed mappings, extracted records, and validation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, time
from typing import Any, Literal

from qa_status_report.discovery.models import SourceRef

DecisionStatus = Literal["confirmed", "ignored", "pending"]
ValueStatus = Literal["valid", "missing", "invalid", "formula_without_cache"]
ValidationStatus = Literal["ready", "blocked"]
EntityName = Literal[
    "project", "sprint", "release", "requirement", "test_scenario", "test_execution", "bug"
]


@dataclass(frozen=True)
class Provenance:
    workbook: str
    sheet: str
    column: str
    row: int
    coordinate: str


@dataclass(frozen=True)
class MappingDecision:
    canonical_field: str
    status: DecisionStatus
    source: SourceRef | None
    justification: str
    required: bool = False
    blocking: bool = False


@dataclass(frozen=True)
class MappingDecisionSet:
    workbook: str
    review_complete: bool
    decisions: tuple[MappingDecision, ...] = ()
    blocking_ambiguities: tuple[str, ...] = ()
    required_fields: tuple[str, ...] = ()


@dataclass(frozen=True)
class RecordValue:
    status: ValueStatus
    value: Any = None
    raw_value: Any = None
    provenance: Provenance | None = None
    is_formula: bool = False
    cached_value_available: bool | None = None
    issue: str | None = None


@dataclass(frozen=True)
class CanonicalRecord:
    entity: EntityName
    source_record_id: str
    source_sheet: str
    fields: dict[str, RecordValue]
    provenance: tuple[Provenance, ...]


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    canonical_field: str | None = None
    provenance: Provenance | SourceRef | None = None
    blocking: bool = False


@dataclass(frozen=True)
class ValidationState:
    status: ValidationStatus
    issues: tuple[ValidationIssue, ...] = ()
    unresolved_blocking_ambiguities: tuple[str, ...] = ()
    required_decisions_pending: tuple[str, ...] = ()
    review_complete: bool = False


@dataclass(frozen=True)
class CanonicalDataset:
    """A dataset that passed the global extraction gate and can be consumed later."""

    workbook: str
    records: tuple[CanonicalRecord, ...]
    mapping_decisions: tuple[MappingDecision, ...]
    validation: ValidationState


@dataclass(frozen=True)
class ExtractionResult:
    workbook: str
    records: tuple[CanonicalRecord, ...]
    validation: ValidationState
    dataset: CanonicalDataset | None = None
    limitations: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, *, indent: int = 2) -> str:
        import json

        def serialize(value: Any) -> Any:
            if isinstance(value, (date, datetime, time)):
                return value.isoformat()
            raise TypeError(f"Tipo não serializável: {type(value).__name__}")

        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent, default=serialize)
