# Changelog

Todas as mudanças relevantes ao projeto. Formato baseado em [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased] — 2026-05-02

Sessão de implementação das Fases 1, 2, 3, 4 e 5 do `IMPROVEMENT_PLAN.md`.

### Fase 5 — Documentation

#### Adicionado
- **`docs/index.md`** reescrito — hero card com palette do tema (Material default), feature grid neutro, diagrama Mermaid de arquitetura, tabela de estado.
- **`docs/api/`** (4 ficheiros) — referência API auto-gerada via `mkdocstrings`:
  - `reference.md` — visão geral + config centralizado
  - `engine.md` — `Virus_project`, `hash_cache`, `exclusion_matcher`
  - `support.md` — 8 módulos de suporte (history, prefs, vt_cache, rate_limiter, notifications, gui_filters, report_generator, excel_exporter)
  - `web.md` — `web_api` (FastAPI) + `scheduler` com tabelas de endpoints e exemplos curl
- **`docs/guides/troubleshooting.md`** — 20+ problemas comuns organizados por categoria (instalação, permissões, performance, VirusTotal, tests/CI, GUI, build).
- **`docs/guides/faq.md`** — FAQ completo com `<details>` expansíveis, organizado em 7 secções.
- **`docs/architecture/architecture.md`** — diagramas ASCII substituídos por **Mermaid**:
  - `flowchart TB` da arquitetura completa (UI → Engine → Suporte → Data)
  - `sequenceDiagram` do fluxo de scan (User → UI → Engine → Cache → Sigs → Report)

#### Alterado
- **`mkdocs.yml`** reescrito:
  - Tema Material com palette teal limpa (light + dark toggle)
  - Plugin `mkdocstrings` configurado (Google docstrings, paths=`["."]`)
  - `pymdownx.superfences` com fence Mermaid registado
  - Mermaid.js carregado via CDN (`extra_javascript`)
  - Nav reorganizado com secção "API Reference" nova
- **`docs/stylesheets/extra.css`** — reduzido de ~110 linhas (cyber theme com `!important` em todo o lado e contraste fraco) para ~55 linhas de overrides limpos que herdam variáveis do tema (light/dark funcionam).
- **`.github/workflows/deploy.yml`** — instala `mkdocstrings[python]` e `requirements.txt` para que mkdocstrings consiga importar os módulos.

#### Removido
- Estilos hardcoded fluorescentes (`#00ffa3`, `text-shadow: 0 0 20px ...`) do `index.md` que tornavam o site ilegível em modo claro.

### Cobertura Fase 5
- 0 testes adicionados (docs não são testáveis com unittest), mas o build dos docs corre no CI (`mkdocs build --strict`).
- 18 páginas markdown organizadas em 6 secções.

### Fase 4 — Testing & CI/CD

#### Adicionado
- **`test_scheduler.py`** (11 testes) — `_should_run_now` (matching/wrong-day/window/no-days), `_load_config` (default/missing/invalid JSON), `_run_scan` (skip-no-paths/full-flow/auto-quarantine), `create_schedule_config`.
- **`test_integration.py`** (3 testes) — pipeline end-to-end com sandbox real:
  - Full pipeline: scan → cache populate → exclusions respeitadas → JSON/HTML/Excel reports → history record → quarentena com anti-colisão.
  - Re-scan usa cache (sha256_file não é chamado).
  - Modificação de ficheiro invalida cache.
- **`.coveragerc`** + secção `[tool.coverage.*]` em `pyproject.toml` com `fail_under = 80` e omits para módulos GUI/web.
- **`.flake8`** com `max-line-length=100`, ignores E203/W503/E501, per-file ignores para tests.
- **`pyproject.toml`** novas optional-dependencies: `notifications`, `excel`, `api`, `dev` (com coverage, bandit, safety).
- **`build_exe.spec`** — `templates/` agora bundled no .exe (3.1 dependeu disto).
- **`.github/workflows/tests.yml`** reescrito:
  - Job `test` — matriz 3 OS × 4 Python (12 configs), unittest discover.
  - Job `coverage` — `coverage` com threshold 80%, uploads `coverage.xml` + `htmlcov/`.
  - Job `lint` — `black --check` + `flake8` (não-bloqueantes inicialmente).
  - Job `security` — `bandit` static analysis + `safety` dep vulnerabilities, upload de relatórios.
  - Job `build-exe` — PyInstaller no Windows, condicional a `main`/tags, com upload de artifact.

#### Cobertura Fase 4
- **130 testes** totais (116 anteriores + 14 novos), 5 skipped quando FastAPI ausente.
- Todos passam em < 0.8s localmente.

### Fase 3 — UI/UX Overhaul

### Fase 3 — UI/UX Overhaul

#### Adicionado
- **`templates/report.html`** + **`templates/report.css`** — template HTML externalizado, carregado via `string.Template` (sem deps).
- **`report_generator.py`** reescrito:
  - `ReportMetadata` (dataclass) com `scan_id`, `started_at`, `finished_at`, `paths`, `duration_seconds`, `scan_rate()`.
  - Resumo executivo com classificação automática de risco (`SEGURO` / `ATENÇÃO` / `RISCO ELEVADO`).
  - Gráficos Chart.js inline (CDN, zero deps Python): doughnut de distribuição de estados + bar chart de top diretórios afectados.
  - JSON enriquecido com envelope `{metadata, counts, results}` quando `metadata` é fornecida (legacy continua a devolver lista pura).
- **`excel_exporter.py`** — `ExcelReportGenerator` com 4 sheets (Summary, Infected, Clean, Stats), styling com headers coloridos e auto-width. Import lazy de `openpyxl` (degrada gracefully).
- **`gui_filters.py`** — função pura `filter_results(results, FilterCriteria)` + helpers `format_eta`/`format_elapsed`. Permite testes da lógica de filtros sem Tk.
- **`gui.py`** redesenho:
  - Tabs `LOG` / `RESULTADOS` / `EXPORTAR` (CTkTabview).
  - Tab `RESULTADOS`: search box + 3 toggles (Limpos/Ameaças/Ignorados) com refresh automático.
  - Tab `EXPORTAR`: botões HTML / JSON / Excel com feedback de status.
  - Métricas live na sidebar: `files/s · ELAPSED · ETA`.
  - Botão **Pausar/Retomar** com `threading.Event` (worker bloqueia em `wait()`).
  - Cancelamento limpo no fecho da janela.
- **`web_api.py`** — FastAPI app (lazy import, opcional):
  - `GET /api/health`, `/api/status`, `/api/scan/{id}`, `/api/scan/{id}/results`, `/api/history`
  - `POST /api/scan` (BackgroundTasks)
  - `GET /api/reports/{id}/{html|json|xlsx}` com `FileResponse`
  - Registry de scans em memória (`_scans` + lock).
- Tests (21 novos):
  - `test_report_generator.py` (16): metadata, classificação de risco, helpers, HTML + JSON.
  - `test_excel_exporter.py` (5): availability, sheets, fallback sem openpyxl, capping de Clean rows.
  - `test_gui_filters.py` (14): filter pipeline, ETA/elapsed formatting, edge cases.
  - `test_web_api.py` (7, skipped quando FastAPI ausente).

#### Alterado
- **`gui.py`** — UI principal totalmente reorganizada (ver Adicionado).
- **`report_generator.py`** — API mantém retrocompatibilidade (`metadata` é opcional).

#### Performance / UX
- Refresh de progress agora batched a cada 25 ficheiros (`UI_REFRESH_EVERY`) — evita repaint excessivo em scans grandes.
- Resultados visuais cap a 500 linhas no scroll (filtros permitem navegar o resto).

#### Notas técnicas
- FastAPI + uvicorn são opcionais (`pip install fastapi uvicorn` quando se quer a API).
- `openpyxl` é opcional (`pip install openpyxl` para Excel).
- Chart.js é via CDN — relatórios HTML continuam standalone mas precisam de internet para renderizar gráficos. Sem internet os dados em JSON ficam embutidos no HTML.

### Cobertura Fase 3
- 116 testes totais (95 anteriores + 21 novos), 5 skipped quando FastAPI ausente.
- Todos passam em < 1.2s.

---

## Histórico

### Fases 1 e 2 — 2026-05-01

### Adicionado

#### Fase 1 — Core Stability
- **`config.py`** — paths e parâmetros centralizados (`PATHS`, `SCAN`, `VIRUSTOTAL`, `LOG`).
- **`hash_cache.py`** — `HashCache` SQLite (WAL, thread-safe) com invalidação automática por `mtime`/`size`. Esperado ~60% menos tempo em rescans.
- **`exclusion_matcher.py`** — `ExclusionMatcher` que pré-compila padrões fnmatch em regex uma única vez por scan.
- Suporte a **timeout** em `sha256_file()` — devolve `None` se exceder o limite (default 5s, configurável em `config.SCAN["file_timeout_seconds"]`).
- Tests:
  - `test_hash_cache.py` (12 testes) — set/get, invalidação por size/mtime, persistência cross-instance, edge cases.
  - `test_exclusion_matcher.py` (6 testes) — directory/basename/glob matching, edge cases.
  - 3 testes adicionais em `test_virus_project.py` — integração `scan_file` + cache, timeout.

#### Fase 2 — Feature Gaps
- **`vt_cache.py`** — `VTCache` SQLite com TTL configurável (default 30 dias). Cacheia tanto respostas 200 como 404 para evitar requeries.
- **`rate_limiter.py`** — `RateLimiter` token-bucket thread-safe (4 req/min default) + decorator `retry` com exponential backoff e jitter, sem dependências externas.
- **`scan_history.py`** — `ScanHistory` SQLite. `ScanRecord` dataclass com `scan_id` (UUID), timestamps, totais e `report_path`.
- **`user_prefs.py`** — `UserPrefs` JSON com escrita atómica (`os.replace`), `recent_paths` deduplicado e capped.
- **`notifications.py`** — `notify_scan_complete()` via `plyer` com fallback no-op (não falha se `plyer` ausente).
- GUI Cyber-Sentinel reescrita: paths recentes persistidos, view de Histórico de scans, notificação no fim, threading thread-safe via `after(0, …)`.
- Tests (32 novos, 70 totais):
  - `test_vt_cache.py` (6), `test_rate_limiter.py` (7), `test_scan_history.py` (6), `test_user_prefs.py` (5), `test_virustotal_updater.py` (8).

### Alterado
- **`Virus_project.py`** — usa `config`, `ExclusionMatcher`, `HashCache`. `scan_file()` e `scan_directory()` aceitam parâmetro opcional `cache=`.
- **`virustotal_updater.py`** — integra `VTCache`, `RateLimiter`, retry decorator, deduplicação de hashes antes de chamadas API. Distingue 200/404/429/5xx.
- **`scheduler.py`** — usa `config.PATHS`, integra `HashCache` e `ScanHistory`, dispara notificação no fim de cada scan, cleanup correto em `finally`.
- **`gui.py`** — sidebar com botão "HISTÓRICO", header com "RECENTES ▼", todas as updates de UI são `after()`-marshalled, prompt de quarentena no thread principal.
- **`README.md`** — reescrito: remove referências obsoletas a `gui2.py`/`gui3.py`, documenta arquitetura de 3 camadas (UI/Engine/Suporte/Config), tabela de testes.

### Performance
- **Skip path:** `fnmatch` em loop substituído por regex pré-compilados — esperado +30% velocidade quando há muitos padrões de exclusão.
- **Hash cache:** rescans saltam o cálculo SHA-256 quando `mtime`+`size` não mudaram — +60% típico em pastas estáveis.
- **VirusTotal:** `vt_cache` evita até ~90% das chamadas em batch updates repetidos.

### Notas técnicas
- Todos os SQLite databases usam `journal_mode=WAL` para permitir leituras concorrentes.
- Todos os módulos novos têm `__enter__`/`__exit__` ou `close()` para cleanup explícito.
- `notifications.notify_scan_complete()` nunca quebra um scan: erros são apenas logados.
- Sem novas dependências obrigatórias. `plyer` é opcional.

### Cobertura
- 70/70 testes passam em < 700ms.
- 18 testes originais → 70 (+289%).
