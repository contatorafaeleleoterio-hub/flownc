## Context

O `core/` é estável (106 testes verdes, `mypy --strict` limpo) e já contém o motor de substituição não-cascata: `matcher.find_matches` (boundary CNC `(?<![A-Z])…(?![0-9.])`), `replacement_plan.build_plan` (plano + conflito por `Suppression`), `replacer.apply_edits` (composição do fim para o início), `file_handler` (encoding/EOL + escrita atômica `_write_bytes_atomic`/`os.replace`) e `conference` (SHA-256 `integrity_hash`/`verify_saved`).

A nova dinâmica "por código" precisa de três capacidades de motor (ver `proposal.md` e `specs/`): **varredura/contagem**, **validação de lote** e **publicação segura**. Esta mudança entrega só o `core/` — sem UI. As decisões de produto estão travadas em `docs/DECISOES.md` e não se reabrem aqui.

> **Nota (2026-06-05):** a ação **"Retirar"** (e a faxina de linha `core/line_cleanup.py`) saiu do escopo — a remoção já é atendida pela troca-por-vazio. As decisões D1/D2/D6 originais sobre Retirar foram removidas; a numeração abaixo foi reorganizada.

## Goals / Non-Goals

**Goals:**
- Contagem de ocorrências por arquivo (pura, `read_fn` injetável) com agregado de cobertura.
- Validação de lote (conflito de regra), distinta do conflito de pedaço.
- Publicação segura: pasta de trabalho + backup versionado, troca atômica, **dupla** conferência SHA-256, só toca o que mudou.
- Manter back-compat: presets e settings antigos carregam sem migração manual.

**Non-Goals:**
- Nenhuma UI (3 colunas, diálogo de pastas → Mudanças 3 e 4).
- Biblioteca código+função+variações e `normalized_form` → Mudança 2.
- Verificações como porteiro no resumo → futuro.
- Threading/QThread → é embrulho de UI (Mudança 3); aqui as funções de `core/` são puras e síncronas.
- **Ação "Retirar" dedicada + faxina de linha → fora do escopo** (remoção já atendida pela troca-por-vazio).

## Decisions

### D1 — `scan.py` reusa `find_matches`, com `Rule` descartável ou helper
`find_matches(text, rule, case_sensitive)` exige um `Rule` (precisa de `find`/`mode`). `scan.count_occurrences` constrói um `Rule` descartável **ou** extrai-se um helper `find_spans(text, find, mode, case_sensitive)` de `matcher`. **Decisão de implementação** (ambos válidos; preferir o helper se ficar limpo). `read_fn: Callable[[Path], str]` injetável → testável sem disco. `ScanResult` carrega `{arquivo: contagem}` + agregado "X de Y contêm".

### D2 — Dois sentidos de "conflito" separados
- **Conflito de pedaço:** sobreposição de bytes; já resolvido por `Suppression` no `build_plan`. Não é responsabilidade de `batch.py`.
- **Conflito de regra:** ≥2 regras no mesmo **código de origem**; novo em `batch.validate_batch`, severidade âmbar (aviso, não bloqueia). Saída: `list[Issue]`.

### D3 — `publisher.py`: ordem à prova de falha, por arquivo que mudou
Para cada arquivo cujo conteúdo **mudou**: (1) grava `.tmp` na pasta de trabalho; (2) confere SHA do `.tmp` vs. conteúdo em memória; (3) copia o original para `backup_dir/_backup_orig_DATA_HORA/` e confere SHA (backup vs. original); (4) `os.replace(.tmp, final)` — atômico; (5) confere SHA do publicado vs. memória; (6) log. **Ordem importante:** backup do original **antes** da troca atômica, para que uma falha no meio nunca deixe a produção sem original recuperável. Reusa `_write_bytes_atomic`/`os.replace` (file_handler) e `integrity_hash`/`verify_saved` (conference). `.tmp` fica no **mesmo volume** da pasta de trabalho (atômico mesmo em share de rede); o backup pode ser outro volume (é cópia, não `replace`).
- **Alternativa rejeitada:** continuar gravando em pasta `_processado_*` paralela (decisão #5 do plano a substituiu — o operador movia arquivos na mão).
- **Invariante:** "o original nunca se perde" agora é garantido pelo backup versionado + dupla conferência, não mais por "não tocar no original".

### D4 — `settings_store` schema v1 → v2 com migração transparente
Adiciona `working_dir` e `backup_dir`. `load_settings` já tem fallback seguro; estender para preencher as chaves novas com default (`""`) quando ausentes. `save_settings` grava v2. Carregar um JSON v1 não levanta erro.

## Risks / Trade-offs

- **Publicação é destrutiva na produção** (energia/falha no meio) → ordem à prova de falha (`.tmp` → confere → backup → `os.replace` → confere); teste de interrupção simulada garante que a pasta de trabalho nunca fica sem o arquivo íntegro.
- **Republicar na mesma pasta (origem = destino)** → backup **versionado** por data/hora → o original verdadeiro nunca se perde (Rafael dispensou aviso prévio).
- **Pasta de trabalho em rede (lenta/instável)** → `.tmp` no mesmo share (troca atômica vale em rede); backup pode ser local; nesta mudança tudo é síncrono (o progresso/2º plano é embrulho da Mudança 3).
- **Regra de ouro:** nada entra no `core/` sem teste novo; "o original nunca se perde" reverificado por teste de publicação.

## Migration Plan

1. `models.py`: adicionar `ScanResult`, `Issue` — sem quebrar presets.
2. `settings_store.py`: schema v2 + migração transparente (carregar v1 sem erro).
3. Novos módulos puros: `scan.py`, `batch.py`.
4. `publisher.py` reusando file_handler + conference.
5. Testes por módulo; `mypy --strict`; rodar a suíte inteira (não regredir os existentes).
- **Rollback:** mudança é aditiva no `core/`; reverter os arquivos novos restaura o comportamento atual.

## Open Questions

- `scan` usar `Rule` descartável **vs.** extrair `find_spans` de `matcher` (D1) — decidir na implementação pela legibilidade.
- Formato exato do nome do backup (`_backup_orig_DATA_HORA/`) e se o log da publicação é o mesmo `session_log` ou um anexo — alinhar com o `session_log` atual na implementação.
