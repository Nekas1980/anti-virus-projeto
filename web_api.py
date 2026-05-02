"""
Web API REST (FastAPI) — Fase 3 (3.3) do plano.

Endpoints expostos:

* ``GET  /api/health``                      — liveness probe
* ``GET  /api/status``                      — estado do scan em curso (se houver)
* ``POST /api/scan``                        — dispara um scan async (corpo: ``{"paths": [...]}``)
* ``GET  /api/scan/{scan_id}``              — estado/resultados do scan
* ``GET  /api/scan/{scan_id}/results``      — apenas a lista de resultados
* ``GET  /api/history``                     — últimos scans persistidos (SQLite)
* ``GET  /api/reports/{scan_id}/{fmt}``     — gera + descarrega relatório (html|json|xlsx)

Sem WebSocket nem dashboard front-end (deferido). Pensado para integração com
clientes externos (curl, scripts) e como base para um dashboard futuro.

Para correr::

    pip install fastapi uvicorn
    python -m uvicorn web_api:app --reload --port 8765
"""
from __future__ import annotations

import logging
import os
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence

logger = logging.getLogger(__name__)


# Lazy FastAPI import — módulo continua importável sem fastapi instalado.
try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks
    from fastapi.responses import FileResponse, JSONResponse
    from pydantic import BaseModel, Field
    _FASTAPI_AVAILABLE = True
except ImportError:
    FastAPI = None  # type: ignore[assignment,misc]
    HTTPException = Exception  # type: ignore[assignment,misc]
    BackgroundTasks = None  # type: ignore[assignment,misc]
    FileResponse = None  # type: ignore[assignment,misc]
    JSONResponse = None  # type: ignore[assignment,misc]
    BaseModel = object  # type: ignore[assignment,misc]
    Field = lambda *a, **k: None  # type: ignore[assignment]
    _FASTAPI_AVAILABLE = False


from config import PATHS, SCAN
from excel_exporter import ExcelReportGenerator
from exclusion_matcher import ExclusionMatcher
from hash_cache import HashCache
from report_generator import (
    HTMLReportGenerator,
    ReportMetadata,
    generate_json_report,
)
from scan_history import ScanHistory
from Virus_project import (
    ScanResult,
    load_exclusions,
    load_signatures,
    save_report,
    scan_file,
)


# ─────────────────────────────────────────────────────────────────────
# In-memory scan registry (estado de scans iniciados via API)
# ─────────────────────────────────────────────────────────────────────


@dataclass
class ScanState:
    scan_id: str
    paths: List[str]
    status: str = "pending"  # pending | running | finished | error
    started_at: float = field(default_factory=time.time)
    finished_at: Optional[float] = None
    total: int = 0
    processed: int = 0
    clean: int = 0
    infected: int = 0
    skipped: int = 0
    error: Optional[str] = None
    results: List[ScanResult] = field(default_factory=list)
    metadata: Optional[ReportMetadata] = None

    def progress(self) -> float:
        return self.processed / self.total if self.total else 0.0

    def to_summary(self) -> dict:
        return {
            "scan_id": self.scan_id,
            "status": self.status,
            "paths": self.paths,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "total": self.total,
            "processed": self.processed,
            "progress": round(self.progress(), 4),
            "clean": self.clean,
            "infected": self.infected,
            "skipped": self.skipped,
            "error": self.error,
        }


_scans: Dict[str, ScanState] = {}
_scans_lock = threading.Lock()


# Modelo Pydantic ao nível do módulo — definido aqui (em vez de dentro de
# create_app) para que FastAPI consiga resolver as annotations através de
# typing.get_type_hints() apesar do `from __future__ import annotations`.
if _FASTAPI_AVAILABLE:
    class ScanRequest(BaseModel):
        paths: List[str]
else:  # pragma: no cover — definição vazia só para evitar NameError
    class ScanRequest:  # type: ignore[no-redef]
        pass


def _run_scan(state: ScanState) -> None:
    """Worker síncrono que actualiza ``state`` à medida que o scan progride."""
    cache: Optional[HashCache] = None
    try:
        state.status = "running"
        signatures = load_signatures(PATHS["signatures"])
        exclusions = load_exclusions(PATHS["exclusions"])
        matcher = ExclusionMatcher(exclusions)

        targets: List[Path] = []
        for p in state.paths:
            base = Path(p)
            if not base.exists():
                continue
            if base.is_file():
                if not matcher.matches(base):
                    targets.append(base)
            else:
                for current_root, dirs, files in os.walk(base):
                    # Podar diretórios excluídos
                    i = len(dirs) - 1
                    while i >= 0:
                        d_path = Path(current_root) / dirs[i]
                        if matcher.matches(d_path):
                            del dirs[i]
                        i -= 1
                    
                    for f in files:
                        f_path = Path(current_root) / f
                        if not matcher.matches(f_path):
                            targets.append(f_path)

        state.total = len(targets)
        if SCAN["cache_enabled"]:
            cache = HashCache(PATHS["scan_cache"])

        for f in targets:
            r = scan_file(f, signatures, cache=cache)
            state.results.append(r)
            state.processed += 1
            if r.status == "infected":
                state.infected += 1
            elif r.status == "skip":
                state.skipped += 1
            else:
                state.clean += 1

        state.finished_at = time.time()
        state.metadata = ReportMetadata(
            scan_id=state.scan_id,
            started_at=state.started_at,
            finished_at=state.finished_at,
            paths=state.paths,
        )

        out_dir = PATHS["output_dir"]
        out_dir.mkdir(parents=True, exist_ok=True)
        report_path = out_dir / f"api_scan_{state.scan_id}.json"
        save_report(state.results, report_path)

        with ScanHistory(PATHS["scan_history"]) as hist:
            hist.record(
                paths=state.paths,
                total=state.total,
                clean=state.clean,
                infected=state.infected,
                skipped=state.skipped,
                started_at=state.started_at,
                finished_at=state.finished_at,
                report_path=report_path,
            )
        state.status = "finished"
    except Exception as e:  # pragma: no cover — defensive
        logger.exception("Erro no scan via API")
        state.status = "error"
        state.error = str(e)
        state.finished_at = time.time()
    finally:
        if cache is not None:
            cache.close()


# ─────────────────────────────────────────────────────────────────────
# FastAPI app factory
# ─────────────────────────────────────────────────────────────────────


def create_app():
    """Devolve uma instância FastAPI; raises se fastapi não estiver instalado."""
    if not _FASTAPI_AVAILABLE:
        raise RuntimeError(
            "FastAPI não instalado. Corre `pip install fastapi uvicorn` para activar a API."
        )

    api = FastAPI(
        title="Antivírus Projeto — Web API",
        description="API REST para disparar scans, consultar histórico e descarregar relatórios.",
        version="0.3.0",
    )

    @api.get("/api/health")
    def health() -> dict:
        return {"status": "ok", "version": api.version}

    @api.get("/api/status")
    def status() -> dict:
        with _scans_lock:
            running = [s.to_summary() for s in _scans.values() if s.status == "running"]
        return {"running_scans": running, "total_tracked": len(_scans)}

    @api.post("/api/scan")
    def start_scan(req: ScanRequest, background: BackgroundTasks) -> dict:
        if not req.paths:
            raise HTTPException(status_code=400, detail="paths não pode ser vazio")
        scan_id = str(uuid.uuid4())
        state = ScanState(scan_id=scan_id, paths=list(req.paths))
        with _scans_lock:
            _scans[scan_id] = state
        background.add_task(_run_scan, state)
        return state.to_summary()

    @api.get("/api/scan/{scan_id}")
    def get_scan(scan_id: str) -> dict:
        state = _scans.get(scan_id)
        if not state:
            raise HTTPException(status_code=404, detail="scan_id desconhecido")
        return state.to_summary()

    @api.get("/api/scan/{scan_id}/results")
    def get_results(scan_id: str) -> dict:
        state = _scans.get(scan_id)
        if not state:
            raise HTTPException(status_code=404, detail="scan_id desconhecido")
        return {
            "scan_id": scan_id,
            "status": state.status,
            "results": [
                {
                    "file_path": r.file_path,
                    "status": r.status,
                    "reason": r.reason,
                    "sha256": r.sha256,
                }
                for r in state.results
            ],
        }

    @api.get("/api/history")
    def history(limit: int = 20) -> dict:
        with ScanHistory(PATHS["scan_history"]) as hist:
            recent = hist.recent(limit=limit)
        return {
            "count": len(recent),
            "scans": [
                {
                    "scan_id": r.scan_id,
                    "started_iso": r.started_iso,
                    "duration_seconds": round(r.duration_seconds, 3),
                    "paths": r.paths,
                    "total": r.total,
                    "clean": r.clean,
                    "infected": r.infected,
                    "skipped": r.skipped,
                    "report_path": r.report_path,
                }
                for r in recent
            ],
        }

    @api.get("/api/reports/{scan_id}/{fmt}")
    def get_report(scan_id: str, fmt: str):
        state = _scans.get(scan_id)
        if not state:
            raise HTTPException(status_code=404, detail="scan_id desconhecido")
        if state.status not in ("finished", "error"):
            raise HTTPException(status_code=409, detail="scan ainda em curso")

        out_dir = PATHS["output_dir"]
        out_dir.mkdir(parents=True, exist_ok=True)
        target = out_dir / f"api_scan_{scan_id}.{fmt}"

        if fmt == "json":
            generate_json_report(state.results, target, metadata=state.metadata)
            media = "application/json"
        elif fmt == "html":
            HTMLReportGenerator.generate(state.results, target, metadata=state.metadata)
            media = "text/html"
        elif fmt == "xlsx":
            if not ExcelReportGenerator.is_available():
                raise HTTPException(status_code=503, detail="openpyxl não instalado")
            ExcelReportGenerator.generate(state.results, target, metadata=state.metadata)
            media = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            raise HTTPException(
                status_code=400, detail=f"formato inválido: {fmt} (esperado html|json|xlsx)"
            )

        return FileResponse(str(target), media_type=media, filename=target.name)

    return api


# Auto-instancia se FastAPI presente — permite ``uvicorn web_api:app``.
app = create_app() if _FASTAPI_AVAILABLE else None


def _reset_state_for_tests() -> None:
    """Limpa registry global — uso exclusivo em testes."""
    with _scans_lock:
        _scans.clear()


if __name__ == "__main__":  # pragma: no cover
    if not _FASTAPI_AVAILABLE:
        raise SystemExit(
            "FastAPI não instalado. Corre `pip install fastapi uvicorn` para activar."
        )
    import uvicorn
    uvicorn.run("web_api:app", host="127.0.0.1", port=8765, reload=False)
