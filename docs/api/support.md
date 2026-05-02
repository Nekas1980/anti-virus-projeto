# Suporte — Persistência, Reports, UX

Módulos auxiliares: histórico, preferências, cache de VT, rate limiting, geração de relatórios e helpers da GUI.

---

## `scan_history`

Histórico persistente de scans (SQLite). Cada execução grava uma linha com totais, duração e referência ao relatório.

::: scan_history
    options:
      members:
        - ScanRecord
        - ScanHistory

---

## `user_prefs`

Preferências em JSON com escrita atómica (`os.replace`). Mantém uma lista de paths recentes deduplicada e capped.

::: user_prefs
    options:
      members:
        - UserPrefs

---

## `vt_cache`

Cache SQLite das respostas VirusTotal com TTL configurável (default 30 dias). Cacheia tanto 200 como 404 para evitar requeries.

::: vt_cache
    options:
      members:
        - VTCache

---

## `rate_limiter`

Token-bucket thread-safe + decorator `retry()` com exponential backoff e jitter — sem dependências externas.

::: rate_limiter
    options:
      members:
        - RateLimiter
        - retry

---

## `notifications`

Camada fina sobre `plyer` para notificações desktop. Falha gracefully quando `plyer` não está instalado.

::: notifications
    options:
      members:
        - notify_scan_complete

---

## `gui_filters`

Função pura `filter_results()` + helpers ETA/elapsed. Separados da GUI para permitir testes sem Tk.

::: gui_filters
    options:
      members:
        - FilterCriteria
        - filter_results
        - format_eta
        - format_elapsed

---

## `report_generator`

Geração de HTML (com Chart.js) e JSON. Templates externos em `templates/report.{html,css}`.

::: report_generator
    options:
      members:
        - ReportMetadata
        - HTMLReportGenerator
        - generate_json_report

---

## `excel_exporter`

Exportação `.xlsx` multi-sheet (Summary, Infected, Clean, Stats) via `openpyxl` (lazy import).

::: excel_exporter
    options:
      members:
        - ExcelReportGenerator
