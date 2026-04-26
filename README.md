# 🛡️ Anti-Vírus Projeto (Python)

Este projeto é um motor de varredura (*scanning engine*) simplificado, desenvolvido em **Python**. O objetivo principal é demonstrar as bases da cibersegurança, especificamente como identificar ficheiros maliciosos através do cruzamento de assinaturas digitais.

## 🚀 Funcionalidades

* **Deteção por Assinatura:** Gera hashes (MD5/SHA256) dos ficheiros e compara-os com uma base de dados de malware conhecido.
* **Varrimento Recursivo:** Analisa pastas e subpastas à procura de ameaças.
* **Interface Simples:** Feedback imediato no terminal sobre o estado de cada ficheiro verificado.
* **Log de Ameaças:** Registo detalhado de todos os ficheiros suspeitos encontrados durante a execução.

## 🛠️ Tecnologias e Bibliotecas

* **Python 3.x**
* `hashlib`: Para a criação das assinaturas digitais dos ficheiros.
* `os`: Para a navegação e manipulação do sistema de ficheiros.
* `colorama` (opcional): Para dar cor aos alertas no terminal (se decidires usar).

## 📦 Instalação e Utilização

1.  **Clonar o repositório:**
    ```bash
    git clone [https://github.com/Nekas1980/anti-virus-projeto.git](https://github.com/Nekas1980/anti-virus-projeto.git)
    ```

2.  **Entrar na pasta do projeto:**
    ```bash
    cd anti-virus-projeto
    ```

3.  **(Opcional) Criar um ambiente virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    ```

4.  **Escolher versão e executar:**
    
    - **GUI Simples** (básica):
      ```bash
      python gui.py
      ```
    
    - **GUI Intermediária** (threading, logs coloridos):
      ```bash
      python gui2.py
      ```
    
    - **GUI Avançada** (recomendada — progress bar, gráficos, 3 tipos de scan):
      ```bash
      python gui3.py
      ```
    
    - **CLI** (terminal, sem interface gráfica):
      ```bash
      python Virus_project.py
      ```

## ⚙️ Lógica de Funcionamento

O script funciona da seguinte forma:
1. **Input:** O utilizador indica o caminho da diretoria ou ficheiro a analisar.
2. **Cálculo:** O Python lê o conteúdo binário do ficheiro e gera um hash único.
3. **Verificação:** O hash é comparado com uma lista de hashes conhecidos (ex: ficheiro `database.txt` ou lista interna).
4. **Resultado:** O programa informa se o ficheiro é "Seguro" ou "Ameaça Detetada".

## ⚠️ Aviso Legal

Este projeto tem fins **estritamente educacionais**. Não deve ser utilizado como proteção principal para o teu computador, uma vez que não possui análise heurística em tempo real como os antivírus comerciais (ex: Windows Defender, Avast, etc.).

## ✒️ Autor

* **Nekas1980** - [Perfil no GitHub](https://github.com/Nekas1980)

---
*Se achaste este projeto útil para aprenderes mais sobre Python e Segurança, deixa uma ⭐️!*
