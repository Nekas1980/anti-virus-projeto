"""
Persistência leve de preferências do utilizador (paths recentes, opções da GUI).

Ficheiro JSON simples — atomicidade básica via escrita em ficheiro temporário.
"""
from __future__ import annotations

import json
import logging
import os
import tempfile
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

_DEFAULTS = {
    "recent_paths": [],
    "auto_quarantine": False,
    "notify_on_complete": True,
    "max_recent": 10,
}


class UserPrefs:
    """Preferências persistidas em JSON, com defaults seguros."""

    def __init__(self, prefs_file: Path):
        self.prefs_file = prefs_file
        self._data = dict(_DEFAULTS)
        self._load()

    def _load(self) -> None:
        if not self.prefs_file.exists():
            return
        try:
            with self.prefs_file.open("r", encoding="utf-8") as f:
                stored = json.load(f)
            if isinstance(stored, dict):
                self._data.update(stored)
        except (json.JSONDecodeError, IOError) as exc:
            logger.warning(f"Erro ao ler {self.prefs_file}, usando defaults: {exc}")

    def save(self) -> None:
        self.prefs_file.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(
            prefix=".prefs_", suffix=".tmp", dir=str(self.prefs_file.parent)
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
            os.replace(tmp, self.prefs_file)
        except OSError as exc:
            logger.error(f"Erro ao gravar prefs: {exc}")
            try:
                os.unlink(tmp)
            except OSError:
                pass

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def set(self, key: str, value) -> None:
        self._data[key] = value
        self.save()

    @property
    def recent_paths(self) -> List[str]:
        return list(self._data.get("recent_paths", []))

    def add_recent_path(self, path: str) -> None:
        recent = [p for p in self.recent_paths if p != path]
        recent.insert(0, path)
        max_recent = int(self._data.get("max_recent", 10))
        self._data["recent_paths"] = recent[:max_recent]
        self.save()
