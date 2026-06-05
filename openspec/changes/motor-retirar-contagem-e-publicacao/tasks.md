> Grupos 1–5 = bloco "1a" (Retirar/scan/batch); grupo 6 = bloco "1b" (publicação); grupo 7 = integração/QA. Se a revisão pesar, 1a e 1b podem virar duas mudanças (ver design D8). Regra de ouro: nada no `core/` sem teste novo; rodar a suíte inteira ao final (não regredir os 106).

## 1. Modelo (`core/models.py`)

- [ ] 1.1 Adicionar `class Action(str, Enum)` com `SUBSTITUIR = "substituir"` e `RETIRAR = "retirar"`.
- [ ] 1.2 Adicionar campo `action: Action = Action.SUBSTITUIR` ao `Rule` (frozen) — default garante back-compat dos presets antigos.
- [ ] 1.3 Adicionar dataclass `ScanResult` (contagem por arquivo `dict[str, int]` + agregado "X de Y arquivos contêm").
- [ ] 1.4 Adicionar dataclass `Issue` (validação de lote: severidade `Severity` + mensagem + referência à(s) regra(s)).
- [ ] 1.5 `mypy --strict` limpo nos models.

## 2. Faxina de linha (`core/line_cleanup.py`, novo, puro)

- [ ] 2.1 Criar `clean_removed_lines(text, removed_line_idxs, eol) -> CleanupResult` (texto novo + linhas afetadas + pares antes→depois p/ preview futuro).
- [ ] 2.2 Regras: colapsar 2+ espaços/tabs em 1; aparar pontas; apagar linha+quebra se ficou vazia **por causa** da remoção; preservar EOL.
- [ ] 2.3 Não tocar linhas fora de `removed_line_idxs`; não apagar linha que já era vazia.
- [ ] 2.4 `tests/test_line_cleanup.py`: linha vazia some · linha vazia pré-existente preservada · EOL `\r\n`/`\n` preservado · linha vizinha com espaços duplos intacta · espaços colapsados na linha tocada.

## 3. Integração da faxina no motor (`core/replacer.py`, `core/replacement_plan.py`)

- [ ] 3.1 Criar `apply_edits_tracked(text, edits) -> (str, list[int])` que devolve o texto composto **e** os índices de linha do resultado tocados por edits de `action=RETIRAR` (preservar `apply_edits` atual intacto — D2).
- [ ] 3.2 No fluxo de composição, se houver edits RETIRAR, chamar `clean_removed_lines` escopado a essas linhas; senão, comportamento idêntico ao atual.
- [ ] 3.3 Garantir que `build_plan` marca a origem da edit (qual regra/ação) para o tracking saber quais são RETIRAR.
- [ ] 3.4 `mypy --strict` limpo; nenhuma regressão nos testes de substituição existentes.

## 4. Varredura / contagem (`core/scan.py`, novo, puro)

- [ ] 4.1 Criar `count_occurrences(find, mode, case_sensitive, files, read_fn) -> ScanResult`, reusando o matching com boundary (Rule descartável ou helper `find_spans` — D3).
- [ ] 4.2 Preencher contagem por arquivo + agregado "X de Y contêm"; marcar arquivos com 0 ocorrências como sinal útil.
- [ ] 4.3 `tests/test_scan.py`: contagem por arquivo · agregado · boundary (`M6` não conta `M60`) · `read_fn` injetável (sem disco) · zero-ocorrências sinalizado.

## 5. Validação de lote (`core/batch.py`, novo, puro)

- [ ] 5.1 Criar `validate_batch(rules, library) -> list[Issue]`.
- [ ] 5.2 Conflito de **regra**: ≥2 regras no mesmo código de origem → `Issue` âmbar (aviso).
- [ ] 5.3 Limite: >1 regra de ação RETIRAR → `Issue` crítico.
- [ ] 5.4 Allowlist: regra de Retirar com código fora da biblioteca → `Issue` crítico.
- [ ] 5.5 `tests/test_batch_validate.py`: conflito de regra âmbar · >1 Retirar bloqueia · allowlist bloqueia · lote válido = lista vazia · conflito de regra ≠ conflito de pedaço.

## 6. Publicação segura (`core/publisher.py`, novo, sensível) + settings

- [ ] 6.1 `core/settings_store.py`: adicionar `working_dir` e `backup_dir`; subir schema v1 → v2; `load_settings` carrega v1 sem erro (defaults seguros); `save_settings` grava v2.
- [ ] 6.2 Criar `publish_batch(working_dir, backup_dir, items, read_fn) -> PublishResult` (só arquivos que mudaram).
- [ ] 6.3 Por arquivo que mudou: gravar `.tmp` na pasta de trabalho (reusar `_write_bytes_atomic`) → conferir SHA do `.tmp` vs. memória.
- [ ] 6.4 Copiar original para `backup_dir/_backup_orig_DATA_HORA/` → conferir SHA (backup vs. original) com `integrity_hash`/`verify_saved`.
- [ ] 6.5 `os.replace(.tmp, final)` atômico → conferir SHA do publicado vs. memória → registrar no log.
- [ ] 6.6 Ordem à prova de falha: backup **antes** da troca; `.tmp` no mesmo volume; backup pode ser outro volume; nunca deixar a pasta de trabalho sem o arquivo.
- [ ] 6.7 `tests/test_publisher.py`: backup versionado por execução · troca atômica · só toca o que mudou · falha simulada deixa a produção íntegra (original recuperável) · backup em outro volume · dupla conferência reporta divergência.
- [ ] 6.8 Teste de settings: persistência `working_dir`/`backup_dir` · carregar v1 sem erro.

## 7. Integração, QA e fechamento

- [ ] 7.1 Teste de integração "Retirar dentro do `build_plan`": `N50 M6 T0101`→`N50 T0101` · `M6` sozinho→linha some · `M6T1`→`T1` · `M8 M6 M9`→`M8 M9` · `M60` intacto · lote misto (`M8→M08` + retirar `M6`) compõe · conflito Substituir×Retirar resolvido por `Suppression`.
- [ ] 7.2 Rodar a suíte completa (`pytest`) — todos verdes, sem regressão dos 106 existentes.
- [ ] 7.3 `mypy --strict` limpo no `core/` inteiro; `ruff` (line-length 100) limpo nos arquivos novos/alterados.
- [ ] 7.4 Conferir DoD: vetores do Retirar passam · lote misto compõe · publicação testada (backup versionado + troca atômica + dupla conferência; falha simulada não corrompe a produção) · invariante "o original nunca se perde" preservado.
- [ ] 7.5 Atualizar `docs/CONTEXTO.md` e a memória ao concluir; preparar para `/opsx:archive`.
