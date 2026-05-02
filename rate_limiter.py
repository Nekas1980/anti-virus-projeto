"""
Rate limiter token-bucket simples + decorator de retry com backoff.

Usado pelo `virustotal_updater` para respeitar o limite gratuito de 4
requests/min e tolerar falhas transitórias de rede sem dependências
externas (sem `tenacity`/`backoff`).
"""
from __future__ import annotations

import functools
import logging
import random
import threading
import time
from typing import Callable, Tuple, Type, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RateLimiter:
    """Token bucket simples. Bloqueia chamadas para respeitar req/minuto."""

    def __init__(self, max_per_minute: int):
        if max_per_minute <= 0:
            raise ValueError("max_per_minute deve ser > 0")
        self.max_per_minute = max_per_minute
        self.min_interval = 60.0 / max_per_minute
        self._lock = threading.Lock()
        self._last_call = 0.0

    def acquire(self) -> None:
        """Bloqueia até ser seguro fazer a próxima chamada."""
        with self._lock:
            now = time.monotonic()
            wait = self.min_interval - (now - self._last_call)
            if wait > 0:
                logger.debug(f"Rate limit: aguardando {wait:.2f}s")
                time.sleep(wait)
            self._last_call = time.monotonic()

    def __enter__(self) -> "RateLimiter":
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exceptions: Tuple[Type[BaseException], ...] = (Exception,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator de retry com exponential backoff e jitter."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            attempt = 0
            while True:
                attempt += 1
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    if attempt >= max_attempts:
                        raise
                    delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                    delay += random.uniform(0, delay * 0.25)
                    logger.warning(
                        f"{func.__name__} falhou (tentativa {attempt}/{max_attempts}): "
                        f"{exc}. Retry em {delay:.2f}s"
                    )
                    time.sleep(delay)

        return wrapper

    return decorator
