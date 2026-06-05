## Why

A nova dinâmica "por código" (agora sintetizada em `docs/PRODUTO.md` e planejada em `docs/PLANO.md`) exige quatro capacidades de motor que hoje não existem: **retirar** um código (não só substituir), **contar** ocorrências por arquivo antes de executar (a varredura que alimenta os chips e o match-banner), **validar o lote** (1 Retirar por execução, allowlist, conflito de regra) e **publicar** o resultado direto na pasta de trabalho da máquina com **backup versionado** dos originais. Esta é a **Mudança 1** do plano — a parte mais arriscada e 100% testável, base de toda a UI que vem depois. Sem UI: só `core/` puro/sensível.

## What Changes

- **Ação "Retirar" no motor** — sem motor novo. "Retirar X" é modelado como `Rule(find=X, replace="", action=RETIRAR)`, reusando `build_plan`/`apply_edits` (boundary CNC, conflito de pedaço via `Suppression`, composição de lote misto — já testados). A **única** parte nova é a **faxina de linha** (`core/line_cleanup.py`, função pura): junta espaços duplicados, apara as pontas e, se a linha ficou vazia **por causa** da remoção, apaga a linha e a quebra; preserva o EOL do arquivo.
- **Varredura / contagem** (`core/scan.py`, novo) — conta ocorrências de um código por arquivo, com agregado "X de Y arquivos contêm". Função pura com `read_fn` injetável (testável sem disco).
- **Validação de lote** (`core/batch.py`, novo) — `validate_batch`: conflito de **regra** (≥2 regras no mesmo código de origem → âmbar), **1 Retirar por execução**, **allowlist** (só código presente na biblioteca). Distinto do conflito de **pedaço** (`Suppression`), que o motor já resolve.
- **Publicação segura** (`core/publisher.py`, novo) — `publish_batch`: por arquivo que **mudou**, grava `.tmp` na pasta de trabalho → confere SHA → copia o original para o backup versionado → confere → `os.replace` atômico → confere o publicado → log. **Dupla conferência** SHA-256 (backup + publicado), troca **atômica** (a pasta da máquina nunca fica sem o arquivo), só toca o que mudou.
- **Modelo** (`core/models.py`) — `Action = SUBSTITUIR | RETIRAR`; `Rule` ganha `action: Action = SUBSTITUIR` (campo novo com default → presets antigos continuam válidos); novos `ScanResult` e `Issue`.
- **Integração mínima** (`core/replacer.py`, `core/replacement_plan.py`) — após compor o texto, se houve edits de ação RETIRAR, rodar a faxina **escopada às linhas do resultado** tocadas por um RETIRAR. `apply_edits` passa a poder reportar quais linhas do resultado foram tocadas por RETIRAR.
- **Configuração** (`core/settings_store.py`) — ganha `working_dir` (pasta da máquina) e `backup_dir`, persistentes. **BREAKING (interno)**: schema de settings sobe de v1 → v2, com migração transparente (defaults seguros; settings v1 carregam sem erro).
- **Non-goals:** nenhuma UI (3 colunas, Substituir/Retirar visual, diálogo de pastas ficam nas Mudanças 3 e 4); biblioteca código+função+variações é a Mudança 2; verificações-porteiro são futuro. **Não** se cria `core/remover.py` — Retirar reusa o motor existente.

## Capabilities

### New Capabilities
- `remocao-de-codigo`: ação "Retirar" como troca-por-vazio + faxina de linha, integrada ao motor de plano/composição existente (boundary, conflito, lote misto).
- `varredura-de-ocorrencias`: contagem de ocorrências de um código por arquivo, com agregado, base da varredura em 2º plano.
- `validacao-de-lote`: regras de segurança do lote (1 Retirar por execução, allowlist da biblioteca, aviso de conflito de regra).
- `publicacao-segura`: publicação do resultado na pasta de trabalho + backup versionado dos originais, com troca atômica, dupla conferência SHA-256 e configuração de pastas persistente.

### Modified Capabilities
<!-- Não há specs existentes em openspec/specs/; todas as capacidades acima são novas. -->

## Impact

- **Código novo:** `core/line_cleanup.py`, `core/scan.py`, `core/batch.py`, `core/publisher.py`.
- **Código modificado:** `core/models.py` (Action, campo `Rule.action`, `ScanResult`, `Issue`), `core/replacer.py` e `core/replacement_plan.py` (ponto de integração da faxina), `core/settings_store.py` (`working_dir`/`backup_dir`, schema v2 + migração).
- **Reaproveitado intacto (não mexer):** `core/matcher.py` (boundary), `core/session_log.py`, `core/preset_store.py`, `core/json_store.py`; de `core/file_handler.py` a escrita atômica (`_write_bytes_atomic`/`os.replace`) e `encode_batch`; de `core/conference.py` o SHA-256 (`integrity_hash`/`verify_saved`), agora aplicado **duas vezes** (backup + publicado).
- **Testes novos:** `tests/test_line_cleanup.py`, `tests/test_scan.py`, `tests/test_batch_validate.py`, `tests/test_publisher.py`, + 1 de integração "Retirar dentro do `build_plan`".
- **Invariante preservado:** "o original nunca se perde" — antes era "pasta nova"; agora é **backup versionado** + troca atômica + dupla conferência + log.
- **Compatibilidade:** presets existentes (`MAZAK_VTC530.json`) e settings v1 continuam carregando sem migração manual.
- **DoD:** testes novos verdes · `mypy --strict` limpo no `core/` · vetores do Retirar passam · lote misto compõe · publicação testada (backup versionado + troca atômica + dupla conferência; falha simulada não corrompe a produção) · invariante "o original nunca se perde" preservado.
