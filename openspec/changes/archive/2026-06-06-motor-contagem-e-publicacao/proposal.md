## Why

A nova dinâmica "por código" (sintetizada em `docs/PRODUTO.md` e planejada em `docs/PLANO.md`) exige capacidades de motor que hoje não existem: **contar** ocorrências por arquivo antes de executar (a varredura que alimenta os chips e o match-banner), **validar o lote** (aviso de conflito de regra) e **publicar** o resultado direto na pasta de trabalho da máquina com **backup versionado** dos originais. É a parte mais arriscada e 100% testável, base de toda a UI que vem depois. Sem UI: só `core/` puro/sensível.

> **Nota (2026-06-05):** a ação **"Retirar"** saiu desta proposta. A remoção de um código já é atendida hoje pela troca-por-vazio (campo "Trocar por"/"Substituir por" deixado em branco), tanto no fluxo de Lote quanto no editor por arquivo. A versão dedicada com faxina de linha pode voltar como mudança própria no futuro, se necessário.

## What Changes

- **Varredura / contagem** (`core/scan.py`, novo) — conta ocorrências de um código por arquivo, com agregado "X de Y arquivos contêm". Função pura com `read_fn` injetável (testável sem disco).
- **Validação de lote** (`core/batch.py`, novo) — `validate_batch`: conflito de **regra** (≥2 regras no mesmo código de origem → âmbar/aviso). Distinto do conflito de **pedaço** (`Suppression`), que o motor já resolve.
- **Publicação segura** (`core/publisher.py`, novo) — `publish_batch`: por arquivo que **mudou**, grava `.tmp` na pasta de trabalho → confere SHA → copia o original para o backup versionado → confere → `os.replace` atômico → confere o publicado → log. **Dupla conferência** SHA-256 (backup + publicado), troca **atômica** (a pasta da máquina nunca fica sem o arquivo), só toca o que mudou.
- **Modelo** (`core/models.py`) — novos `ScanResult` e `Issue`.
- **Configuração** (`core/settings_store.py`) — ganha `working_dir` (pasta da máquina) e `backup_dir`, persistentes. **BREAKING (interno)**: schema de settings sobe de v1 → v2, com migração transparente (defaults seguros; settings v1 carregam sem erro).
- **Non-goals:** nenhuma UI (3 colunas, diálogo de pastas ficam nas Mudanças 3 e 4); biblioteca código+função+variações é a Mudança 2; verificações-porteiro são futuro; **ação "Retirar" dedicada** (faxina de linha) foi retirada do escopo.

## Capabilities

### New Capabilities
- `varredura-de-ocorrencias`: contagem de ocorrências de um código por arquivo, com agregado, base da varredura em 2º plano.
- `validacao-de-lote`: aviso de conflito de regra (≥2 regras no mesmo código de origem), distinto do conflito de pedaço.
- `publicacao-segura`: publicação do resultado na pasta de trabalho + backup versionado dos originais, com troca atômica, dupla conferência SHA-256 e configuração de pastas persistente.

### Modified Capabilities
<!-- Não há specs existentes em openspec/specs/; todas as capacidades acima são novas. -->

## Impact

- **Código novo:** `core/scan.py`, `core/batch.py`, `core/publisher.py`.
- **Código modificado:** `core/models.py` (`ScanResult`, `Issue`), `core/settings_store.py` (`working_dir`/`backup_dir`, schema v2 + migração).
- **Reaproveitado intacto (não mexer):** `core/matcher.py` (boundary), `core/session_log.py`, `core/preset_store.py`, `core/json_store.py`; de `core/file_handler.py` a escrita atômica (`_write_bytes_atomic`/`os.replace`) e `encode_batch`; de `core/conference.py` o SHA-256 (`integrity_hash`/`verify_saved`), agora aplicado **duas vezes** (backup + publicado).
- **Testes novos:** `tests/test_scan.py`, `tests/test_batch_validate.py`, `tests/test_publisher.py`.
- **Invariante preservado:** "o original nunca se perde" — antes era "pasta nova"; agora é **backup versionado** + troca atômica + dupla conferência + log.
- **Compatibilidade:** presets existentes (`MAZAK_VTC530.json`) e settings v1 continuam carregando sem migração manual.
- **DoD:** testes novos verdes · `mypy --strict` limpo no `core/` · varredura confere por arquivo + agregado · validação reporta conflito de regra · publicação testada (backup versionado + troca atômica + dupla conferência; falha simulada não corrompe a produção) · invariante "o original nunca se perde" preservado.
