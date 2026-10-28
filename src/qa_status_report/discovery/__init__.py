"""Adaptive discovery of Excel workbook structure and canonical QA mappings."""

from __future__ import annotations

from pathlib import Path

from .mapping import suggest_mappings, suggest_relations
from .models import DiscoveryResult
from .profiler import profile_workbook
from .reader import (
    CorruptWorkbookError,
    UnsupportedWorkbookFormatError,
    WorkbookDiscoveryError,
    read_workbook,
)


def discover_workbook(path: str | Path) -> DiscoveryResult:
    """Discover workbook structure and propose unconfirmed canonical mappings."""
    workbook = read_workbook(path)
    sheets, identifiers = profile_workbook(workbook)
    mappings = suggest_mappings(workbook)
    relations = suggest_relations(workbook, identifiers)
    return DiscoveryResult(
        format_version=1,
        workbook=workbook.path.name,
        supported_format=workbook.path.suffix.casefold(),
        sheets=sheets,
        mappings=mappings,
        identifier_candidates=identifiers,
        relation_candidates=relations,
        limitations=workbook.limitations,
    )


__all__ = [
    "CorruptWorkbookError",
    "DiscoveryResult",
    "UnsupportedWorkbookFormatError",
    "WorkbookDiscoveryError",
    "discover_workbook",
]
