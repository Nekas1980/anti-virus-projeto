# Troubleshooting

Problemas comuns e como resolvê-los, organizados por sintoma.

---

## Instalação e arranque

### `ModuleNotFoundError: No module named 'customtkinter'`

A GUI requer `customtkinter`. Instala:

```bash
pip install customtkinter
# ou todos os opcionais:
pip install -r requirements.txt
```

Se estás num venv, confirma que ele está ativado:

```bash
source venv/bin/activate          # macOS/Linux
venv\Scripts\activate             # Windows
```

---

### `ModuleNotFoundError: No module named '_tkinter'`

O Python desta máquina foi compilado **sem suporte Tk**. Soluções:

=== "macOS (Homebrew)"

    ```bash
    brew install python-tk@3.11
    # ou usar a versão oficial python.org que já traz Tk
    ```

=== "Linux (Debian/Ubuntu)"

    ```bash
    sudo apt install python3-tk
    ```

=== "Windows"

    Reinstala o Python a partir de [python.org](https://www.python.org/downloads/) — o instalador oficial inclui Tk por defeito.

---

### `RuntimeError: FastAPI não instalado`

A Web API é opcional. Para a usar:

```bash
pip install fastapi uvicorn
python -m uvicorn web_api:app --port 8765
```

Sem fastapi instalado, o módulo `web_api.py` continua importável mas `create_app()` rejeita.

---

### `openpyxl não instalado` ao exportar Excel

A exportação `.xlsx` precisa de `openpyxl`:

```bash
pip install openpyxl
```

A GUI mostra esse aviso na própria tab "EXPORTAR" se a dependência faltar — os outros formatos (HTML/JSON) continuam a funcionar.

---

## Permissões e ficheiros

### `PermissionError` ao escanear `~/Library/Caches` ou `/System` (macOS)

macOS protege várias pastas de sistema com **TCC (Transparency, Consent and Control)**.

1. Restringe o scan a pastas que controlas (`~/Downloads`, `~/Desktop`, projetos…).
2. Se precisas mesmo de scan profundo, dá ao terminal **Full Disk Access**:
    `Definições → Privacidade & Segurança → Acesso completo ao disco → Adicionar terminal`.

---

### `[!] Erro ao ler /…/file: I/O operation on closed file`

Geralmente significa que o ficheiro foi modificado/eliminado durante o scan (race condition). O motor regista um warning e continua. Se acontecer com frequência:

- Pausa serviços que escrevem na pasta (sync, IDEs, etc.)
- Aumenta `SCAN["file_timeout_seconds"]` em `config.py` se forem ficheiros grandes.

---

### Quarentena diz "ficheiro já existe"

O `quarantine_file()` adiciona automaticamente sufixos numéricos para evitar colisões — `evil.exe` → `evil_1.exe` → `evil_2.exe`. Se vires este aviso, limpa manualmente a pasta `quarantine/` ou usa `git clean -fd quarantine/` (cuidado).

---

## Performance

### Primeiro scan demorado, segundo é rápido — porquê?

É o **HashCache** (Fase 1) a fazer efeito. A primeira passagem calcula SHA-256 de todos os ficheiros e popula `.scan_cache.db`; a segunda só recalcula os que mudaram (mtime ou size diferentes).

Se quiseres limpar o cache:

```bash
rm .scan_cache.db
```

---

### Scan emperra num ficheiro específico

`sha256_file()` tem um **timeout** (default 5s). Ficheiros que excedem ficam com `status="skip"` e `reason="erro ou timeout"`. Para ajustar:

```python
# config.py
SCAN["file_timeout_seconds"] = 10.0   # ou None para desactivar
```

---

### CPU constantemente a 100% durante o scan

Esperado — SHA-256 é CPU-bound. Para limitar:

- Reduz `SCAN["buffer_size"]` (default 1 MB) para libertar mais cooperativamente
- Corre o scan com `nice -n 19 python …` (Linux/macOS)
- Usa o **scheduler** para correr fora de horas

---

## VirusTotal

### `429 Too Many Requests`

Atingiste o limite gratuito (4 req/min). O `RateLimiter` (Fase 2) já regula automaticamente, mas podes tornar mais conservador:

```python
# config.py
VIRUSTOTAL["rate_limit_per_minute"] = 2   # mais defensivo
```

---

### Resultados não aparecem actualizados

O `VTCache` mantém respostas durante 30 dias por defeito. Para forçar refresh:

```bash
rm .vt_cache.db
# ou aumentar TTL temporariamente
```

```python
# config.py
VIRUSTOTAL["cache_ttl_days"] = 1
```

---

### `VIRUSTOTAL_API_KEY not set`

Define a variável de ambiente:

=== "macOS / Linux"

    ```bash
    export VIRUSTOTAL_API_KEY="a_tua_chave"
    # persistente: adiciona a ~/.zshrc ou ~/.bashrc
    ```

=== "Windows (PowerShell)"

    ```powershell
    [Environment]::SetEnvironmentVariable('VIRUSTOTAL_API_KEY', 'a_tua_chave', 'User')
    ```

Nunca cometas a chave ao git — `.env` está no `.gitignore`.

---

## Tests e CI

### Testes do `web_api` aparecem como `skipped`

Esperado se FastAPI/httpx não estiverem instalados — a API é opcional. Para os correr:

```bash
pip install fastapi uvicorn httpx
python -m unittest test_web_api -v
```

---

### `coverage` falha com "fail_under: 80"

A cobertura caiu abaixo do limiar. Vê o relatório:

```bash
coverage run -m unittest discover -p "test_*.py"
coverage report --show-missing
coverage html      # abre htmlcov/index.html
```

Adiciona testes para as linhas em falta ou ajusta `fail_under` em `pyproject.toml` se a queda for justificada.

---

### CI falha em `bandit` mas localmente passa

O job de security usa `--severity-level medium`. Algumas warnings de baixa severidade aparecem na pipeline mas não falham. Confere o artifact `bandit-report` no GitHub Actions.

---

## GUI e UX

### Janela aparece minúscula em monitor 4K

O CustomTkinter herda DPI scaling do Tk. Adiciona ao topo de `main.py`:

```python
import customtkinter as ctk
ctk.set_widget_scaling(1.5)   # ou 2.0 em 4K
ctk.set_window_scaling(1.5)
```

---

### Botão "PAUSAR" não responde

Acontece se o scan ainda não começou (worker thread não está a correr). O botão fica desactivado fora de scans — confere a sidebar.

---

### Métricas live mostram `ETA: —` o tempo todo

Aparece quando a taxa de scan é zero (poucos ficheiros, ainda a iniciar). Estabiliza após ~25 ficheiros (controlado por `UI_REFRESH_EVERY` em `gui.py`).

---

## Build e packaging

### `pyinstaller` falha com "templates not found"

A spec atual já inclui `templates/`. Se mexeste e perdeste, repõe em `build_exe.spec`:

```python
datas=[
    (str(project_root / "signatures.json"), "."),
    (str(project_root / "exclusions.json"), "."),
    (str(project_root / "templates"), "templates"),
],
```

---

### `.exe` não inicia em Windows ("antivirus_projeto.exe stopped working")

1. Executa a partir do terminal para ver o traceback: `dist\antivirus_projeto.exe`
2. Confirma que `signatures.json` e `exclusions.json` foram bundled (verifica o tamanho do .exe — deve ter >5 MB)
3. Tenta rebuilds limpos: `rmdir /s /q build dist && pyinstaller build_exe.spec`

---

## Onde reportar bugs

- [Issues do GitHub](https://github.com/Nekas1980/anti-virus-projeto/issues) — bugs e feature requests
- Inclui sempre: SO + versão Python, comando exacto, traceback completo, conteúdo de `scan.log`
