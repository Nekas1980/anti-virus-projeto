# 🔍 Anti-Virus Projeto — Plano Completo de Melhorias

**Data de Análise**: 2026-04-27  
**Analisador**: Claude Code (Haiku 4.5)  
**Status**: Fases 1, 2, 3, 4 e 5 implementadas (2026-05-02) — **plano de melhorias 100% concluído**. Ver `CHANGELOG.md`.

## ✅ Estado de Implementação

| Fase | Estado | Notas |
|------|--------|-------|
| **1 — Core Stability** | ✅ Concluída (2026-05-01) | `config.py`, `hash_cache.py`, `exclusion_matcher.py`, timeout em `sha256_file` |
| **2 — Feature Gaps**   | ✅ Concluída (2026-05-01) | `vt_cache.py`, `rate_limiter.py`, `scan_history.py`, `user_prefs.py`, `notifications.py`, GUI refactorada |
| **3 — UI/UX Overhaul** | ✅ Concluída (2026-05-01) | `report_generator` refactored com Chart.js + templates externos; `excel_exporter`; GUI tabs+filtros+pause/resume+métricas live; `web_api` FastAPI (opcional). Web Dashboard Vue **deferido** (educacional vs full-stack). |
| **4 — Testing & CI/CD**| ✅ Concluída (2026-05-02) | 130 testes (5 skipped); `test_scheduler.py` + `test_integration.py`; `.coveragerc` + `.flake8`; CI workflow reescrito com 5 jobs (test matrix, coverage 80%, lint, security bandit/safety, build .exe condicional) |
| **5 — Documentation**  | ✅ Concluída (2026-05-02) | Tema Material limpo (palette teal); `mkdocstrings` em 4 páginas API; diagramas Mermaid (flowchart + sequence); troubleshooting guide (20+ problemas); FAQ completo |



---

## 📋 Sumário Executivo

Análise exhaustiva do codebase com identificação de problemas em 5 áreas:
- ❌ **Backend**: Performance, caching, APIs
- ❌ **Frontend**: UX, histórico, customização
- ⚠️ **Infrastructure**: Tests incompletos, CI/CD gaps
- ⚠️ **Data Layer**: Sem metadata, sem versionamento
- ✅ **Core**: Solid foundation, bom architecture

**Total**: 230 horas de trabalho em 5 fases (~3 meses part-time).

---

## 🔴 BACKEND — Scanning Engine & Services

### 1. Virus_project.py (Scanning Engine)

**Problemas Identificados:**

| Problema | Severidade | Descrição | Solução |
|----------|-----------|-----------|---------|
| Sem timeout ficheiros grandes | 🔴 Critical | `scan_directory()` usa `rglob()` sem limite — pode emperrar em pastas gigantes | Adicionar timeout de 5s/10MB |
| Sem hash cache | 🟠 High | Recomputa SHA256 sempre mesmo para ficheiros idênticos | Cache em disco (MD5 path+size → SHA256) |
| `should_skip_path()` ineficiente | 🟡 Medium | Fnmatch em loop — lento com 20+ patterns | Compilar regex uma vez, cache |
| Sem modo incremental | 🟡 Medium | Rescans re-processam tudo | Tracking de ficheiros já scanned |
| Sem detecção de ficheiros movidos | 🟢 Low | Se ficheiro muda de path, visto como novo | Use inode (Unix) ou FileID (Windows) |

**Plano de Ação (FASE 1):**

1. **1.1 Hash Cache** (Prioridade: MÁXIMA)
   - Ficheiro: `.scan_cache.db` (SQLite)
   - Schema: `(file_path_hash, file_size, sha256, timestamp)`
   - Invalida se: `mtime` ou `size` mudou
   - Estimado: +60% performance em rescans
   - Esforço: **Baixo** (2-3 horas)

2. **1.2 Optimize `should_skip_path()`**
   - Pré-compilar patterns em regex (sem fnmatch loop)
   - Cache na classe (não recompile cada chamada)
   - Estimado: +30% skip speed
   - Esforço: **Baixo** (1 hora)

3. **1.3 Add Timeout para ficheiros grandes**
   - `timeout=5s` por ficheiro
   - Se timeout, skip com status `"timeout"`
   - Evita freezes em ficheiros corrupos ou gigantes
   - Esforço: **Médio** (2-3 horas)

4. **1.4 Incremental Scanning**
   - Flag `--incremental` na CLI
   - Usa cache + last_scan_time
   - Só rescans ficheiros novos/modificados
   - Esforço: **Médio** (3-4 horas)

---

### 2. scheduler.py (Scheduled Scans)

**Problemas Identificados:**

| Problema | Severidade | Descrição | Solução |
|----------|-----------|-----------|---------|
| Polling a 30s | 🟠 High | Ineficiente, consome CPU | Use APScheduler ou system cron |
| Sem persistência | 🔴 Critical | Se cair, perde histórico e state | DB com metadata scans |
| Sem notificações | 🟠 High | User não sabe se detectou ameaças | Desktop alerts + email opt-in |
| Config sem validação | 🟡 Medium | JSON puro, sem schema | Use Pydantic |
| Sem retry logic | 🟡 Medium | Se scan falha parcialmente, perde dados | Implement exponential backoff |

**Plano de Ação (FASE 2):**

1. **2.1 Substituir polling por APScheduler**
   - Dependency: `pip install apscheduler`
   - Mais eficiente (event-driven vs polling)
   - Suporta cron expressions
   - Esforço: **Médio** (3-4 horas)

2. **2.2 Adicionar schema validation com Pydantic**
   - Define `ScheduleConfig` model
   - Valida ao carregar
   - Mensagens de erro claras
   - Esforço: **Baixo** (2 horas)

3. **2.3 Persistência de scans**
   - DB: `scans_history.db`
   - Armazena: `(scan_id, timestamp, paths, results_count, infected_count, status)`
   - Permite UI mostrar histórico
   - Esforço: **Médio** (3 horas)

4. **2.4 Sistema de notificações**
   - Desktop alerts: `plyer` library
   - Email (opcional): SendGrid ou SMTP
   - Config em `schedule_config.json`
   - Esforço: **Médio** (4 horas)

---

### 3. virustotal_updater.py (VirusTotal Integration)

**Problemas Identificados:**

| Problema | Severidade | Descrição | Solução |
|----------|-----------|-----------|---------|
| Sem rate limiting | 🔴 Critical | Pode bater limites API (4 requests/min free) | Add exponential backoff + queue |
| Sem cache | 🔴 Critical | Requer API para o mesmo hash 2x | SQLite local cache |
| Sem batch mode | 🟠 High | 1 request per hash (ineficiente) | Usar VirusTotal v3 batch API |
| Sem deduplicação | 🟡 Medium | Ficheiro idêntico com 2 nomes = 2 queries | Hash dedup antes de API call |
| Sem tratamento de erros | 🟡 Medium | API flakes não retry | Implement retry + fallback |

**Plano de Ação (FASE 2):**

1. **2.1 SQLite Cache local**
   - Ficheiro: `vt_cache.db`
   - Schema: `(file_hash, vt_response, cached_at, expires_at)`
   - TTL: 30 dias
   - Estimado: -90% API calls
   - Esforço: **Médio** (3-4 horas)

2. **2.2 Rate Limiting + Retry Logic**
   - Use `backoff` library (exponential backoff)
   - Max 4 requests/min (free tier)
   - Retry com jitter
   - Esforço: **Médio** (3 horas)

3. **2.3 Batch API mode (opcional)**
   - VirusTotal v3 suporta batch de 40 hashes/request
   - Requer Premium, mas economiza API calls
   - Can implement como fallback
   - Esforço: **Alto** (5+ horas)

4. **2.4 Deduplicação**
   - Set de hashes antes de API calls
   - Log duplicates encontrados
   - Esforço: **Baixo** (1 hora)

---

### 4. report_generator.py (Reports)

**Problemas Identificados:**

| Problema | Severidade | Descrição | Solução |
|----------|-----------|-----------|---------|
| HTML template é gigante | 🟡 Medium | CSS inline + HTML bundled | Separar em ficheiro `.html` template |
| Sem gráficos | 🟡 Medium | Só tabelas de texto | Add matplotlib/plotly charts |
| Sem exportação | 🟡 Medium | Só HTML/JSON, sem Excel/PDF | Add `openpyxl` + `reportlab` |
| Sem timestamp | 🟠 High | Difícil rastrear quando scan correu | Add datetime em metadata |
| Sem resumo executivo | 🟡 Medium | Straight to tables, sem summary | Add 1-page exec summary |

**Plano de Ação (FASE 3):**

1. **3.1 Refactor HTML Template**
   - Move CSS para `templates/report.css`
   - Move template para `templates/report.html`
   - Use Jinja2 para rendering
   - Esforço: **Baixo** (2 horas)

2. **3.2 Add Gráficos**
   - Pie chart: Clean vs Infected vs Skipped
   - Bar chart: Top directories com mais threats
   - Timeline: Threats over time (se histórico)
   - Tools: `matplotlib` ou `plotly` (HTML export)
   - Esforço: **Médio** (4 horas)

3. **3.3 Exportação Excel**
   - Dependency: `openpyxl`
   - Formatação: Headers, colors, auto-width
   - Sheets: Summary, Infected, Clean, Stats
   - Esforço: **Médio** (3 horas)

4. **3.4 Add Timestamp & Metadata**
   - Report header: `Generated: 2026-04-27 14:30:45`
   - Summary: Duration, files scanned rate
   - Esforço: **Baixo** (1 hora)

---

### 5. Dependencies & General

**Problemas Identificados:**

| Problema | Severidade | Descrição | Solução |
|----------|-----------|-----------|---------|
| `requests` é pesado | 🟡 Medium | Só para VirusTotal API | Alternativa: `urllib3` ou `httpx` |
| Sem retry em APIs | 🔴 Critical | Network flaky não retry | Implement universal retry wrapper |
| Tightly coupled | 🟡 Medium | Functions importam tudo entre si | Refactor para dependency injection |
| Sem config centralized | 🟡 Medium | Paths hardcoded em vários ficheiros | Central `config.py` |

**Plano de Ação:**

1. **Add `config.py` centralized**
   ```python
   # config.py
   PATHS = {
       "signatures": Path("signatures.json"),
       "exclusions": Path("exclusions.json"),
       "cache": Path(".scan_cache.db"),
   }
   ```
   - Esforço: **Baixo** (1 hora)

2. **Universal Retry Wrapper**
   - Function decorator: `@retry(max_attempts=3, backoff=exponential)`
   - Usa `tenacity` library ou custom
   - Esforço: **Médio** (2 horas)

---

## 🔴 FRONTEND — GUI & Web Interface

### 1. gui.py (CustomTkinter - CyberSentinel)

**Problemas Identificados:**

| Problema | Severidade | Descrição | Solução |
|----------|-----------|-----------|---------|
| Hardcoded scan paths | 🔴 Critical | Só scans `~/Downloads`, `~/Desktop`, `~/Documents` | Add folder picker dialog |
| Sem histórico | 🟠 High | Cada scan é isolado | Persist results em DB |
| Sem filtros/search | 🟡 Medium | Mostra todos os resultados sem opções | Add search box + sort by name/date |
| Threading sem pool | 🟡 Medium | Cria thread nova cada scan | Use `ThreadPoolExecutor` |
| Sem pause/resume | 🟡 Medium | Não pode pausar scan longo | Flag + thread signaling |
| Sem notificações | 🟠 High | User não sabe quando scan acaba | Desktop toast notifications |

**Plano de Ação (FASE 2 + 3):**

1. **2.4 Customizable Scan Paths**
   - Button "Selecionar Pastas"
   - `tkinter.filedialog.askdirectory()`
   - Armazena em config (reuse próxima vez)
   - Esforço: **Baixo** (2 horas)

2. **2.3 Histórico de Scans**
   - Nova tab: "Histórico"
   - Lista de scans com timestamp + resultado
   - Click para ver detalhes (infected files)
   - Esforço: **Médio** (4 horas)

3. **3.2 Filtros + Search**
   - Search box: Filter infected by filename/path
   - Buttons: "Mostrar Apenas Infectados", "Show Skipped"
   - Sort by: Name, Date, Size
   - Esforço: **Médio** (3 horas)

4. **2.5 Thread Pool + Pause/Resume**
   - Use `concurrent.futures.ThreadPoolExecutor`
   - Flag: `scanning = False` → stop
   - Button: "Pausar" ↔ "Retomar"
   - Esforço: **Médio** (3 horas)

5. **2.6 Desktop Notifications**
   - `plyer.notification.notify()` quando scan acaba
   - Mostra: "{X} infectados encontrados"
   - Esforço: **Baixo** (2 horas)

6. **3.2 Detalhes visuais**
   - Add progress % (não só bar)
   - Show scan speed: X files/sec
   - List de arquivos em tempo real (live update)
   - Esforço: **Médio** (3 horas)

---

### 2. index.html (Web Landing Page)

**Problemas Identificados:**

| Problema | Severidade | Descrição | Solução |
|----------|-----------|-----------|---------|
| Página estática | 🔴 Critical | Não se conecta à app | Build Web API + Dashboard |
| Sem way trigger scans | 🔴 Critical | Não consegue fazer nada | REST API + Web UI |
| Sem real-time status | 🟠 High | Sem WebSocket para live updates | WebSocket ou Server-Sent Events |

**Plano de Ação (FASE 3):**

1. **3.3 Web API (FastAPI)**
   - Endpoints:
     - `GET /api/status` → `{scanning, progress, current_file}`
     - `POST /api/scan` → `{paths}` → retorna scan_id
     - `GET /api/scan/{id}/results` → resultados
     - `GET /api/history` → lista de scans
   - Esforço: **Médio** (5 horas)

2. **3.4 Web Dashboard (Vue 3)**
   - Frontend: Vue 3 app
   - Pages:
     - Dashboard: Live scan progress
     - Results: Filterable list de infected files
     - History: Past scans
   - Esforço: **Alto** (8-10 horas)

3. **3.5 WebSocket live updates**
   - Progress updates em real-time
   - Results stream conforme encontra
   - Esforço: **Médio** (4 horas)

---

### 3. main.py

✅ **OK** — Simples e claro, sem problemas.

---

## ⚠️ INFRASTRUCTURE — Tests, CI/CD, Packaging

### 1. test_virus_project.py

**Problemas Identificados:**

| Problema | Severidade | Descrição | Solução |
|----------|-----------|-----------|---------|
| Sem testes scheduler | 🔴 Critical | `scheduler.py` não tem testes | Mock config + test scheduling logic |
| Sem testes VirusTotal | 🟠 High | `virustotal_updater.py` não testado | Mock API responses |
| Sem integration tests | 🟠 High | Só unit tests, sem end-to-end | Test scan → report → quarantine flow |
| Sem mocks para API | 🟡 Medium | Tests precisam de API key real | Fixture JSON responses |
| Cobertura desconhecida | 🟡 Medium | Sem `pytest-cov` report | Add coverage badge |

**Plano de Ação (FASE 4):**

1. **4.1 Unit Tests para scheduler**
   - Test `_should_run_now()` logic
   - Test config validation
   - Test scan execution flow
   - Esforço: **Médio** (3 horas)

2. **4.2 Unit Tests para virustotal_updater**
   - Mock VirusTotal responses (fixtures JSON)
   - Test `fetch_vt_hash_info()`
   - Test cache logic
   - Esforço: **Médio** (3 horas)

3. **4.3 Integration Tests**
   - Test: `scan_directory() → save_report() → quarantine_file()`
   - Use temp directory fixtures
   - Test all file statuses (clean, infected, skip)
   - Esforço: **Médio** (4 horas)

4. **4.4 Coverage Report**
   - Command: `pytest --cov=. --cov-report=html`
   - GitHub Actions: Upload coverage
   - Codecov badge em README
   - Target: 80%+ coverage
   - Esforço: **Baixo** (1 hora)

---

### 2. GitHub Actions / CI

**Problemas Identificados:**

| Problema | Severidade | Descrição | Solução |
|----------|-----------|-----------|---------|
| Sem coverage gates | 🟡 Medium | CI não falha se coverage cai | Add `coverage fail` check |
| Sem linting check | 🟡 Medium | Código pode violar style | Add `black --check` + `flake8` |
| Sem security scan | 🟡 Medium | Sem detection de vulnerabilidades | Add `bandit` ou `safety` |
| Sem build artifacts | 🟡 Medium | Sem .exe para download | Add PyInstaller step |

**Plano de Ação (FASE 4):**

1. **4.5 Add quality gates**
   ```yaml
   - name: Black format check
     run: black --check .
   
   - name: Flake8 lint
     run: flake8 . --max-line-length=100
   
   - name: Coverage threshold
     run: pytest --cov --cov-fail-under=80
   ```
   - Esforço: **Baixo** (1 hora)

2. **4.6 Security scanning**
   - Add `bandit` para security issues
   - Add `safety` para dependency vulnerabilities
   - Esforço: **Baixo** (1 hora)

3. **4.7 Build artifacts**
   - Add PyInstaller step
   - Upload `.exe` como artifact
   - Tag releases com binaries
   - Esforço: **Médio** (2 horas)

---

### 3. Documentation

**Problemas Identificados:**

| Problema | Severidade | Descrição | Solução |
|----------|-----------|-----------|---------|
| README outdated | 🔴 Critical | Ainda refere `gui3.py`, `gui2.py` | Update com `main.py` + `gui.py` |
| MkDocs theme ilegível | 🔴 Critical | "Cyber Coder" tem baixo contraste | Revert para Material default |
| Sem API docs | 🟡 Medium | Funções sem docstring em Sphinx | Add type hints + docstrings |
| Sem architecture diagram | 🟡 Medium | Difícil entender fluxo | Add Mermaid diagram |
| Sem troubleshooting | 🟡 Medium | Users não sabem como debugar | Add FAQ + common issues |

**Plano de Ação (FASE 5):**

1. **5.1 Fix README.md**
   - Remove refs `gui3.py`, `gui2.py`
   - Update: `python main.py` (not gui)
   - Update requirements + dependencies
   - Add screenshot (GUI)
   - Esforço: **Baixo** (1 hora)

2. **5.2 Revert MkDocs theme**
   - Change: `theme: material` (default)
   - Remove inline CSS override
   - Set proper color palette (light mode)
   - Esforço: **Baixo** (30 min)

3. **5.3 Add API documentation**
   - Add docstrings a todas funções (Google style)
   - Generate docs: `mkdocstrings` plugin
   - Inclui type hints
   - Esforço: **Médio** (3 horas)

4. **5.4 Architecture diagram**
   - Mermaid flowchart: User → GUI → Engine → Reports
   - Data flow: Signatures → Scan → Results
   - Include em docs
   - Esforço: **Baixo** (1 hora)

5. **5.5 Troubleshooting guide**
   - Common issues: "API key not found", "No permissions"
   - Solutions: Step-by-step
   - FAQ: Performance tips, exclusion patterns
   - Esforço: **Baixo** (1 hora)

---

## ⚠️ DATA LAYER & Configuration

### 1. signatures.json

**Problemas Identificados:**

| Problema | Severidade | Descrição | Solução |
|----------|-----------|-----------|---------|
| Sem metadata | 🟡 Medium | Só hash → name, sem data adicionada | Add `added_at`, `source`, `category` |
| Sem versionamento | 🟡 Medium | Sem rastreamento de mudanças | Add `signature_version` field |
| Sem categorização | 🟡 Medium | Tudo flat, difícil filtrar | Add `category: trojan|backdoor|worm` |

**Novo Schema:**
```json
{
  "version": "1.0",
  "updated_at": "2026-04-27T14:30:00Z",
  "malware_hashes": {
    "abc123...": {
      "name": "Trojan.Win32.Generic",
      "category": "trojan",
      "source": "virustotal",
      "added_at": "2026-01-15T10:00:00Z"
    }
  }
}
```

---

### 2. exclusions.json

**Problemas Identificados:**

| Problema | Severidade | Descrição | Solução |
|----------|-----------|-----------|---------|
| Sem separação OS | 🟡 Medium | Patterns Windows vs Linux diferentes | Add `os_specific` section |
| Sem comentários | 🟡 Medium | Users não sabem por que excluded | Add description field |

**Novo Schema:**
```json
{
  "version": "1.0",
  "exclusion_patterns": [
    {
      "pattern": "node_modules",
      "description": "Dependency cache, comum false positives",
      "os": ["all"]
    },
    {
      "pattern": "*/AppData/Local/Temp",
      "description": "Windows temp files",
      "os": ["windows"]
    }
  ]
}
```

---

### 3. schedule_config.json

Já melhorado em FASE 2 (Pydantic validation).

---

## 🎯 Resumo: Prioridades

### 🔴 CRÍTICAS (Comece aqui)
| # | Tarefa | Fase | Esforço | Benefício |
|----|--------|------|---------|-----------|
| 1 | Fix README (gui3.py → main.py) | 5.1 | 1h | Clarity |
| 2 | Hash cache | 1.1 | 3h | +60% perf |
| 3 | Skip path optimization | 1.2 | 1h | +30% perf |
| 4 | VirusTotal cache | 2.1 | 4h | -90% API |
| 5 | Customizable scan paths | 2.4 | 2h | UX |

### 🟠 ALTAS (Depois)
| # | Tarefa | Fase | Esforço | Benefício |
|----|--------|------|---------|-----------|
| 6 | Unit tests scheduler | 4.1 | 3h | Coverage |
| 7 | Config validation | 1.4 | 2h | Bugs |
| 8 | Desktop notifications | 2.6 | 2h | UX |
| 9 | Scan history | 2.3 | 4h | UX |
| 10 | Web API | 3.3 | 5h | Feature |

### 🟡 MÉDIAS (Nice-to-have)
| # | Tarefa | Fase | Esforço | Benefício |
|----|--------|------|---------|-----------|
| 11 | Revert MkDocs theme | 5.2 | 1h | Readability |
| 12 | Add graphs reports | 3.2 | 4h | Polish |
| 13 | Web dashboard | 3.4 | 10h | Modern UI |
| 14 | Tests VirusTotal | 4.2 | 3h | Coverage |

---

## 📊 Estimativas Finais

### Por Fase

| Fase | Tema | Horas | Semanas |
|------|------|-------|---------|
| **1** | Core Stability | 40 | 2 |
| **2** | Feature Gaps | 60 | 3-4 |
| **3** | UI/UX Overhaul | 80 | 2-3 |
| **4** | Testing & CI/CD | 30 | 1-2 |
| **5** | Documentation | 20 | 1 |
| **TOTAL** | | **230** | **~3 months** |

### Timeline Recomendado (Part-time 10h/week)

```
Week 1-2:   FASE 1.1 + 1.2 + 5.1 (Quick wins)
Week 3-4:   FASE 1.3 + 1.4 (Stability)
Week 5-8:   FASE 2 (Features)
Week 9-11:  FASE 3 (UI/UX)
Week 12-13: FASE 4 (Tests)
Week 14:    FASE 5 (Polish)
```

---

## 💡 Decisões Técnicas Recomendadas

| Decisão | Opção Recomendada | Razão |
|---------|-------------------|-------|
| **Cache Backend** | SQLite local | Leve, integrado, sem deps |
| **Web Framework** | FastAPI | Async nativa, auto-docs, type hints |
| **Web Frontend** | Vue 3 | Menor bundle, learning curve, ideal educational |
| **Notifications** | `plyer` | Cross-platform (Win/Mac/Linux) |
| **Logging** | `structlog` (future) | JSON logs, estruturado |
| **Config Validation** | Pydantic | Type-safe, reutilizável |
| **Task Scheduling** | APScheduler | Event-driven, cron support |
| **Testing** | pytest + fixtures | Standard Python, fixtures JSON |

---

## 🚀 Como Começar

### Próximos Passos

1. **IMEDIATO** (This week)
   - [ ] Criar branch: `feature/hash-cache`
   - [ ] Implementar 1.1 (Hash cache)
   - [ ] Implementar 1.2 (Skip path optimization)
   - [ ] PR com tests

2. **CURTO PRAZO** (Week 2-3)
   - [ ] Fix README (5.1)
   - [ ] Config validation com Pydantic (1.4)
   - [ ] Customizable paths GUI (2.4)

3. **MÉDIO PRAZO** (Week 4-8)
   - [ ] VirusTotal cache (2.1)
   - [ ] Scan history (2.3)
   - [ ] Rate limiting (2.2)

4. **LONGO PRAZO** (Week 9+)
   - [ ] Web API + Dashboard (3.3 + 3.4)
   - [ ] Reports com gráficos (3.2)
   - [ ] Full test coverage (FASE 4)

---

## 📝 Notas Importantes

### Para o Tim Técnico

- **Não refatorar tudo de uma vez**: Incremental changes com PRs pequenas
- **Testes primeiro**: Especialmente cache logic (edge cases)
- **Backwards compatibility**: Database migrations se mudar schema
- **Security**: API keys nunca em logs, use env vars

### Para a Comunidade

- Bem documentar cada PR
- Add examples nos commit messages
- Keep educational value (não virar production-grade demais)

---

**Documento gerado**: 2026-04-27  
**Próxima revisão recomendada**: Após FASE 2 completa  
**Mantém por**: Nelson M Madeira Rijo + Colaboradores
