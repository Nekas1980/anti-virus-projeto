# 🛡️ Anti-Vírus Projeto (Python)

[![Tests](https://github.com/Nekas1980/anti-virus-projeto/actions/workflows/tests.yml/badge.svg)](https://github.com/Nekas1980/anti-virus-projeto/actions/workflows/tests.yml)
[![Docs](https://github.com/Nekas1980/anti-virus-projeto/actions/workflows/deploy.yml/badge.svg)](https://nekas1980.github.io/anti-virus-projeto/)
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/downloads/)
[![Tests passing](https://img.shields.io/badge/tests-130%20passing-brightgreen.svg)](https://github.com/Nekas1980/anti-virus-projeto/actions/workflows/tests.yml)
[![Coverage](https://img.shields.io/badge/coverage-%E2%89%A580%25-brightgreen.svg)](https://github.com/Nekas1980/anti-virus-projeto/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Motor de varredura de malware em **Python** desenvolvido no IEFP Python Bootcamp — Cibersegurança. Detecta ficheiros maliciosos por cruzamento de assinaturas SHA-256, com cache local para acelerar rescans, integração opcional com VirusTotal, GUI moderna em CustomTkinter e Web API REST opcional (FastAPI).

> **Aviso:** Projeto educacional. Não substitui um antivírus comercial em produção.

📚 **[Documentação completa](https://nekas1980.github.io/anti-virus-projeto/)** · 🐛 **[Reportar bug](https://github.com/Nekas1980/anti-virus-projeto/issues)** · 💡 **[FAQ](https://nekas1980.github.io/anti-virus-projeto/guides/faq/)**

---

## 🚀 Funcionalidades

- **Detecção por SHA-256:** cruza hashes contra base de assinaturas conhecidas.
- **Cache de hashes (SQLite):** evita recomputar SHA-256 de ficheiros já analisados — invalidado automaticamente quando `mtime` ou tamanho mudam.
- **Matcher de exclusões pré-compilado:** padrões fnmatch convertidos em regex uma única vez por scan, sem custo por ficheiro.
- **Timeout por ficheiro:** evita freezes em ficheiros grandes ou corrompidos.
- **Varrimento recursivo** com exclusões configuráveis (`exclusions.json`).
- **Quarentena automática** com renomeação anti-colisão.
- **Relatórios profissionais** — HTML com gráficos Chart.js (doughnut + bar de top diretórios), JSON estruturado com metadata, **Excel `.xlsx`** multi-sheet (Summary/Infected/Clean/Stats).
- **Varreduras agendadas** via `scheduler.py`.
- **Histórico persistente** (SQLite) com paths, totais e duração.
- **Integração VirusTotal** (opcional) com rate limiting + cache local.
- **Notificações desktop** opcionais (`plyer`) no fim de cada scan.
- **GUI Cyber-Sentinel** (CustomTkinter) com tabs LOG / RESULTADOS / EXPORTAR, filtros pesquisáveis, métricas live (`files/s · ETA · ELAPSED`) e botão Pausar/Retomar.
- **Web API REST** (FastAPI, opcional) — `/api/scan`, `/api/history`, `/api/reports/{id}/{html|json|xlsx}`.

---

## 📦 Instalação

```bash
git clone https://github.com/Nekas1980/anti-virus-projeto.git
cd anti-virus-projeto
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## ⚡ Utilização

### GUI (recomendado)
```bash
python main.py
```

### CLI
```bash
python Virus_project.py
# será pedido o diretório a analisar
```

### Atualizar assinaturas via VirusTotal
```bash
export VIRUSTOTAL_API_KEY="a_tua_chave"
python virustotal_updater.py
```

### Scheduler (varreduras periódicas)
```bash
python scheduler.py create-config   # gera schedule_config.json
python scheduler.py run             # corre em foreground
```

### Web API (opcional — requer FastAPI)
```bash
pip install fastapi uvicorn
python -m uvicorn web_api:app --port 8765
# curl -X POST http://localhost:8765/api/scan -H 'Content-Type: application/json' \
#      -d '{"paths": ["/Users/me/Downloads"]}'
```

### Exportar Excel (opcional — requer openpyxl)
```bash
pip install openpyxl
# Pela GUI: tab "EXPORTAR" → botão EXCEL
```

---

## 🧪 Testes

```bash
python -m unittest discover -p "test_*.py" -v
```

A suite cobre **130 testes** organizados em 13 módulos:

| Módulo                          | Testes | Cobertura                                   |
|---------------------------------|:------:|---------------------------------------------|
| `test_virus_project.py`         |   20   | scan, signatures, exclusions, cache, timeout |
| `test_hash_cache.py`            |   12   | set/get, invalidação, persistência, edges   |
| `test_exclusion_matcher.py`     |    6   | matching de padrões, edge cases             |
| `test_vt_cache.py`              |    6   | TTL, hits/misses, cache de 404              |
| `test_rate_limiter.py`          |    7   | token-bucket, retry decorator               |
| `test_scan_history.py`          |    6   | persistência, recent(), get/delete          |
| `test_user_prefs.py`            |    5   | escrita atómica, recent_paths cap           |
| `test_virustotal_updater.py`    |    8   | API, fetch, dedup, fallback                 |
| `test_report_generator.py`      |   16   | metadata, risk class, HTML+JSON, charts     |
| `test_excel_exporter.py`        |    5   | sheets, fallback openpyxl, capping          |
| `test_gui_filters.py`           |   14   | filtros, search, ETA/elapsed                |
| `test_web_api.py`               |    7   | health/scan/history (skip se FastAPI ausente) |
| `test_scheduler.py`             |   11   | _should_run_now, _load_config, _run_scan, auto-quarantine |
| `test_integration.py`           |    3   | end-to-end: scan→cache→reports→quarantine |

### Coverage e Quality

```bash
# Coverage local (requer `pip install coverage[toml]`)
coverage run -m unittest discover -p "test_*.py"
coverage report  # threshold ≥ 80% configurado em pyproject.toml
coverage html    # gera htmlcov/

# Lint
black --check .
flake8

# Security
bandit -r . -c pyproject.toml
safety check --file=requirements.txt
```

CI corre todos estes em GitHub Actions a cada push/PR — ver `.github/workflows/tests.yml`.

---

## 🗂️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│  UI:    main.py (entry) ─► gui.py (CustomTkinter, tabs+filtros) │
│         Virus_project.py main() (CLI)                           │
│         web_api.py (FastAPI, opcional)                          │
├─────────────────────────────────────────────────────────────────┤
│  Engine:  Virus_project.py                                      │
│           ├─ sha256_file()      ── cálculo SHA-256              │
│           ├─ scan_file()        ── usa HashCache + timeout      │
│           └─ scan_directory()   ── usa ExclusionMatcher         │
├─────────────────────────────────────────────────────────────────┤
│  Suporte:  hash_cache.py        SQLite cache (.scan_cache.db)   │
│            exclusion_matcher.py regex pré-compilado             │
│            scheduler.py         agendamento periódico           │
│            virustotal_updater.py enriquecimento (rate-limited)  │
│            vt_cache.py          cache local de respostas VT     │
│            rate_limiter.py      token bucket + retry decorator  │
│            scan_history.py      histórico persistente (SQLite)  │
│            user_prefs.py        prefs JSON atómicas             │
│            notifications.py     desktop alerts (plyer, opcional)│
│            gui_filters.py       filtros puros + ETA/elapsed     │
│            report_generator.py  HTML+JSON com Chart.js          │
│            excel_exporter.py    .xlsx multi-sheet (openpyxl)    │
├─────────────────────────────────────────────────────────────────┤
│  Templates: templates/report.{html,css}                          │
│  Config:    config.py            paths e parâmetros centrais     │
│  Dados:     signatures.json, exclusions.json                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Configuração

Todos os paths e parâmetros estão centralizados em `config.py`:

| Chave                                | Descrição                                        |
|--------------------------------------|--------------------------------------------------|
| `PATHS["signatures"]`                | base de hashes de malware                        |
| `PATHS["exclusions"]`                | padrões fnmatch a ignorar                        |
| `PATHS["scan_cache"]`                | DB SQLite do cache de hashes                     |
| `SCAN["file_timeout_seconds"]`       | timeout por ficheiro (default 5s)                |
| `SCAN["cache_enabled"]`              | activa/desactiva o cache                         |
| `VIRUSTOTAL["rate_limit_per_minute"]`| limite da API gratuita                           |

A chave VirusTotal nunca deve ser commited — usa `.env` ou variável de ambiente `VIRUSTOTAL_API_KEY`.

---

## 🧠 Lógica de Funcionamento

1. Utilizador indica directório a analisar.
2. Engine carrega `signatures.json` e `exclusions.json`.
3. `ExclusionMatcher` pré-compila padrões em regex.
4. `HashCache` é aberto (SQLite) para evitar recomputar hashes já vistos.
5. `scan_directory()` percorre recursivamente; ficheiros excluídos são saltados.
6. Para cada ficheiro: tenta cache → senão calcula SHA-256 com timeout → compara com assinaturas.
7. Resultado classificado em `clean`, `infected` ou `skip` (com `reason`).
8. Relatório gravado em `output/scan_report.json`.
9. Opção de mover infectados para `quarantine/`.

---

## 🤝 Contribuir

Vê [`CONTRIBUTING.md`](CONTRIBUTING.md) para o workflow completo. Resumo:

1. Fork → branch a partir de `main`
2. Implementa + adiciona testes (`test_*.py`)
3. `python -m unittest discover -p "test_*.py"` deve passar a 100%
4. PR descritivo

---

## ✒️ Autor

**Nelson M Madeira Rijo** — [@Nekas1980](https://github.com/Nekas1980)
IEFP Python Bootcamp · Cibersegurança · Faro, Portugal

---

*Se este projeto te ajudou a aprender, deixa uma ⭐.*
