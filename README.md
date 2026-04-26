# anti-virus-projeto# 🛡️ Anti-Vírus Projeto

Este projeto consiste num motor de varredura (scanning engine) simples desenvolvido para fins educacionais. O objetivo é demonstrar como funciona a identificação de ficheiros maliciosos através de assinaturas de hash e análise de estrutura.

## 🚀 Funcionalidades

- **Varredura por Hash:** Identifica ficheiros maliciosos conhecidos comparando hashes (MD5/SHA256).
- **Análise de Diretórios:** Capacidade de percorrer pastas de forma recursiva à procura de ameaças.
- **Relatório de Ameaças:** Exibe no terminal (ou interface) os ficheiros considerados perigosos.
- **Base de Dados Extensível:** Facilidade para adicionar novas assinaturas de vírus à base de dados local.

## 🛠️ Tecnologias Utilizadas

* [Python](https://www.python.org/) (Linguagem principal)
* `hashlib` (Para geração de assinaturas dos ficheiros)
* `os` & `sys` (Para manipulação do sistema de ficheiros)

## 📦 Instalação e Uso

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/Nekas1980/anti-virus-projeto.git](https://github.com/Nekas1980/anti-virus-projeto.git)
