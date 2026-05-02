# Anti-Vírus Projeto

[![Tests](https://github.com/Nekas1980/anti-virus-projeto/actions/workflows/tests.yml/badge.svg)](https://github.com/Nekas1980/anti-virus-projeto/actions/workflows/tests.yml)
[![Docs](https://github.com/Nekas1980/anti-virus-projeto/actions/workflows/deploy.yml/badge.svg)](https://nekas1980.github.io/anti-virus-projeto/)
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/downloads/)
[![Tests passing](https://img.shields.io/badge/tests-146%20passing-brightgreen.svg)](https://github.com/Nekas1980/anti-virus-projeto/actions/workflows/tests.yml)
[![Coverage](https://img.shields.io/badge/coverage-%E2%89%A580%25-brightgreen.svg)](https://github.com/Nekas1980/anti-virus-projeto/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Motor de detecção de malware em **Python** desenvolvido no âmbito do IEFP Python Bootcamp — Cibersegurança. Detecta ficheiros maliciosos por cruzamento de assinaturas SHA-256, com cache local, integração opcional com VirusTotal, GUI moderna e Web API REST.

> **Aviso:** Projecto educacional. Não substitui um antivírus comercial em produção.

📚 **[Documentação completa](https://nekas1980.github.io/anti-virus-projeto/)** · 🐛 **[Reportar bug](https://github.com/Nekas1980/anti-virus-projeto/issues)**

---

## Funcionalidades

| Área | Detalhe |
|------|---------|
| **Detecção** | Cruzamento de hashes SHA-256 contra base de assinaturas conhecidas |
| **Cache** | SQLite local — evita recomputar hashes de ficheiros já analisados; invalidado automaticamente quando `mtime` ou tamanho mudam |
| **Exclusões** | Padrões fnmatch pré-compilados em regex uma única vez por scan |
| **Timeout** | Limite configurável por ficheiro — evita bloqueios em ficheiros grandes ou corrompidos |
| **Quarentena** | Mover automaticamente ficheiros infectados, com renomeação anti-colisão |
| **Relatórios** | HTML com gráficos Chart.js · JSON estruturado com metadata · Excel `.xlsx` multi-sheet |
| **Histórico** | Persistência de scans em SQLite (paths, totais, duração) |
| **Scheduler** | Varreduras periódicas configuráveis (`scheduler.py`) |
| **VirusTotal** | Enriquecimento opcional com rate limiting e cache local |
| **Notificações** | Alertas desktop opcionais via `plyer` |
| **GUI** | Interface CustomTkinter com tabs LOG / RESULTADOS / EXPORTAR, métricas live (files/s · ETA · elapsed) e Pausar/Retomar |
| **Web API** | REST opcional via FastAPI — `/api/scan`, `/api/history`, `/api/reports/{id}/{html\|json\|xlsx}` |

---

## Instalação

```bash
git clone https://github.com/Nekas1980/anti-virus-projeto.git
cd anti-virus-projeto
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Dependências opcionais

```bash
pip install openpyxl              # Exportação Excel
pip install fastapi uvicorn       # Web API REST
pip install plyer                 # Notificações desktop
```

---

## Utilização

### GUI (recomendado)

```bash
python main.py
```

### CLI

```bash
python Virus_project.py
```

### Web API

```bash
python -m uvicorn web_api:app --port 8765

# Iniciar scan
curl -X POST http://localhost:8765/api/scan \
     -H 'Content-Type: application/json' \
     -d '{"paths": ["/home/user/Downloads"]}'

# Consultar resultado
curl http://localhost:8765/api/scan/<scan_id>

# Descarregar relatório HTML
curl http://localhost:8765/api/reports/<scan_id>/html -o report.html
```

### Scheduler

```bash
python scheduler.py create-config   # gera schedule_config.json
python scheduler.py run             # executa em foreground
```

### Actualizar assinaturas via VirusTotal

```bash
export VIRUSTOTAL_API_KEY="a_tua_chave"
python virustotal_updater.py
```

---

## Testes

```bash
python -m unittest discover -p "test_*.py" -v
```

**146 testes** organizados em 15 módulos:

| Módulo | Testes | Âmbito |
|--------|:------:|--------|
| `test_virus_project.py` | 20 | scan, assinaturas, exclusões, cache, timeout |
| `test_hash_cache.py` | 12 | set/get, invalidação, persistência |
| `test_exclusion_matcher.py` | 6 | padrões fnmatch, edge cases |
| `test_vt_cache.py` | 6 | TTL, hits/misses, cache de 404 |
| `test_rate_limiter.py` | 7 | token bucket, retry decorator |
| `test_scan_history.py` | 6 | persistência, `recent()`, get/delete |
| `test_user_prefs.py` | 5 | escrita atómica, cap de recent_paths |
| `test_virustotal_updater.py` | 8 | API, fetch, dedup, fallback |
| `test_report_generator.py` | 16 | metadata, risk class, HTML+JSON, gráficos |
| `test_excel_exporter.py` | 5 | sheets, fallback openpyxl, capping |
| `test_gui_filters.py` | 14 | filtros, search, ETA/elapsed |
| `test_notifications.py` | 10 | ImportError path, success, exception, branches |
| `test_web_api.py` | 7 | health/scan/history (skip se FastAPI ausente) |
| `test_scheduler.py` | 11 | `_should_run_now`, `_load_config`, auto-quarantine |
| `test_integration.py` | 3 | end-to-end: scan → cache → relatórios → quarentena |

### Quality gates

```bash
# Cobertura (≥80%, branch=True)
coverage run -m unittest discover -p "test_*.py"
coverage report

# Linting
black --check .
flake8

# Segurança estática
bandit -r . -c pyproject.toml
safety check --file=requirements.txt
```

CI corre todas as verificações em GitHub Actions em cada push/PR — 12 configurações (3 OS × 4 Python).

---

## Arquitectura

```
┌──────────────────────────────────────────────────────────────────┐
│  UI       main.py (entry) → gui.py (CustomTkinter)              │
│           Virus_project.py main() (CLI)                          │
│           web_api.py (FastAPI, opcional)                         │
├──────────────────────────────────────────────────────────────────┤
│  Engine   Virus_project.py                                       │
│           ├─ sha256_file()      cálculo SHA-256 com timeout      │
│           ├─ scan_file()        HashCache + assinaturas          │
│           └─ scan_directory()   ExclusionMatcher + recursão      │
├──────────────────────────────────────────────────────────────────┤
│  Suporte  hash_cache.py         cache SQLite de hashes           │
│           exclusion_matcher.py  regex pré-compilado              │
│           scan_history.py       histórico persistente (SQLite)   │
│           scheduler.py          agendamento periódico            │
│           virustotal_updater.py enriquecimento (rate-limited)    │
│           vt_cache.py           cache local de respostas VT      │
│           rate_limiter.py       token bucket + retry decorator   │
│           notifications.py      alertas desktop (plyer)          │
│           user_prefs.py         preferências JSON atómicas       │
│           gui_filters.py        filtros puros + ETA/elapsed      │
│           report_generator.py   HTML + JSON com Chart.js         │
│           excel_exporter.py     .xlsx multi-sheet (openpyxl)     │
├──────────────────────────────────────────────────────────────────┤
│  Templates  templates/report.{html,css}                          │
│  Config     config.py  — paths e parâmetros centrais             │
│  Dados      signatures.json · exclusions.json                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## Configuração

Todos os paths e parâmetros estão centralizados em `config.py`:

| Chave | Descrição | Default |
|-------|-----------|---------|
| `PATHS["signatures"]` | Base de hashes de malware | `signatures.json` |
| `PATHS["exclusions"]` | Padrões fnmatch a ignorar | `exclusions.json` |
| `PATHS["scan_cache"]` | DB SQLite do cache de hashes | `.scan_cache.db` |
| `SCAN["file_timeout_seconds"]` | Timeout por ficheiro | `5 s` |
| `SCAN["cache_enabled"]` | Activa/desactiva o cache | `True` |
| `VIRUSTOTAL["rate_limit_per_minute"]` | Limite da API gratuita | `4` |

A chave VirusTotal nunca deve ser committada — usa `.env` ou variável de ambiente `VIRUSTOTAL_API_KEY`.

---

## Contribuir

1. Fork → branch a partir de `main`
2. Implementa + adiciona testes (`test_*.py`)
3. `python -m unittest discover -p "test_*.py"` deve passar a 100%
4. PR descritivo

Ver [`CONTRIBUTING.md`](CONTRIBUTING.md) para o workflow completo.

---

## Autor

**Nelson M Madeira Rijo** — [@Nekas1980](https://github.com/Nekas1980)  
IEFP Python Bootcamp · Cibersegurança · Faro, Portugal

---

*Se este projecto te ajudou a aprender, deixa uma ⭐.*
