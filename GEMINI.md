# 🛡️ Antivírus Projeto - Contexto para Gemini CLI

Este ficheiro fornece o contexto operacional, arquitetural e de desenvolvimento necessário para trabalhar no projeto **Antivírus Projeto**.

## 📋 Visão Geral do Projeto
Um motor de varredura (*scanning engine*) educacional desenvolvido em **Python** para demonstrar as bases da cibersegurança, focado na deteção por assinaturas digitais (SHA256).

### Tecnologias Core
- **Linguagem:** Python 3.9+
- **Bibliotecas:** `hashlib` (hashing), `colorama` (CLI), `requests` (API VirusTotal), `tkinter`/`customtkinter` (GUI)
- **Gestão de Dependências:** `pip` (`requirements.txt`, `pyproject.toml`)
- **Testes:** `unittest`, `pytest`

## 🏗️ Arquitetura do Sistema
O projeto está organizado em 4 camadas principais:
1.  **Interface (UI):** `gui.py` (Tkinter) e `Virus_project.py` (CLI).
2.  **Motor de Varredura:** `Virus_project.py` (lógica de hashing e recursão).
3.  **Integração e Suporte:** `virustotal_updater.py` (API), `scheduler.py` (agendamento), `report_generator.py` (HTML/JSON).
4.  **Dados e Configuração:** `signatures.json` (base de malware), `exclusions.json` (diretórios a ignorar).

## 🚀 Comandos Essenciais

### Desenvolvimento e Execução
- **Executar CLI:** `python Virus_project.py`
- **Executar GUI:** `python gui.py`
- **Iniciar Scheduler:** `python scheduler.py run`
- **Atualizar Assinaturas:** `python virustotal_updater.py` (Requer `VIRUSTOTAL_API_KEY`)
- **Criar Config do Scheduler:** `python scheduler.py create-config`

### Testes e Qualidade
- **Executar Testes (Unittest):** `python -m unittest test_virus_project -v`
- **Executar Testes (Pytest):** `pytest`
- **Linting (Flake8):** `flake8 .`
- **Formatação (Black):** `black .`
- **Type Checking (Mypy):** `mypy Virus_project.py`

## 🛠️ Convenções de Desenvolvimento

### Estilo de Código
- Segue rigorosamente o **PEP 8**.
- Utiliza `pathlib` para manipulação de caminhos.
- Utiliza `dataclasses` para estruturas de dados de resultados (`ScanResult`).
- Logging estruturado via módulo `logging`.

### Fluxo de Trabalho
1.  **Novas Funcionalidades:** Devem ser acompanhadas de testes em `test_virus_project.py`.
2.  **Assinaturas:** Novas ameaças devem ser adicionadas via `virustotal_updater.py` ou manualmente em `signatures.json`.
3.  **Exclusões:** Padrões de exclusão (ex: `.git`, `node_modules`) devem ser configurados em `exclusions.json`.

## 📂 Estrutura de Ficheiros Chave
- `Virus_project.py`: Core do motor de varredura e interface CLI.
- `gui.py`: Interface gráfica baseada em Tkinter.
- `signatures.json`: Base de dados de hashes SHA256 (Malware).
- `exclusions.json`: Lista de padrões de ficheiros/pastas a ignorar.
- `report_generator.py`: Lógica para gerar relatórios visuais em HTML.
- `test_virus_project.py`: Suite de testes unitários (18+ testes).

## ⚠️ Notas de Segurança
- **Ambiente de Teste:** Nunca utilizes malware real. Usa ficheiros inofensivos cujos hashes estejam em `signatures.json` para testar a deteção.
- **API Keys:** A chave do VirusTotal deve ser passada via variável de ambiente `VIRUSTOTAL_API_KEY`. Nunca a faças commit no código.
- **Propósito:** Este software é **estritamente educacional** e não substitui uma solução de segurança comercial.
