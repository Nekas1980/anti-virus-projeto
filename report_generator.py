"""
Gerador de Relatórios — Fase 3 do plano de melhorias.

Suporta saída em HTML (com gráficos Chart.js), JSON e Excel (.xlsx). O template
HTML é externalizado em ``templates/report.html`` e ``templates/report.css``
para permitir customização sem mexer em código Python.

A classe ``ReportMetadata`` opcional acrescenta scan_id, timestamps, paths e
taxa de scan. Compatibilidade reversa: se ``metadata=None`` for passado,
todos os relatórios continuam a funcionar com valores derivados.
"""
from __future__ import annotations

import html
import json
import logging
import os
import time
import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from string import Template
from typing import Iterable, List, Optional, Sequence

from Virus_project import ScanResult

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
HTML_TEMPLATE_PATH = TEMPLATES_DIR / "report.html"
CSS_TEMPLATE_PATH = TEMPLATES_DIR / "report.css"


@dataclass
class ReportMetadata:
    """Contexto opcional sobre a sessão de scan que originou os resultados."""

    scan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: float = field(default_factory=time.time)
    finished_at: Optional[float] = None
    paths: List[str] = field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        end = self.finished_at if self.finished_at is not None else time.time()
        return max(0.0, end - self.started_at)

    def scan_rate(self, total_files: int) -> float:
        d = self.duration_seconds
        return (total_files / d) if d > 0 else 0.0

    @property
    def started_iso(self) -> str:
        return datetime.fromtimestamp(self.started_at).strftime("%d/%m/%Y %H:%M:%S")

    def to_dict(self) -> dict:
        return {
            "scan_id": self.scan_id,
            "started_at": self.started_at,
            "started_iso": self.started_iso,
            "finished_at": self.finished_at,
            "duration_seconds": round(self.duration_seconds, 3),
            "paths": list(self.paths),
        }


def _format_duration(seconds: float) -> str:
    if seconds < 1:
        return f"{seconds * 1000:.0f} ms"
    if seconds < 60:
        return f"{seconds:.1f} s"
    minutes, secs = divmod(seconds, 60)
    return f"{int(minutes)}m {secs:.0f}s"


def _classify_risk(infected: int, total: int) -> tuple[str, str, str]:
    """Devolve (label, css_class, mensagem)."""
    if total == 0:
        return ("SEM DADOS", "warn", "Nenhum ficheiro foi analisado neste scan.")
    if infected == 0:
        return (
            "SEGURO",
            "safe",
            "Nenhuma ameaça detectada. Sistema considerado limpo neste scan.",
        )
    if infected < 5:
        return (
            "ATENÇÃO",
            "warn",
            f"Foram detectadas {infected} ameaça(s). Recomenda-se quarentena imediata "
            "e investigação da origem dos ficheiros afectados.",
        )
    return (
        "RISCO ELEVADO",
        "danger",
        f"Foram detectadas {infected} ameaças. Acção urgente: quarentena, "
        "verificação de outras máquinas na rede e revisão de pontos de entrada.",
    )


def _top_infected_dirs(results: Sequence[ScanResult], limit: int = 10) -> List[tuple[str, int]]:
    counter: Counter[str] = Counter()
    for r in results:
        if r.status != "infected":
            continue
        try:
            # as_posix() normaliza separadores → consistente entre Win/Unix
            parent = Path(r.file_path).parent.as_posix()
        except (TypeError, ValueError):
            parent = "(desconhecido)"
        counter[parent] += 1
    return counter.most_common(limit)


def _truncate(value: str, length: int) -> str:
    return value if len(value) <= length else value[: length - 1] + "…"


def _read_template(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, IOError) as e:
        logger.error(f"Erro ao ler template {path}: {e}")
        raise


class HTMLReportGenerator:
    """Gera relatórios HTML auto-contidos com gráficos Chart.js."""

    THREAT_TABLE = """
            <h2>⚠️ Ameaças Detectadas</h2>
            <table>
                <thead>
                    <tr>
                        <th>Ficheiro</th>
                        <th>Ameaça</th>
                        <th>Hash SHA256</th>
                    </tr>
                </thead>
                <tbody>
{rows}
                </tbody>
            </table>"""

    THREAT_ROW = (
        "                    <tr>\n"
        "                        <td>{file_path}</td>\n"
        "                        <td><span class=\"threat\">{reason}</span></td>\n"
        "                        <td><span class=\"hash\">{sha256}</span></td>\n"
        "                    </tr>"
    )

    SUMMARY_TABLE = """
            <h2>📊 Resumo Detalhado</h2>
            <table>
                <thead>
                    <tr>
                        <th>Ficheiro</th>
                        <th>Estado</th>
                        <th>Hash</th>
                    </tr>
                </thead>
                <tbody>
{rows}
                </tbody>
            </table>"""

    SUMMARY_ROW = (
        "                    <tr>\n"
        "                        <td>{file_path}</td>\n"
        "                        <td><span class=\"status {status_class}\">{status}</span></td>\n"
        "                        <td><span class=\"hash\">{sha256}</span></td>\n"
        "                    </tr>"
    )

    @classmethod
    def generate(
        cls,
        results: List[ScanResult],
        output_file: Path = Path("output/scan_report.html"),
        include_summary: bool = True,
        metadata: Optional[ReportMetadata] = None,
        summary_limit: int = 50,
    ) -> bool:
        """Gera relatório HTML. Retorna True se sucesso."""
        try:
            meta = metadata or ReportMetadata(finished_at=time.time())
            infected = [r for r in results if r.status == "infected"]
            clean = [r for r in results if r.status == "clean"]
            skipped = [r for r in results if r.status == "skip"]

            threat_section = ""
            if infected:
                rows = "\n".join(
                    cls.THREAT_ROW.format(
                        file_path=html.escape(_truncate(r.file_path, 90)),
                        reason=html.escape(r.reason or "(desconhecido)"),
                        sha256=html.escape(
                            (r.sha256[:32] + "…") if len(r.sha256) > 32 else (r.sha256 or "—")
                        ),
                    )
                    for r in infected
                )
                threat_section = cls.THREAT_TABLE.format(rows=rows)

            summary_section = ""
            if include_summary and results:
                shown = results[:summary_limit]
                rows = "\n".join(
                    cls.SUMMARY_ROW.format(
                        file_path=html.escape(_truncate(r.file_path, 90)),
                        status=html.escape(r.status.upper()),
                        status_class=html.escape(r.status),
                        sha256=html.escape((r.sha256[:24] + "…") if r.sha256 else "N/A"),
                    )
                    for r in shown
                )
                if len(results) > summary_limit:
                    extra = len(results) - summary_limit
                    rows += (
                        "\n                    <tr><td colspan='3' style='text-align:center;color:#999;'>"
                        f"+ {extra} resultados não listados (ver JSON/Excel)"
                        "</td></tr>"
                    )
                summary_section = cls.SUMMARY_TABLE.format(rows=rows)

            risk_label, risk_class, exec_summary = _classify_risk(len(infected), len(results))

            top_dirs = _top_infected_dirs(infected)
            dirs_data = {
                "labels": [_truncate(d, 40) for d, _ in top_dirs],
                "values": [n for _, n in top_dirs],
                "dataset_label": "Ameaças por diretório",
            }
            status_data = {
                "labels": ["Limpos", "Infectados", "Ignorados"],
                "values": [len(clean), len(infected), len(skipped)],
            }

            css = _read_template(CSS_TEMPLATE_PATH)
            template = Template(_read_template(HTML_TEMPLATE_PATH))

            html = template.safe_substitute(
                css=css,
                scan_date=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                scan_id=meta.scan_id,
                started_at=meta.started_iso,
                duration=_format_duration(meta.duration_seconds),
                scan_rate=f"{meta.scan_rate(len(results)):.1f} ficheiros/s",
                paths=" · ".join(meta.paths) if meta.paths else "(não especificado)",
                total=len(results),
                clean=len(clean),
                infected=len(infected),
                skipped=len(skipped),
                risk_class=risk_class,
                risk_label=risk_label,
                exec_summary=exec_summary,
                dirs_chart_title=(
                    "Top diretórios com ameaças" if top_dirs else "Diretórios afectados"
                ),
                threat_section=threat_section,
                summary_section=summary_section,
                status_data_json=json.dumps(status_data, ensure_ascii=False),
                dirs_data_json=json.dumps(dirs_data, ensure_ascii=False),
            )

            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(html, encoding="utf-8")
            logger.info(f"Relatório HTML gerado em {output_file}")
            return True
        except Exception as e:
            logger.error(f"Erro ao gerar relatório HTML: {e}")
            return False


def generate_json_report(
    results: List[ScanResult],
    output_file: Path = Path("output/scan_report.json"),
    metadata: Optional[ReportMetadata] = None,
) -> bool:
    """Gera relatório JSON. Inclui metadata e contagens se ``metadata`` fornecida."""
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)

        items = [
            {
                "file_path": r.file_path,
                "status": r.status,
                "reason": r.reason,
                "sha256": r.sha256,
            }
            for r in results
        ]

        if metadata is None:
            payload: object = items
        else:
            counts = Counter(r.status for r in results)
            payload = {
                "metadata": metadata.to_dict(),
                "counts": {
                    "total": len(results),
                    "clean": counts.get("clean", 0),
                    "infected": counts.get("infected", 0),
                    "skipped": counts.get("skip", 0),
                },
                "results": items,
            }

        with output_file.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        logger.info(f"Relatório JSON gerado em {output_file}")
        return True
    except (OSError, IOError, TypeError) as e:
        logger.error(f"Erro ao gerar relatório JSON: {e}")
        return False
