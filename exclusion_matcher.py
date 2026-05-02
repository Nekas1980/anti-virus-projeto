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
        self._name_regexes: List[Pattern[str]] = []
        self._compile()

    def _compile(self) -> None:
        for pattern in self._patterns:
            path_pattern = fnmatch.translate(f"*{pattern}*")
            name_pattern = fnmatch.translate(pattern)
            self._path_regexes.append(re.compile(path_pattern))
            self._name_regexes.append(re.compile(name_pattern))

    def matches(self, path: Path) -> bool:
        """Retorna True se o caminho corresponde a algum padrão de exclusão."""
        path_str = str(path)
        name = path.name
        for path_re, name_re in zip(self._path_regexes, self._name_regexes):
            if path_re.match(path_str) or name_re.match(name):
                return True
        return False

    @property
    def patterns(self) -> List[str]:
        return list(self._patterns)

    def __len__(self) -> int:
        return len(self._patterns)
