# 🛡️ Plano de Trabalho — Anti-Virus Projeto

## Análise Atual

### Estrutura
- **Virus_project.py** — Motor principal (bem estruturado com dataclasses, SHA256, quarentena)
- **gui.py** — Interface simples (básica, 75 linhas)
- **gui2.py** — Interface intermediária (não explorado ainda)
- **gui3.py** — Interface avançada (threading, progress bar, gráficos, 3 tipos de scan)
- **clamav.py** — Stub vazio (apenas config mockado)
- **index.html** — Versão web (não explorado ainda)
- **signatures.json** — Base de dados educacional (fictícia, 10 hashes teste)

### Problemas Identificados

| Problema | Severidade | Localização |
|----------|-----------|-------------|
| Inconstência: `gui.py` e `gui3.py` procuram `assinaturas.json`, mas o motor usa `signatures.json` | 🔴 CRÍTICO | gui.py:18, gui3.py:125 |
| README menciona `python main.py` mas arquivo não existe | 🟡 MÉDIO | README.md:40 |
| Sem `requirements.txt` — dependências não documentadas | 🟡 MÉDIO | N/A |
| `clamav.py` é vazio — propósito unclear | 🟢 BAIXO | clamav.py |
| `index.html` não explorado — integração web desconhecida | 🟡 MÉDIO | index.html |

---

## Roadmap de Melhorias

### Fase 1: Correções Críticas (1-2h)
- [x] Explorar estrutura completa
- [ ] **Corrigir inconstência de nomes de arquivo** — unificar em `signatures.json`
- [ ] **Criar `requirements.txt`** — tkinter, pathlib, json, hashlib (built-in)
- [ ] **Atualizar README** — remover `main.py`, detalhar qual GUI usar
- [ ] **Testar ambas as GUIs** — garantir que funcionam

### Fase 2: Melhorias de Código (2-3h)
- [ ] **Refatorar `clamav.py`** — ou remover, ou implementar integração real com ClamAV
- [ ] **Consolidar GUI** — escolher entre gui3 (avançada) como principal; remover gui.py/gui2.py ou manter como fallback
- [ ] **Melhorar Virus_project.py**:
  - [ ] Adicionar logging estruturado (não apenas print)
  - [ ] Exceção handling mais robusta
  - [ ] Opção de multi-threading na varredura
- [ ] **Explorar `index.html`** — se for versão web, criar Flask/FastAPI backend

### Fase 3: Novos Recursos (3-4h)
- [ ] **Whitelist/Exclusões** — permitir ignorar pastas (node_modules, .git, etc.)
- [ ] **Atualizar assinaturas** — integrar com VirusTotal API ou ClamAV CVD
- [ ] **Agendamento** — scan automático em intervalos (background)
- [ ] **Relatórios melhorados** — HTML, PDF (além de JSON)
- [ ] **Testes unitários** — pytest para core functions
- [ ] **Documentação API** — docstrings, type hints completos

### Fase 4: Produção (1-2h)
- [ ] **CI/CD** — GitHub Actions para testes automáticos
- [ ] **Packaging** — .exe (PyInstaller), ou distribuição Python formal
- [ ] **Docs completas** — dev setup, contribuição, architecture

---

## Prioridades Imediatas

**Esta semana:**
1. ✅ Clonar + análise completa (FEITO)
2. ⏳ Corrigir inconstência `assinaturas.json` → `signatures.json`
3. ⏳ Criar `requirements.txt`
4. ⏳ Testar gui3.py em macOS (threading, caminhos)
5. ⏳ Explorar index.html

**Próxima semana:**
- Consolidar GUIs
- Refactor de Virus_project.py
- Testes básicos

---

## Notas Técnicas

- **Python 3.x** com tkinter (built-in)
- **macOS**: caminhos como `~/Downloads`, `~/Desktop` funcionam; `C:/Windows/Temp` é Windows-only
- **gui3.py** é a versão mais completa — usar como base
- **Virus_project.py** está bem estruturado — evitar grandes refactors

---

## Próximo Passo
→ Começar com **Fase 1: Correções Críticas**
