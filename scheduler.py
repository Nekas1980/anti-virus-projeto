#!/usr/bin/env python3
"""
Antivírus Scheduler

Executa varreduras agendadas em intervalos regulares.
Pode correr como serviço de background.
"""

import json
import logging
import os
import signal
import time
from datetime import datetime
from pathlib import Path
from typing import Dict

from config import PATHS, SCAN
from hash_cache import HashCache
from notifications import notify_scan_complete
from scan_history import ScanHistory
from Virus_project import (
    load_exclusions,
    load_signatures,
    quarantine_file,
    save_report,
    scan_directory,
)

SCHEDULE_CONFIG = str(PATHS["schedule_config"])
SCHEDULE_LOG = "schedule.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(SCHEDULE_LOG),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ScanScheduler:
    """Gerenciador de varreduras agendadas."""

    def __init__(self, config_file: Path = Path(SCHEDULE_CONFIG)):
        self.config_file = config_file
        self.running = False
        self.config = self._load_config()
        self.cache = HashCache(PATHS["scan_cache"]) if SCAN["cache_enabled"] else None
        self.history = ScanHistory(PATHS["scan_history"])
        signal.signal(signal.SIGINT, self._handle_shutdown)

    def close(self) -> None:
        if self.cache is not None:
            self.cache.close()
            self.cache = None
        self.history.close()

    def _load_config(self) -> Dict:
        """Carrega configuração do scheduler."""
        if not self.config_file.exists():
            return self._get_default_config()
        try:
            with self.config_file.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Erro ao carregar config, usando padrão: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """Retorna configuração padrão."""
        return {
            "enabled": True,
            "intervals": [
                {
                    "name": "daily_morning",
                    "hour": 9,
                    "minute": 0,
                    "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
                    "paths": [os.path.expanduser("~/Downloads"), os.path.expanduser("~/Desktop")],
                    "auto_quarantine": False,
                }
            ],
            "auto_quarantine": False,
            "keep_logs": 30,
            "report_dir": "scheduled_reports",
        }

    def _save_config(self) -> bool:
        """Salva configuração."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with self.config_file.open("w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info("Configuração salva")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar configuração: {e}")
            return False

    def _handle_shutdown(self, signum, frame):
        """Tratamento de shutdown gracioso."""
        logger.info("Recebido sinal de encerramento...")
        self.running = False

    def _should_run_now(self, interval: Dict) -> bool:
        """Verifica se um intervalo deve ser executado agora."""
        now = datetime.now()
        schedule_time = now.replace(hour=interval["hour"], minute=interval["minute"], second=0)

        if "days" in interval:
            day_name = now.strftime("%a")
            if day_name not in interval["days"]:
                return False

        time_until = abs((now - schedule_time).total_seconds())
        return time_until < 60

    def _run_scan(self, interval: Dict) -> None:
        """Executa uma varredura individual."""
        logger.info(f"Iniciando scan agendado: {interval.get('name', 'unnamed')}")
        started_at = time.time()

        signatures = load_signatures(PATHS["signatures"])
        exclusions = load_exclusions(PATHS["exclusions"])

        paths = [Path(p) for p in interval.get("paths", [])]
        paths = [p for p in paths if p.exists()]

        if not paths:
            logger.warning("Nenhum caminho válido para escanear")
            return

        results = []
        for path in paths:
            logger.info(f"Escaneando: {path}")
            results.extend(scan_directory(path, signatures, exclusions, cache=self.cache))

        infected = [r for r in results if r.status == "infected"]
        clean = [r for r in results if r.status == "clean"]
        skipped = [r for r in results if r.status == "skip"]

        logger.info(
            f"Scan concluído: {len(clean)} limpos, {len(infected)} infectados, {len(skipped)} ignorados"
        )

        report_dir = Path(interval.get("report_dir", "scheduled_reports"))
        report_file = report_dir / f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_report(results, report_file)

        self.history.record(
            paths=paths,
            total=len(results),
            clean=len(clean),
            infected=len(infected),
            skipped=len(skipped),
            started_at=started_at,
            report_path=report_file,
        )

        if self.config.get("notify_on_complete", True):
            notify_scan_complete(len(infected), len(clean), len(skipped))

        if infected and (interval.get("auto_quarantine") or self.config.get("auto_quarantine")):
            logger.info(f"Movendo {len(infected)} arquivo(s) para quarentena")
            for result in infected:
                quarantine_file(Path(result.file_path), PATHS["quarantine_dir"])

    def run(self) -> None:
        """Executa o scheduler em loop."""
        if not self.config.get("enabled"):
            logger.warning("Scheduler desabilitado na configuração")
            return

        self.running = True
        logger.info("=== Antivírus Scheduler Iniciado ===")

        try:
            while self.running:
                try:
                    for interval in self.config.get("intervals", []):
                        if self._should_run_now(interval):
                            self._run_scan(interval)
                    time.sleep(30)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(f"Erro no scheduler: {e}")
                    time.sleep(60)
        finally:
            self.close()

        logger.info("=== Antivírus Scheduler Encerrado ===")

    @staticmethod
    def create_schedule_config(output_file: Path = Path(SCHEDULE_CONFIG)) -> bool:
        """Cria arquivo de configuração de exemplo."""
        scheduler = ScanScheduler.__new__(ScanScheduler)
        scheduler.config = scheduler._get_default_config()
        scheduler.config_file = output_file
        return scheduler._save_config()


def main() -> None:
    """Interface CLI para o scheduler."""
    import sys

    if len(sys.argv) < 2:
        print("Uso: python scheduler.py [create-config|run]")
        print("")
        print("Comandos:")
        print("  create-config  - Cria arquivo de configuração de exemplo")
        print("  run            - Executa o scheduler em background")
        return

    command = sys.argv[1]

    if command == "create-config":
        if ScanScheduler.create_schedule_config():
            print(f"✓ Configuração criada em {SCHEDULE_CONFIG}")
            print("  Edite o arquivo para personalizadores horários e caminhos")
        else:
            print("✗ Erro ao criar configuração")

    elif command == "run":
        scheduler = ScanScheduler()
        scheduler.run()

    else:
        print(f"Comando desconhecido: {command}")


if __name__ == "__main__":
    main()
