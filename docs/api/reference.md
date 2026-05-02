# API Reference

Esta secção contém **documentação auto-gerada** a partir das docstrings dos módulos Python via [`mkdocstrings`](https://mkdocstrings.github.io/).

A organização segue as 5 camadas da arquitetura:

| Camada | Página | Módulos |
|--------|--------|---------|
| **Engine** | [Engine](engine.md) | `Virus_project`, `hash_cache`, `exclusion_matcher` |
| **Suporte** | [Suporte](support.md) | `scan_history`, `user_prefs`, `vt_cache`, `rate_limiter`, `notifications`, `gui_filters`, `report_generator`, `excel_exporter` |
| **Web API** | [Web API](web.md) | `web_api` (FastAPI), `scheduler` |

---

## Convenções de docstring

O projeto usa **Google style** (suportado pelo `mkdocstrings` configurado em `mkdocs.yml`):

```python
def scan_file(file_path: Path, signatures: Dict[str, str]) -> ScanResult:
    """Analisa um ficheiro contra a base de assinaturas.

    Args:
        file_path: Caminho absoluto do ficheiro a analisar.
        signatures: Mapa hash SHA-256 → nome da ameaça.

    Returns:
        Um ``ScanResult`` com status ``clean``/``infected``/``skip``.

    Raises:
        OSError: Se houver falha de I/O ao ler o ficheiro.
    """
```

---

## Configuração centralizada

::: config
    options:
      show_root_heading: false
