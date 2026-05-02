# FAQ

Perguntas frequentes sobre o projeto, decisões de design e uso prático.

---

## Geral

??? question "Posso usar isto em produção?"
    Não. É um projeto **educacional** — não substitui um antivírus comercial (Kaspersky, Bitdefender, Defender). Falta-lhe deteção heurística, análise comportamental, sandbox dinâmica, atualização de assinaturas em tempo real e uma equipa de threat intel por trás. Use-o para aprender ou para scans pontuais reforçados por VirusTotal.

??? question "Em que se baseia a deteção?"
    Apenas em **comparação de hashes SHA-256** contra `signatures.json`. Se o hash exacto do ficheiro estiver na base, é marcado como infectado. Qualquer alteração de 1 byte muda o hash e escapa à deteção — é a limitação clássica da deteção por assinatura.

??? question "Posso adicionar mais assinaturas?"
    Sim. Manualmente em `signatures.json` ou via CLI:

    ```bash
    python -c "from Virus_project import add_signature; \
               add_signature('hash_sha256_aqui', 'Nome.Da.Ameaca')"
    ```

    Para enriquecer a partir do VirusTotal:

    ```bash
    export VIRUSTOTAL_API_KEY=...
    python virustotal_updater.py
    ```

??? question "Pode escanear ficheiros dentro de ZIP/RAR?"
    Não — o motor lê só ficheiros do filesystem, sem extracção. Para isso seria preciso adicionar suporte a arquivos (ex.: módulo `zipfile`), o que está fora do scope educacional.

---

## Performance

??? question "Quantos ficheiros consigo escanear por segundo?"
    Depende muito do disco e do tamanho médio dos ficheiros. Em SSD moderno com cache populado (segunda passagem), tipicamente **200–800 ficheiros/s**. Sem cache: **30–100 ficheiros/s** se forem pequenos, muito menos para multimédia grande.

??? question "Como é que o cache funciona?"
    O `HashCache` (SQLite) guarda `(path, mtime, size, sha256)`. Numa nova chamada a `cache.get(path)`, recompara `mtime` e `size` — se ambos coincidirem, devolve o hash sem recalcular. Qualquer alteração invalida automaticamente. Ver `hash_cache.py`.

??? question "Devo desligar o cache?"
    Só se andares a fazer benchmarks comparativos do cálculo de hash. Para uso normal, mantém ligado:

    ```python
    SCAN["cache_enabled"] = True   # default
    ```

??? question "Quanto espaço ocupa o cache?"
    Aproximadamente **80–120 bytes por ficheiro** indexado (em SQLite com índices). 1 milhão de ficheiros ≈ 100 MB.

---

## VirusTotal

??? question "Preciso mesmo de uma API key?"
    Só se quiseres usar `virustotal_updater.py` para enriquecer assinaturas ou consultar reputação. O scan local funciona sem API key — usa apenas `signatures.json`.

??? question "A free tier chega?"
    Para uso educacional, **sim**. O limite é 4 requests/min e 500/dia. O `RateLimiter` (token-bucket) garante que não excedes, e o `VTCache` (TTL 30 dias) elimina a maior parte das chamadas repetidas.

??? question "Posso usar a v2 em vez da v3?"
    Não está implementado — o `virustotal_updater.py` usa apenas a v3 (mais moderna, mais ricas em metadados). Adicionar v2 seria refactor não-trivial.

---

## GUI vs CLI vs Web API

??? question "Qual devo usar?"
    Depende do uso:

    | Uso | Interface |
    |-----|-----------|
    | Inspeccionar pastas pontualmente | **GUI** (`python main.py`) |
    | Pipeline / automação / scripting | **CLI** (`python Virus_project.py`) |
    | Integração com dashboard, agendamento externo, multi-cliente | **Web API** (`python -m uvicorn web_api:app`) |
    | Cron-style recurrent scans | **Scheduler** (`python scheduler.py run`) |

??? question "Posso correr a Web API em produção (ex: container)?"
    Tecnicamente sim — é FastAPI standard. Mas falta-lhe autenticação, rate limiting de API e isolation que esperarias num serviço externo. **Não exponhas à internet** sem adicionar pelo menos `Depends(API key)` e um proxy reverso. Para uso local/intranet está OK.

??? question "Tem dashboard web?"
    Não nesta versão. A API REST está pronta para servir um — Vue/React/Svelte ficam ao critério do contribuidor. Foi conscientemente **deferido** para manter o scope educacional.

---

## Quarentena

??? question "Os ficheiros em `quarantine/` ainda são perigosos?"
    Sim — apenas foram **movidos**, não desinfectados. Não os executes. Para os eliminar definitivamente:

    ```bash
    rm -rf quarantine/   # macOS/Linux
    rmdir /s /q quarantine    # Windows
    ```

??? question "Posso restaurar um ficheiro da quarentena?"
    Sim — é só `mv`. O ficheiro original mantém o nome (com sufixo se houvesse colisão), mas o caminho original perde-se. Se for crítico, regista o `file_path` original do `ScanResult` antes de quarentenar.

---

## Tests e CI

??? question "Como aumento a coverage?"
    Vê o relatório:

    ```bash
    coverage run -m unittest discover -p "test_*.py"
    coverage report --show-missing
    coverage html        # htmlcov/index.html
    ```

    Adiciona testes para as linhas marcadas como missing. O alvo é ≥80% — está configurado em `.coveragerc` e `pyproject.toml`.

??? question "Por que `gui.py` e `web_api.py` estão omissos do coverage?"
    O `gui.py` é difícil de testar sem display (Tk requer servidor X/Quartz). O `web_api.py` está coberto via `test_web_api.py` mas só corre quando FastAPI está instalado — para evitar reportar coverage falsamente baixa quando a dep está ausente, está omisso por defeito. Podes inverter editando `.coveragerc`.

??? question "Black/flake8 falham no CI mas o código está limpo?"
    Os jobs `lint` estão com `continue-on-error: true` por enquanto — não bloqueiam merges. Quando o codebase ficar 100% conforme, removemos esse flag em `.github/workflows/tests.yml`.

---

## Documentação e MkDocs

??? question "Como gero esta documentação localmente?"
    ```bash
    pip install mkdocs mkdocs-material mkdocstrings[python] pymdown-extensions
    mkdocs serve         # http://localhost:8000
    mkdocs build         # gera site/
    ```

??? question "Posso editar e ver mudanças sem deploy?"
    Sim — `mkdocs serve` faz live-reload. Cada `.md` editado dispara rebuild automático.

??? question "A API reference está vazia?"
    Significa que `mkdocstrings` não conseguiu importar o módulo. Confirma que estás na raiz do repo (`paths: ["."]` em `mkdocs.yml`) e que todas as dependências estão instaladas (incluindo as opcionais que os módulos importam).

---

## Educacional / Pedagógico

??? question "É bom como projeto de portfolio?"
    Sim — cobre múltiplos tópicos relevantes (arquitetura em camadas, SQLite, threading, REST API, testes, CI/CD multi-OS, packaging com PyInstaller, MkDocs). Documenta as decisões no README e mostra os 130 testes a passarem nas 12 configurações de CI.

??? question "Como estendo o projeto?"
    Vê o [Roadmap](../contribute/roadmap.md). Sugestões de baixo esforço e alto valor pedagógico:

    - Suporte YARA rules
    - Detecção heurística (ex.: entropy)
    - Dashboard Vue/React consumindo a Web API
    - Suporte a arquivos comprimidos (zip/rar)
    - SBOM (Software Bill of Materials) generator

??? question "Onde aprendo mais sobre o domínio?"
    - [VirusTotal Academy](https://www.virustotal.com/learn) — análise de malware
    - [OWASP Cheat Sheets](https://cheatsheetseries.owasp.org/) — fundamentos de segurança aplicacional
    - [SANS Reading Room](https://www.sans.org/white-papers/) — papers profundos em IR/forense
