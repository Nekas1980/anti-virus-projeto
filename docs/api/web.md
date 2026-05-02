# Web API & Scheduler

Camadas opcionais para integração externa e automação.

---

## `web_api` — REST API (FastAPI)

API REST opcional. Importa-se sem fastapi instalado (degrada gracefully); chamar `create_app()` sem fastapi instalado lança `RuntimeError`.

### Endpoints

| Método | Caminho | Descrição |
|--------|---------|-----------|
| `GET` | `/api/health` | Liveness probe |
| `GET` | `/api/status` | Lista scans em curso |
| `POST` | `/api/scan` | Dispara scan async (corpo: `{"paths": [...]}`) |
| `GET` | `/api/scan/{scan_id}` | Estado de um scan |
| `GET` | `/api/scan/{scan_id}/results` | Resultados completos |
| `GET` | `/api/history?limit=N` | Histórico persistido |
| `GET` | `/api/reports/{scan_id}/{html\|json\|xlsx}` | Download do relatório |

### Como correr

```bash
pip install fastapi uvicorn
python -m uvicorn web_api:app --port 8765
```

### Exemplo curl

```bash
curl -X POST http://localhost:8765/api/scan \
     -H 'Content-Type: application/json' \
     -d '{"paths": ["/Users/me/Downloads"]}'

# Resposta: {"scan_id": "uuid…", "status": "pending", …}

curl http://localhost:8765/api/scan/<uuid>
curl http://localhost:8765/api/reports/<uuid>/html -o report.html
```

### Auto-doc

::: web_api
    options:
      members:
        - ScanState
        - create_app

---

## `scheduler` — Varreduras agendadas

Loop simples baseado em polling (30s) que corre scans em horários definidos em `schedule_config.json`.

::: scheduler
    options:
      members:
        - ScanScheduler

### Configuração

```json
{
  "enabled": true,
  "intervals": [
    {
      "name": "daily_morning",
      "hour": 9,
      "minute": 0,
      "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
      "paths": ["/home/user/Downloads"],
      "auto_quarantine": false
    }
  ]
}
```

### Execução

```bash
python scheduler.py create-config   # gera schedule_config.json
python scheduler.py run             # corre em foreground
```
