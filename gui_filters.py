"""
Filtros e ordenação para a vista de resultados — Fase 3 (3.2).

Função pura ``filter_results`` separada da GUI para permitir testes sem
depender de tkinter / customtkinter.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence

from Virus_project import ScanResult


@dataclass
class FilterCriteria:
    query: str = ""
    show_clean: bool = True
    show_infected: bool = True
    show_skipped: bool = True
    sort_by: str = "status"  # "status" | "name" | "path"

    @property
    def status_set(self) -> set[str]:
        allowed = set()
        if self.show_clean:
            allowed.add("clean")
        if self.show_infected:
            allowed.add("infected")
        if self.show_skipped:
            allowed.add("skip")
        return allowed


_STATUS_ORDER = {"infected": 0, "skip": 1, "clean": 2}


def filter_results(
    results: Sequence[ScanResult], criteria: FilterCriteria
) -> List[ScanResult]:
    """Devolve uma lista filtrada e ordenada conforme ``criteria``."""
    allowed = criteria.status_set
    needle = criteria.query.strip().lower()

    filtered: List[ScanResult] = []
    for r in results:
        if r.status not in allowed:
            continue
        if needle and needle not in r.file_path.lower():
            continue
        filtered.append(r)

    if criteria.sort_by == "name":
        filtered.sort(key=lambda r: r.file_path.rsplit("/", 1)[-1].lower())
    elif criteria.sort_by == "path":
        filtered.sort(key=lambda r: r.file_path.lower())
    else:  # status (default): infected → skip → clean, then alpha
        filtered.sort(
            key=lambda r: (_STATUS_ORDER.get(r.status, 99), r.file_path.lower())
        )
    return filtered


def format_eta(remaining_files: int, files_per_second: float) -> str:
    """Formata ETA (Estimated Time of Arrival) em mm:ss."""
    if files_per_second <= 0 or remaining_files <= 0:
        return "—"
    seconds = int(remaining_files / files_per_second)
    minutes, secs = divmod(seconds, 60)
    if minutes >= 60:
        hours, minutes = divmod(minutes, 60)
        return f"{hours}h{minutes:02d}m"
    return f"{minutes:02d}:{secs:02d}"


def format_elapsed(seconds: float) -> str:
    """Formata tempo decorrido em mm:ss."""
    if seconds < 0:
        seconds = 0
    minutes, secs = divmod(int(seconds), 60)
    if minutes >= 60:
        hours, minutes = divmod(minutes, 60)
        return f"{hours}h{minutes:02d}m"
    return f"{minutes:02d}:{secs:02d}"
