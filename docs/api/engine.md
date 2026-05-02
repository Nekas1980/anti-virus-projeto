# Engine — Core Scanning

A camada de motor é o coração do projeto: hashing, deteção e travessia recursiva.

---

## `Virus_project`

Motor principal — orquestra hashing, comparação com assinaturas, exclusões e geração do `ScanResult`.

::: Virus_project
    options:
      members:
        - ScanResult
        - sha256_file
        - load_signatures
        - load_exclusions
        - get_default_exclusions
        - should_skip_path
        - scan_file
        - scan_directory
        - quarantine_file
        - save_report
        - add_signature

---

## `hash_cache`

Cache SQLite (WAL mode) que guarda os hashes SHA-256 já calculados, evitando recomputar quando `mtime` e `size` permanecem inalterados.

::: hash_cache
    options:
      members:
        - HashCache

---

## `exclusion_matcher`

Pré-compila os padrões `fnmatch` em regex uma única vez por scan — substitui o loop O(n × m) por O(n) regex match.

::: exclusion_matcher
    options:
      members:
        - ExclusionMatcher
