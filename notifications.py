"""
Notificações desktop com fallback no-op.

Tenta `plyer.notification` (cross-platform). Se a dependência não estiver
instalada ou o backend falhar, regista no log e segue silenciosamente para
que o scanner nunca quebre por causa de notificações.
"""
from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)

APP_NAME = "Anti-Virus Projeto"


def notify(title: str, message: str, timeout: int = 8) -> bool:
    """Mostra notificação de sistema. Devolve True se entregue, False se ignorada."""
    try:
        from plyer import notification  # type: ignore
    except ImportError:
        logger.debug("plyer não instalado — notificação ignorada (%s)", title)
        return False

    try:
        notification.notify(
            title=title,
            message=message,
            app_name=APP_NAME,
            timeout=timeout,
        )
        return True
    except Exception as exc:
        logger.warning("Falha ao mostrar notificação: %s", exc)
        return False


def notify_scan_complete(infected: int, clean: int, skipped: int = 0) -> bool:
    """Notificação resumida no fim de um scan."""
    if infected > 0:
        title = f"⚠ {infected} ameaça(s) detectada(s)"
        message = f"Limpos: {clean} | Ignorados: {skipped}"
    else:
        title = "✓ Scan concluído sem ameaças"
        message = f"{clean} ficheiro(s) verificado(s)"
    return notify(title, message)


def notify_scan_started(total_paths: int) -> bool:
    return notify("🔍 Scan iniciado", f"A analisar {total_paths} caminho(s)…", timeout=4)
