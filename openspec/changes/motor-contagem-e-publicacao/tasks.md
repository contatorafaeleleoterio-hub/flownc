> Grupos 1–3 = motor puro (models/scan/batch); grupo 4 = publicação + settings (sensível); grupo 5 = QA/fechamento. Regra de ouro: nada no `core/` sem teste novo; rodar a suíte inteira ao final (não regredir os existentes).
> **Nota (2026-06-05):** a ação "Retirar" e a faxina de linha saíram do escopo (remoção já atendida pela troca-por-vazio). Os grupos de Retirar/faxina/integração foram removidos.

## 1. Modelo (`core/models.py`)

- [x] 1.1 Adicionar dataclass `ScanResult` (contagem por arquivo `dict[str, int]` + agregado "X de Y arquivos contêm").
- [x] 1.2 Adicionar dataclass `Issue` (validação de lote: severidade `Severity` + mensagem + referência à(s) regra(s)).
- [x] 1.3 `mypy --strict` limpo nos models.

## 2. Varredura / contagem (`core/scan.py`, novo, puro)

- [x] 2.1 Criar `count_occurrences(find, mode, case_sensitive, files, read_fn) -> ScanResult`, reusando o matching com boundary (Rule descartável ou helper `find_spans` — D1).
- [x] 2.2 Preencher contagem por arquivo + agregado "X de Y contêm"; marcar arquivos com 0 ocorrências como sinal útil.
- [x] 2.3 `tests/test_scan.py`: contagem por arquivo · agregado · boundary (`M6` não conta `M60`) · `read_fn` injetável (sem disco) · zero-ocorrências sinalizado.

## 3. Validação de lote (`core/batch.py`, novo, puro)

- [x] 3.1 Criar `validate_batch(rules, library) -> list[Issue]`.
- [x] 3.2 Conflito de **regra**: ≥2 regras no mesmo código de origem → `Issue` âmbar (aviso).
- [x] 3.3 `tests/test_batch_validate.py`: conflito de regra âmbar · lote válido = lista vazia · conflito de regra ≠ conflito de pedaço.

## 4. Publicação segura (`core/publisher.py`, novo, sensível) + settings

- [ ] 4.1 `core/settings_store.py`: adicionar `working_dir` e `backup_dir`; subir schema v1 → v2; `load_settings` carrega v1 sem erro (defaults seguros); `save_settings` grava v2.
- [ ] 4.2 Criar `publish_batch(working_dir, backup_dir, items, read_fn) -> PublishResult` (só arquivos que mudaram).
- [ ] 4.3 Por arquivo que mudou: gravar `.tmp` na pasta de trabalho (reusar `_write_bytes_atomic`) → conferir SHA do `.tmp` vs. memória.
- [ ] 4.4 Copiar original para `backup_dir/_backup_orig_DATA_HORA/` → conferir SHA (backup vs. original) com `integrity_hash`/`verify_saved`.
- [ ] 4.5 `os.replace(.tmp, final)` atômico → conferir SHA do publicado vs. memória → registrar no log.
- [ ] 4.6 Ordem à prova de falha: backup **antes** da troca; `.tmp` no mesmo volume; backup pode ser outro volume; nunca deixar a pasta de trabalho sem o arquivo.
- [ ] 4.7 `tests/test_publisher.py`: backup versionado por execução · troca atômica · só toca o que mudou · falha simulada deixa a produção íntegra (original recuperável) · backup em outro volume · dupla conferência reporta divergência.
- [ ] 4.8 Teste de settings: persistência `working_dir`/`backup_dir` · carregar v1 sem erro.

## 5. QA e fechamento

- [ ] 5.1 Rodar a suíte completa (`pytest`) — todos verdes, sem regressão dos testes existentes.
- [ ] 5.2 `mypy --strict` limpo no `core/` inteiro; `ruff` (line-length 100) limpo nos arquivos novos/alterados.
- [ ] 5.3 Conferir DoD: varredura confere por arquivo + agregado · validação reporta conflito de regra · publicação testada (backup versionado + troca atômica + dupla conferência; falha simulada não corrompe a produção) · invariante "o original nunca se perde" preservado.
- [ ] 5.4 Atualizar `docs/CONTEXTO.md` e a memória ao concluir; preparar para `/opsx:archive`.
