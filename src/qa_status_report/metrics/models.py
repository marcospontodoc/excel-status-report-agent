"""Serializable result contract for future deterministic metrics."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

from qa_status_report.data.models import Provenance

MetricStatus = Literal["calculated", "unavailable", "blocked"]


@dataclass(frozen=True)
class MetricResult:
    metric_id: str
    status: MetricStatus
    value: int | float | None
    formula_id: str | None
    formula_description: str | None
    source_fields: tuple[str, ...]
    provenance: tuple[Provenance, ...]
    limitations: tuple[str, ...] = ()
    reason: str | None = None

    def __post_init__(self) -> None:
        if self.status == "calculated":
            if self.value is None or not self.formula_id or not self.formula_description:
                raise ValueError("Métrica calculada precisa de valor e definição de fórmula identificável.")
            if self.reason is not None:
                raise ValueError("Métrica calculada não deve usar motivo de indisponibilidade/bloqueio.")
        elif self.status in {"unavailable", "blocked"}:
            if self.value is not None:
                raise ValueError("Métrica indisponível/bloqueada não pode conter valor numérico.")
            if not self.reason:
                raise ValueError("Métrica indisponível/bloqueada precisa explicar o motivo.")
        else:
            raise ValueError(f"Estado de métrica desconhecido: {self.status}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, *, indent: int = 2) -> str:
        import json

        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
