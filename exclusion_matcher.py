"""
Matching otimizado de padrões de exclusão.

Pré-compila padrões fnmatch em regex uma única vez, evitando o custo
de `fnmatch.translate()` por cada chamada de `should_skip_path()` em
varreduras com milhares de ficheiros.
"""
from __future__ import annotations

import fnmatch
import re
from pathlib import Path
from typing import Iterable, List, Pattern


class ExclusionMatcher:
    """Cacheia padrões fnmatch em regex compilado para matching rápido."""

    def __init__(self, patterns: Iterable[str]):
        self._patterns: List[str] = list(patterns)
        self._path_regexes: List[Pattern[str]] = []
        self._compile()

    def _compile(self) -> None:
        for pattern in self._patterns:
            # Normaliza separadores para matching cross-platform
            p = pattern.replace("\\", "/")
            
            # Para que padrões como 'node_modules' apanhem o diretório em qualquer parte do path
            # (ex: /project/node_modules/foo), envolvemos em * se não for absoluto.
            if not p.startswith(("/", "*")):
                p = f"*{p}"
            if not p.endswith("*"):
                p = f"{p}*"
            
            regex = re.compile(fnmatch.translate(p), re.IGNORECASE)
            self._path_regexes.append(regex)

    def matches(self, path: Path) -> bool:
        """Retorna True se o caminho corresponde a algum padrão de exclusão."""
        path_str = str(path).replace("\\", "/")

        for path_re in self._path_regexes:
            if path_re.match(path_str):
                return True
        return False

    @property
    def patterns(self) -> List[str]:
        return list(self._patterns)

    def __len__(self) -> int:
        return len(self._patterns)
