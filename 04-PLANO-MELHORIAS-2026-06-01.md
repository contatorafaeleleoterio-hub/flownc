# 04 - Plano de Melhorias Revisado (Hardening + UX) - CNC Batch Editor

> **Data:** 2026-06-01  
> **Base obrigatoria:** `00-HANDOFF.md` + `02-PRD_CNC_BatchEditor_v2.3.md`  
> **Status desta revisao:** **VERIFICADO contra o codigo e PRONTO para implementar.** As 7
> lacunas do §2.2 foram confirmadas (refs `arquivo:linha`); fixes propostos usam APIs reais
> (`Mode.CNC_ADDRESS`, `compile_rule`, `write_atomic`, `make_output_dir`); decisao do H0.6
> fechada (modelo de linha rico). Caminhos defasados corrigidos em `00-HANDOFF.md`/`STATUS.md`.
> Proxima sessao: iniciar pela Etapa preliminar + Stage 0. Nenhum codigo foi alterado nesta revisao.

---

## 1. Objetivo desta revisao

Refinar o plano anterior para reduzir risco de erro operacional no chao de fabrica, sem quebrar o motor ja validado.  
Diretriz: melhorias devem ser **aditivas na borda** (UI, persistencia, conferencia, UX), preservando o comportamento seguro do `core/`.

Observacao importante: nenhum software pode garantir risco zero absoluto, mas este plano adiciona camadas de defesa para reduzir risco pratico ao minimo aceitavel.

---

## 2. Analise minuciosa do plano anterior

## 2.1 Pontos fortes (manter)

- Direcao correta: trocar digitacao manual por selecao de codigos.
- Reuso de logica validada do projeto atual (contagem de matches, preview, leitura/escrita atomica).
- Incremental por sessoes independentes (A-E), o que reduz regressao.
- Alinhamento com PRD v2.3 e padroes de mercado (CIMCO/Predator/CNC Syntax).

## 2.2 Lacunas tecnicas criticas identificadas

Esses itens precisam entrar **antes ou junto** das melhorias de UX.
**Revisao 2026-06-01: as 7 lacunas foram CONFIRMADAS no codigo (refs `arquivo:linha`).**

1. `load_preset` pode disparar `KeyError/ValueError` nao encapsulado em `PresetError` (risco de crash na GUI ao abrir preset invalido). — ✅ `core/preset_store.py:65` (`str(data["machine"])`), `:25` (`str(d["id"])`) e enums `Scope/Mode/OnZeroMatches(...)`.
2. Regras por arquivo usam `basename` como chave na UI (`_file_subs`), com risco de colisao quando dois arquivos de pastas diferentes tiverem o mesmo nome. — ✅ `ui/main_window.py:109,359,406,440`; `Rule.file` e basename (`core/models.py:52`).
3. Salvamento usa `out_dir / o.name`; em caso de nomes iguais no lote, pode sobrescrever arquivo de saida. — ✅ `ui/main_window.py:529`; **pior:** `src_dir = checked[0].parent` (`:520`) assume pasta unica (bug latente multi-pasta).
4. Verificacao estrutural usa substring (`"M30" in text`, `count("M30")`), com chance de falso positivo (ex.: `M300`). — ✅ `core/verifier.py:61-62,69`. (`run_configurable` ja usa `compile_rule`; so `run_structural` esta no substring.)
5. Persistencia JSON (`preset`, futuros `library/settings`) nao e atomica; queda de energia pode corromper arquivo. — ✅ `core/preset_store.py:121` (`write_text` direto). Escopo: JSON de config (a escrita dos `.nc` ja e atomica via `write_atomic`).
6. Salvamento em lote nao faz preflight de encodabilidade de todos os arquivos antes de escrever; pode ocorrer lote parcialmente salvo se houver erro no meio. — ✅ `ui/main_window.py:526-531` (grava em loop, sem checar antes).
7. GUI ignora `OnZeroMatches` (CLI respeita `warn/ignore/error`), gerando inconsistencia de regra. — ✅ GUI: `_rules_for` (`:424-434`) nao seta a politica; `blocked` so vem de CRITICAL (`:459`). CLI honra IGNORE/ERROR (`cli.py:104,110-113`). **Causa raiz:** a UI achata `Rule` em tupla de 4 (`:109,344,357`), descartando `on_zero_matches`/`mode`/`priority` (ver H0.6).

---

## 3. Ordem de execucao revisada (segura)

## 3.1 Novo Stage 0 (obrigatorio): Hardening base

Executar este stage antes das sessoes A-D.

### H0.1 Preset robusto e tolerante a erro

- Em `core/preset_store.py`:
  - encapsular `KeyError`, `TypeError`, `ValueError`, `OSError`, `JSONDecodeError` como `PresetError`;
  - validar tipos de campos (`machine`, `extensions`, `rules`, `verifications`);
  - mensagens claras com campo invalido e motivo.

### H0.2 Verificacao estrutural por token CNC (sem substring)

- Em `core/verifier.py`:
  - substituir uso de `in` e `count` por contagem via `compile_rule(..., Mode.CNC_ADDRESS, case_sensitive=True)`;
  - validar `%` inicio/fim como hoje, mas `M30/M02/M06/G43/G44` por match de endereco CNC.
- API confirmada: `Mode.CNC_ADDRESS` (`core/matcher.py:23`) e `compile_rule(find, mode, case_sensitive)` (`:43`) existem; o boundary `(?![0-9.])` ja impede `M30` casar em `M300`.
- **Apos a troca, reconfirmar os 5 testes `TV-STR-*` (`tests/test_verifier.py`) — devem continuar verdes** (a checagem de `M30` em `"M30\n"` segue casando com boundary).
- Nota (fora do Stage 0, melhoria futura): as verificacoes *configuraveis* da aba Verificacoes usam `mode=LITERAL` por padrao (`core/models.py:65`; preset exemplo idem), entao `must_exist M30` tambem casaria `M300`. Avaliar oferecer `CNC_ADDRESS` tambem nelas depois.

### H0.3 Salvamento seguro de lote (all-or-nothing logico)

- Em `ui/main_window.py` e/ou novo helper em `core/file_handler.py`:
  - preflight: para cada arquivo, gerar bytes com `encode_text` antes de gravar qualquer saida;
  - se algum falhar, abortar lote inteiro sem gravar nada;
  - somente apos preflight OK criar pasta e escrever todos.

### H0.4 Colisao de nomes no lote

- Na carga de arquivos:
  - detectar basenames repetidos no lote marcado;
  - bloquear execucao com mensagem clara: listar duplicados e orientar renomear ou processar separadamente.
- Chave interna de regras por arquivo:
  - migrar de `basename` para chave unica (`str(Path.resolve())`) na UI;
  - usar `basename` apenas para exibicao e para `Rule.file` no momento de build por arquivo.
- **Multi-pasta (mesmo bug, tratar junto):** `_save` usa `src_dir = checked[0].parent` (`ui/main_window.py:520`), entao um lote com arquivos de pastas diferentes salva tudo so na pasta do 1º. Decidir saida por arquivo (ao lado de cada origem) ou destino unico explicito (alinha com a Sessao C).

### H0.5 Persistencia atomica para JSON de configuracao

- Criar helper reutilizavel (ex.: `core/json_store.py`) com escrita `tmp + fsync + replace`.
- **Reuso:** espelhar o padrao ja provado em `core/file_handler.py:76-89` (`write_atomic`) — nao inventar do zero.
- Usar helper em:
  - `save_preset` (pelo menos para novos CRUD/backup),
  - futuro `library_store`,
  - futuro `settings_store`.

### H0.6 Paridade GUI x CLI para `OnZeroMatches`

**Decisao tecnica (revisao 2026-06-01): modelo de linha rico.** O tweak original ("respeitar
em `_build_outcomes`") nao basta: a UI achata `Rule` em tupla de 4 (`ui/main_window.py:109`)
e descarta a politica mesmo de presets carregados (`:344,357`), entao `_build_outcomes`/`_rules_for`
nao tem o dado para agir.

- A UI para de achatar `Rule`: passa a **carregar/preservar `on_zero_matches` (+ `mode`/`priority`)**
  por regra — seed do preset; default `WARN` para linha adicionada na tela.
- Em `_build_outcomes`/preview: regra com `on_zero_matches=error` e **0 ocorrencias BLOQUEIA salvar**
  na GUI, identico a CLI (`cli.py:104,110-113`); `ignore` nao gera aviso; `warn` mantem o aviso atual.
- Beneficio colateral: preservar `mode`/`priority` evita degradar presets em silencio (hoje toda
  regra da UI vira `AUTO`/priority 100).
- Alternativas descartadas: *lookup minimo* (buscar politica pelo texto `find`) — fragil, quebra se
  o operador editar o `find`; *adiar+documentar* — mantem divergencia de seguranca GUI x CLI.
- A UI visivel pode seguir simples; a politica viaja com o dado e e enforçada. Um editor explicito
  da politica na tela e melhoria opcional posterior.

---

## 4. Plano de execucao detalhado por sessao

## Sessao A - Biblioteca geral de codigos + menu suspenso

**Objetivo:** parar de digitar pares repetitivos; selecionar e inserir com 1 clique.

### Implementacao

- Novo arquivo `core/library_store.py`:
  - `CodeEntry(find: str, replace: str, label: str = "", tags: list[str] = [])`
  - `load_library(path) -> list[CodeEntry]`
  - `save_library(path, entries) -> None` (via persistencia atomica)
  - validacoes:
    - `find` obrigatorio nao vazio;
    - sem duplicata exata (`find`, `replace`);
    - ordenacao estavel para facilitar diff.
- Em `app_paths.py`:
  - `library_path() -> Path`.
- Novo `ui/library_dialog.py`:
  - tabela com colunas `Buscar`, `Trocar por`, `Rotulo`;
  - botoes `Adicionar`, `Remover`, `Salvar`.
- Em `ui/main_window.py`:
  - botao `+ da lista` com menu pesquisavel;
  - acao `Gerenciar codigos...`;
  - inserir linha na tabela mantendo edicao manual ativa (complementar, nao substitui).

### Testes

- `tests/test_library_store.py`
  - carrega ausente -> lista vazia;
  - ignora/recusa item invalido sem `find`;
  - round-trip JSON;
  - deduplicacao.

### Criterio de aceite

- Operador consegue criar biblioteca e inserir pares sem digitacao livre.
- `pytest` verde.

---

## Sessao B - CRUD de perfis com backup e validacao forte

**Objetivo:** criar/duplicar/renomear/excluir perfil via GUI, sem editar JSON manual.

### Implementacao

- Em `core/preset_store.py`:
  - `create_preset(name, dir_path, template=None)`;
  - `duplicate_preset(src_path, new_name)`;
  - `rename_preset(src_path, new_name)`;
  - `delete_preset(path, trash_dir=None)` (ou exclusao direta com dupla confirmacao na UI);
  - `backup_before_write(path, keep=10)`.
- Regras de nome:
  - whitelist segura (`[A-Za-z0-9._- ]`);
  - bloquear nomes reservados (`CON`, `PRN`, etc., ambiente Windows);
  - bloquear path traversal.
- Em `ui/main_window.py`:
  - botoes `Novo`, `Duplicar`, `Renomear`, `Excluir`;
  - dialogos de confirmacao em 2 etapas para exclusao.

### Testes

- `tests/test_preset_crud.py`
  - criar/duplicar/renomear/excluir;
  - backup criado antes de sobrescrever;
  - retencao maxima de 10 backups por perfil;
  - nomes invalidos recusados.

### Criterio de aceite

- CRUD completo sem quebrar presets antigos.
- Falhas de JSON/validacao mostram erro amigavel, sem crash.

---

## Sessao C - Pasta de saida configuravel com persistencia

**Objetivo:** permitir salvar em destino escolhido e lembrar a ultima escolha.

### Implementacao

- Novo `core/settings_store.py`:
  - schema:
    - `schema_version: 1`
    - `output_mode: "ao_lado" | "fixa"`
    - `output_dir: string`
  - `load_settings(path)` com fallback seguro;
  - `save_settings(path, settings)` atomico.
- Em `app_paths.py`:
  - `settings_path() -> Path`.
- Em `core/file_handler.py`:
  - `make_output_dir(source_dir, profile, base_dir=None)`;
  - `base_dir=None` preserva comportamento atual.
- Em `ui/main_window.py`:
  - controle de destino (`Ao lado dos originais` / `Pasta fixa`);
  - botao para selecionar pasta;
  - mostrar destino efetivo antes de salvar.

### Testes

- `tests/test_settings_store.py`
- atualizar `tests/test_file_roundtrip.py` com caso `base_dir`.

### Criterio de aceite

- Destino persistido entre execucoes.
- Sem quebra no modo legado (`ao_lado`).

---

## Sessao D - Conferencia forte (antes e depois de salvar)

**Objetivo:** provar que as trocas previstas foram aplicadas e que o arquivo gravado manteve integridade.

### Implementacao

- Novo `core/conference.py`:
  - `build_planned_report(rules, match_count_by_rule, on_zero_policy)`
  - `recount_saved(text, rules, case_sensitive)` usando `compile_rule`;
  - `integrity_hash(text_before_save, text_after_readback)` com `sha256`.
- Fluxo:
  - antes de salvar: mostrar checklist por regra (`aplicado N`, `zero`, `bloqueado por policy`);
  - depois de salvar:
    - reler cada arquivo salvo (`read_file`);
    - recalcular contagem por regra;
    - comparar hash esperado x lido;
    - registrar no `SessionLog`.
- Em caso de divergencia:
  - alerta vermelho;
  - manter pasta de saida para auditoria;
  - marcar sessao como falha de conferencia.

### Testes

- `tests/test_conference.py`
  - regra com 0 match em `warn` e `error`;
  - recount correto em casos concatenados (`M6T1`, `G43H1T1`);
  - hash diverge quando arquivo foi alterado.

### Criterio de aceite

- Preview exibe conferencia legivel por arquivo/regra.
- Pos-salvar gera evidencia de integridade no log.

---

## Sessao E - Fechamento operacional

### Implementacao

- Regenerar EXE com `build_exe.ps1`.
- Garantir distribuicao de:
  - `data/presets`,
  - `data/library.json`,
  - `data/settings.json`,
  - `LEIA-ME`.
- Validacao final com arquivos reais (`prog/` + arquivos da fabrica).

### Criterio de aceite

- Fluxo completo via EXE sem Python instalado.
- Teste real assinado pelo operador (checklist manual concluido).

---

## 5. Regras tecnicas obrigatorias para evitar regressao

1. Nao alterar sem necessidade:
   - `core/matcher.py`
   - `core/replacement_plan.py`
   - `core/replacer.py`
2. Toda mudanca de persistencia deve ser atomica.
3. Toda nova opcao deve ter default compativel com versoes antigas.
4. Toda validacao de arquivo externo deve falhar com erro amigavel, nunca crash.
5. Toda sessao precisa terminar com:
   - `pytest` verde,
   - GUI abrindo,
   - `STATUS.md` e `00-HANDOFF.md` atualizados.

---

## 6. Matriz de testes (incremental)

## 6.1 Automatizados (obrigatorios)

- Suite atual (33) + novos testes das sessoes A-D.
- Novos cenarios de risco:
  - nomes duplicados no lote;
  - preset malformado;
  - `M300` nao contar como `M30`;
  - erro de encode em 1 arquivo bloqueia lote inteiro;
  - persistencia interrompida nao corrompe JSON.

## 6.2 Manuais (obrigatorios)

- Fluxo com `programas_teste`:
  - comum + por arquivo,
  - preview,
  - salvar,
  - releitura e conferencia.
- Fluxo com arquivos reais da fabrica:
  - validar dialeto Fanuc local,
  - validar tempo de execucao com lote real,
  - validar logs para auditoria.

---

## 7. Cronograma recomendado (com risco controlado)

1. Stage 0 (hardening base)  
2. Sessao A (biblioteca/menu)  
3. Sessao B (CRUD perfil)  
4. Sessao C (pasta de saida)  
5. Sessao D (conferencia forte)  
6. Sessao E (empacotamento e validacao real)

---

## 8. Referencias usadas para definir logica validada

## 8.1 Internas (fonte principal)

- `00-HANDOFF.md`
- `02-PRD_CNC_BatchEditor_v2.3.md`
- `cnc_batch_editor/core/matcher.py`
- `cnc_batch_editor/core/replacement_plan.py`
- `cnc_batch_editor/core/file_handler.py`
- `cnc_batch_editor/core/verifier.py`
- `cnc_batch_editor/core/preset_store.py`
- `cnc_batch_editor/ui/main_window.py`
- `cnc_batch_editor/tests/*`

## 8.2 Externas (benchmark de UX/fluxo)

- CIMCO Edit / Replace All from File
- Predator CNC Editor / File Compare
- CNC Syntax Editor / code repository
- TextCrawler / BinaryMark / Kutools (listas de replace salvas)

---

## 9. Definicao de pronto (DoD geral)

O plano sera considerado concluido quando:

1. Todas as sessoes A-E forem entregues sem regressao na suite existente.
2. Riscos criticos do Stage 0 estiverem resolvidos.
3. Conferencia antes/depois de salvar estiver ativa e registrada em log.
4. EXE final estiver validado com arquivos reais e aprovado no teste operacional.

