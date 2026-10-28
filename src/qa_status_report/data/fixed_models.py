"""Typed records for the approved fixed QA status workbook."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class CellOrigin:
    workbook: str
    sheet: str
    column: str
    row: int
    coordinate: str


@dataclass(frozen=True)
class ProjectInfo:
    name: str
    period_start: date
    period_end: date
    origins: tuple[CellOrigin, ...]


@dataclass(frozen=True)
class Functionality:
    id: str
    name: str
    origins: tuple[CellOrigin, ...]


@dataclass(frozen=True)
class Scenario:
    id: str
    functionality_id: str
    description: str
    status: str
    responsible: str | None
    observations: str | None
    origins: tuple[CellOrigin, ...]
    status_was_blank: bool = False


@dataclass(frozen=True)
class Bug:
    id: str
    functionality_id: str
    scenario_id: str
    description: str
    status: str
    severity: str
    responsible: str
    opened_at: date
    origins: tuple[CellOrigin, ...]


@dataclass(frozen=True)
class WorkbookNote:
    code: str
    message: str
    origin: CellOrigin | None = None


@dataclass(frozen=True)
class QAWorkbook:
    path: str
    project: ProjectInfo
    functionalities: tuple[Functionality, ...]
    scenarios: tuple[Scenario, ...]
    bugs: tuple[Bug, ...]
    notes: tuple[WorkbookNote, ...] = ()
