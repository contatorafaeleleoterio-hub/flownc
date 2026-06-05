## Context

O `core/` é estável (106 testes verdes, `mypy --strict` limpo) e já contém o motor de substituição não-cascata: `matcher.find_matches` (boundary CNC `(?<![A-Z])…(?![0-9.])`), `replacement_plan.build_plan` (plano + conflito por `Suppression`), `replacer.apply_edits` (composição do fim para o início), `file_handler` (encoding/EOL + escrita atômica `_write_bytes_atomic`/`os.replace`) e `conference` (SHA-256 `integrity_hash`/`verify_saved`).

A nova dinâmica "por código" precisa de quatro capacidades de motor (ver `proposal.md` e `specs/`): **Retirar**, **varredura/contagem**, **validação de lote** e **publicação segura**. Esta mudança entrega só o `core/` — sem UI. As decisões de produto estão travadas em `10-PLANO-EXECUCAO-3-COLUNAS.md` §0 (decisões #1, #2, #5) e não se reabrem aqui.

## Goals / Non-Goals

**Goals:**
- Dar ao motor a ação **Retirar** reusando `build_plan`/`apply_edits`, com a única peça nova sendo a **faxina de linha** (pura).
- Contagem de ocorrências por arquivo (pura, `read_fn` injetável) com agregado de cobertura.
- Validação de lote (1 Retirar/execução, allowlist, conflito de regra), distinta do conflito de pedaço.
- Publicação segura: pasta de trabalho + backup versionado, troca atômica, **dupla** conferência SHA-256, só toca o que mudou.
- Manter back-compat: presets e settings antigos carregam sem migração manual.

**Non-Goals:**
- Nenhuma UI (3 colunas, Substituir/Retirar visual, diálogo de pastas → Mudanças 3 e 4).
- Biblioteca código+função+variações e `normalized_form` → Mudança 2.
- Verificações como porteiro no resumo → futuro.
- Threading/QThread → é embrulho de UI (Mudança 3); aqui as funções de `core/` são puras e síncronas.

## Decisions

### D1 — "Retirar" = troca-por-vazio, não motor novo
"Retirar X" vira `Rule(find="X", replace="", action=RETIRAR)`. `build_plan`/`apply_edits` já fazem matching com boundary, resolução de conflito de pedaço e composição de lote misto — tudo testado. **Alternativa rejeitada:** um `core/remover.py` próprio — duplicaria boundary/conflito/composição e não comporia lote misto (substituir + retirar no mesmo arquivo) de graça. **Consequência:** a única lógica nova é a faxina de linha.

### D2 — Faxina de linha escopada por linha do resultado
A faxina roda **sobre o texto já composto**, indexada por **número de linha do resultado**, só nas linhas que receberam uma remoção (replacement vazio de uma edit com `action=RETIRAR`). Regras: colapsa espaços/tabs múltiplos em um, apara as pontas, e apaga a linha+quebra se ela ficou vazia **por causa** da remoção (linha já vazia antes é preservada). EOL vem de `EncodingInfo.eol`.
- **Por que por linha do resultado, não por offset:** apagar uma linha muda offsets; trabalhar por índice de linha no resultado evita recalcular posições.
- **Como saber quais linhas tocar:** `apply_edits` ganha uma variante (ou retorno estendido) que, além do texto, devolve os índices das linhas do resultado tocadas por uma edit de `action=RETIRAR`. A assinatura atual `apply_edits(text, edits) -> str` é preservada (back-compat); a informação extra vem por função/retorno novo para não quebrar chamadores. **Decisão de implementação:** preferir uma função nova (ex.: `apply_edits_tracked`) a mudar o tipo de retorno da existente.

### D3 — `scan.py` reusa `find_matches`, com `Rule` descartável ou helper
`find_matches(text, rule, case_sensitive)` exige um `Rule` (precisa de `find`/`mode`). `scan.count_occurrences` constrói um `Rule` descartável **ou** extrai-se um helper `find_spans(text, find, mode, case_sensitive)` de `matcher`. **Decisão de implementação** (ambos válidos; preferir o helper se ficar limpo). `read_fn: Callable[[Path], str]` injetável → testável sem disco. `ScanResult` carrega `{arquivo: contagem}` + agregado "X de Y contêm".

### D4 — Dois sentidos de "conflito" separados
- **Conflito de pedaço:** sobreposição de bytes; já resolvido por `Suppression` no `build_plan`. Não é responsabilidade de `batch.py`.
- **Conflito de regra:** ≥2 regras no mesmo **código de origem**; novo em `batch.validate_batch`, severidade âmbar (aviso, não bloqueia). Bloqueios críticos: >1 Retirar por execução, Retirar fora da allowlist da biblioteca. Saída: `list[Issue]`.

### D5 — `publisher.py`: ordem à prova de falha, por arquivo que mudou
Para cada arquivo cujo conteúdo **mudou**: (1) grava `.tmp` na pasta de trabalho; (2) confere SHA do `.tmp` vs. conteúdo em memória; (3) copia o original para `backup_dir/_backup_orig_DATA_HORA/` e confere SHA (backup vs. original); (4) `os.replace(.tmp, final)` — atômico; (5) confere SHA do publicado vs. memória; (6) log. **Ordem importante:** backup do original **antes** da troca atômica, para que uma falha no meio nunca deixe a produção sem original recuperável. Reusa `_write_bytes_atomic`/`os.replace` (file_handler) e `integrity_hash`/`verify_saved` (conference). `.tmp` fica no **mesmo volume** da pasta de trabalho (atômico mesmo em share de rede); o backup pode ser outro volume (é cópia, não `replace`).
- **Alternativa rejeitada:** continuar gravando em pasta `_processado_*` paralela (decisão #5 do plano a substituiu — o operador movia arquivos na mão).
- **Invariante:** "o original nunca se perde" agora é garantido pelo backup versionado + dupla conferência, não mais por "não tocar no original".

### D6 — `Rule.action` com default → back-compat dos presets
`Action = SUBSTITUIR | RETIRAR` (Enum herdando `str`, como os outros do `models.py`). `Rule` (frozen) ganha `action: Action = SUBSTITUIR`. Presets JSON antigos (sem `action`) desserializam para `SUBSTITUIR` — nenhuma migração manual. Cuidado conhecido (handoff §6): enum que herda de `str` + Qt `setData`/`data` perde o tipo → reconstruir o enum ao ler (relevante só na UI, Mudanças 3/4).

### D7 — `settings_store` schema v1 → v2 com migração transparente
Adiciona `working_dir` e `backup_dir`. `load_settings` já tem fallback seguro; estender para preencher as chaves novas com default (`""`) quando ausentes. `save_settings` grava v2. Carregar um JSON v1 não levanta erro.

### D8 — Possível divisão 1a/1b
Se Retirar+scan+batch (1a) e publicação (1b) ficarem grandes demais para uma revisão, dividir em duas mudanças OpenSpec sequenciais — ambas core puro/sensível, sem dependência cruzada forte (1b só usa `models`/`settings` de 1a). **Decisão:** manter como **uma** mudança por padrão (escopo coeso = "preparar o motor para a nova dinâmica"); dividir só se a revisão pesar. As tarefas em `tasks.md` já vêm agrupadas para facilitar um corte limpo.

## Risks / Trade-offs

- **Faxina colapsar espaços de linhas não tocadas** → escopo estrito por nº de linha do resultado tocada por RETIRAR; vetor de teste dedicado (linha vizinha com espaços duplos permanece intacta).
- **Apagar linha muda offsets** → faxina opera por índice de linha no texto já composto, nunca por offset de byte.
- **Publicação é destrutiva na produção** (energia/falha no meio) → ordem à prova de falha (`.tmp` → confere → backup → `os.replace` → confere); teste de interrupção simulada garante que a pasta de trabalho nunca fica sem o arquivo íntegro.
- **Republicar na mesma pasta (origem = destino)** → backup **versionado** por data/hora → o original verdadeiro nunca se perde (Rafael dispensou aviso prévio).
- **Pasta de trabalho em rede (lenta/instável)** → `.tmp` no mesmo share (troca atômica vale em rede); backup pode ser local; nesta mudança tudo é síncrono (o progresso/2º plano é embrulho da Mudança 3).
- **Enum `str` + Qt perde tipo** → só afeta a UI; aqui o `core/` trabalha com o enum diretamente; anotado para as Mudanças 3/4.
- **Regra de ouro:** nada entra no `core/` sem teste novo; "o original nunca se perde" reverificado por teste de publicação.

## Migration Plan

1. `models.py`: adicionar `Action`, `Rule.action` (default), `ScanResult`, `Issue` — sem quebrar presets.
2. `settings_store.py`: schema v2 + migração transparente (carregar v1 sem erro).
3. Novos módulos puros: `line_cleanup.py`, `scan.py`, `batch.py`.
4. Integração mínima em `replacer.py`/`replacement_plan.py` (faxina pós-composição via função nova de tracking).
5. `publisher.py` reusando file_handler + conference.
6. Testes por módulo + integração "Retirar no build_plan"; `mypy --strict`; rodar a suíte inteira (não regredir os 106).
- **Rollback:** mudança é aditiva no `core/`; reverter os arquivos novos + o campo `action` restaura o comportamento atual (presets sem `action` já eram `SUBSTITUIR`).

## Open Questions

- `apply_edits_tracked` (função nova) **vs.** estender o retorno de `apply_edits` — decidir na implementação (D2 recomenda função nova para preservar a assinatura atual).
- `scan` usar `Rule` descartável **vs.** extrair `find_spans` de `matcher` (D3) — decidir na implementação pela legibilidade.
- Formato exato do nome do backup (`_backup_orig_DATA_HORA/`) e se o log da publicação é o mesmo `session_log` ou um anexo — alinhar com o `session_log` atual na implementação.
