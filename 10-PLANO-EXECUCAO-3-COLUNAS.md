# 10 — PLANO DE EXECUÇÃO — Interface "3 Colunas" (dinâmica por código)

**Projeto:** CNC Batch Editor.
**Status:** plano aprovado para implementação (a executar, uma mudança por vez via OpenSpec).
**Data:** 2026-06-03
**Revisão:** 2026-06-03 — confrontado com o código real (`matcher.py`, `replacement_plan.py`, `file_handler.py`, `models.py`). · **2026-06-04** — política de salvamento vira **publicação na pasta de trabalho + backup versionado** (decisão #5). Mudanças resumidas em §9.
**Fontes:** `08-WORKFLOW-NOVA-DINAMICA.md` (dinâmica) + `09-DESIGN-3-COLUNAS.md` (visual) + código atual (`core/` estável, 106 testes).

---

## 0. Decisões travadas (não reabrir)

| # | Decisão | Escolha do Rafael (2026-06-03) |
|---|---|---|
| 1 | **Varredura prévia** (contar ocorrências por arquivo antes de executar) | **SIM, em segundo plano (QThread) desde já** — robusto para lotes grandes |
| 2 | **"Retirar" — limpeza de linha** | **Tira o código + junta espaços; linha que ficar vazia é apagada** |
| 3 | **Interface nova** | **2 fases** — 3a (Substituir) primeiro, 3b (Retirar + conflito + animações) depois |
| 4 | **Biblioteca de códigos** | **Catálogo padrão de mercado + migra o perfil atual** |
| 5 | **Salvamento / publicação** | **Publica o editado direto na pasta de trabalho (a que a máquina lê — fixa, configurável, pode ser de rede); os originais vão para uma pasta de backup configurável, versionada por data/hora. Fluxo único (sem pasta `_processado_` paralela), troca atômica à prova de falha.** |

> **Nota de revisão (substitui trava antiga):** o `08`/handoff antigo registrava *"Sem varredura (rejeitado por complexidade)"* como decisão a **não** reabrir. A **decisão #1 acima a substitui** — a varredura **entra**, em 2º plano. O `00-HANDOFF.md` foi corrigido para refletir isso (sem contradição entre os documentos).

> **Nota de revisão #2 (2026-06-04 — substitui trava antiga de salvamento):** o handoff registrava *"Salvar = COMO HOJE (pasta nova, original nunca tocado); rejeitada pasta fixa/sobrescrever"*. A **decisão #5 a substitui** — o app agora **publica na pasta de trabalho + faz backup versionado dos originais**, decidido por Rafael (2026-06-04) para eliminar o trabalho manual de mover arquivos. Segurança **preservada**: o original nunca se perde (backup versionado, cada execução = pasta nova) e a troca é **atômica** (a pasta da máquina nunca fica sem o programa).

---

## 1. Estratégia geral

**Fatia vertical, uma mudança por vez** (a mesma filosofia que já deu certo). Parte arriscada e pura primeiro (motor, 100% testável); interface grande por último. Cada mudança é uma proposta OpenSpec independente, com testes e DoD próprios.

```
 Mudança 1            Mudança 2             Mudança 3 (Fase 3a)        Mudança 4 (Fase 3b)
 ┌──────────────┐     ┌──────────────┐      ┌────────────────────┐     ┌────────────────────┐
 │ MOTOR:       │     │ BIBLIOTECA   │      │ UI 3 COLUNAS +     │     │ UI: RETIRAR +      │
 │ Retirar +    │     │ código+função│      │ SUBSTITUIR +       │     │ AVISO DE CONFLITO  │
 │ contagem +   │ ──▶ │ + variações  │ ──▶  │ VARREDURA (2º plano│ ──▶ │ + estados/anima-   │
 │ validadores  │     │ + catálogo   │      │ ) + Executar/Salvar│     │ ções (polimento)   │
 │ (core puro)  │     │ + migração   │      │ + pop-up resumo    │     │                    │
 └──────────────┘     └──────────────┘      └────────────────────┘     └────────────────────┘
   testes core          testes + diálogo      a fatia grande (MVP)        depende de 1 e 3
   RISCO médio          RISCO baixo           RISCO alto                  RISCO médio

 Dependências: 3 depende de 1 (contagem) e de 2 (dropdowns + forma normalizada). 4 depende de 1 (Retirar) e de 3 (tela).
 Ordem: 1 → 2 → 3 → 4 → (futuro) Verificações.
```

---

## 2. O que se reaproveita vs. o que muda

**Reaproveitado intacto (NÃO mexer):**
- `core/session_log.py` (log) · `core/replacer.py` (`apply_edits`) · `core/replacement_plan.py` (substituição + conflitos) · `core/matcher.py` (boundary CNC) · `core/preset_store.py` · `core/json_store.py`.
- Do `core/file_handler.py`: leitura/encoding/EOL e a **escrita atômica** (`_write_bytes_atomic`/`os.replace`) — base reusada pela publicação. Do `core/conference.py`: o SHA-256 (`verify_saved`) — reusado, agora aplicado **duas vezes** (backup + publicado).

**Muda / nasce:**
- `core/`: **Retirar** como **troca-por-vazio + faxina de linha** (reusa o motor de matching/conflito já testado), **contagem por arquivo** (novo), **validadores de lote** (novo), **publicação segura** (novo `core/publisher.py`: backup versionado + troca atômica + dupla conferência).
- `core/settings_store.py`: ganha **pasta de trabalho** (da máquina) + **pasta de backup**, persistentes (reusa a infra da Sessão C).
- **Biblioteca**: novo modelo (código + função + variações) + catálogo + migração + contrato "forma normalizada".
- **UI**: reescrita para 3 colunas + **threading** (varredura/execução/publicação em 2º plano) + **diálogo de configuração das pastas**.
- Invariante **"o original nunca se perde"**: antes "pasta nova"; agora **backup versionado** + troca atômica + conferência dupla + log. (O original sai da pasta de produção, mas é preservado no backup.)

---

## 3. "Tudo que vai precisar" (infraestrutura e dependências)

| Item | O que é / por quê | Decisão |
|---|---|---|
| **Fontes IBM Plex Sans + Mono** | O design usa essas fontes. No EXE offline não dá pra depender da web. | **Embutir** os arquivos `.ttf` (licença OFL, livre) em `cnc_batch_editor/assets/fonts/` e carregar via `QFontDatabase.addApplicationFont` no `main.py`, com **fallback** `system-ui`/`monospace` se faltar. |
| **Threading (QThread)** | Varredura e execução em 2º plano (decisão #1), com animações sem travar a tela. | Camada nova `ui/workers.py` (padrão `QObject` + `moveToThread`): `ScanWorker` (conta ocorrências, cancelável) e `ExecuteWorker` (planeja+grava+confere). Sinais Qt: `progress`, `result`, `error`, `finished`. |
| **Ícones (SVG)** | Check, caret, lápis, duplicar, lixeira, escudo, parafusos. | Pequeno conjunto SVG embutido em `assets/icons/` (ou Unicode + QStyle como fallback). Sem dependência externa. |
| **Janela / responsividade** | Design 1340×884; col 2 cresce. | Janela abre num tamanho confortável (ex.: 1280×860) **redimensionável**; col 1 e 3 fixas, col 2 elástica. (Abrir maximizada = opcional.) |
| **Migração de preset** | Perfis hoje guardam `global_rules`/`file_rules`. | Ao carregar perfil: regras viram **cartões** no lote (sem programas, §6.4 do 08). Programas começam vazios. Sem perder presets existentes. |
| **Pasta de trabalho + backup** | A máquina lê de uma pasta fixa (pode ser de rede); o editado é publicado lá e o original vai pro backup. | Duas pastas **configuráveis e persistentes** em `settings_store` (reusa a infra da Sessão C + `base_dir`) + diálogo "Configurar pastas". O `.tmp` da troca atômica fica **na própria pasta de trabalho** (mesmo volume → atômico mesmo em rede); o **backup** pode ser em qualquer lugar (é cópia). |
| **Testes headless** | GUI roda offscreen (já existe `test_ui_smoke.py`). | Estender para a tela nova; testar lógica dos workers **sem** loop de eventos quando possível (funções puras de `core/scan` e `core/line_cleanup`). |
| **Rebuild do EXE** | Empacotar fontes/ícones; checar SmartScreen. | Atualizar `build_exe.ps1` para incluir `assets/`; smoke test do EXE; alertar sobre antivírus (EXE não assinado). |

---

## 4. As mudanças, uma a uma

### ▶ Mudança 1 — Motor: "Retirar" + contagem + validadores + **publicação segura**  *(core puro/sensível)*

- **Objetivo:** dar ao motor, de forma testada, (a) o **"Retirar"** reusando o motor de substituição já existente — *"retirar X"* = trocar X por **vazio** + uma **faxina de linha** —, (b) a **contagem de ocorrências por arquivo** (base da varredura), (c) as **travas de lote**, (d) a **publicação segura** (gravar o editado na pasta de trabalho + backup versionado do original, à prova de falha).
- **Depende de:** nada.
- **Nota de tamanho:** se Retirar + publicação ficarem grandes juntos, dividir em **1a** (Retirar/scan/batch) e **1b** (publicação/backup) — ambos core puro/sensível.
- **A sacada (por que NÃO há motor novo de remoção):** "Retirar M6" é modelado como `Rule(find="M6", replace="", action=RETIRAR)`. Assim o `build_plan`/`apply_edits` **já existentes** fazem o trabalho pesado e **já coberto por testes**:
  - acham `M6` com o **boundary CNC** (`(?<![A-Z])…(?![0-9.])`, não pega `M60`/`M6.5`) — herdado, sem recodar;
  - resolvem **conflito de pedaço** com outras regras (`Suppression`, vencedor por scope→priority→ordem) — herdado;
  - compõem o resultado, então **lote misto** (ex.: `M8→M08` **e** `retirar M6` no mesmo arquivo) **sai pronto**, sem inventar junção.
  - A **única** parte realmente nova é a **faxina de linha** (função pura, testável isolada).
- **Mexe em / nasce:**
  - `core/models.py` — `Action = SUBSTITUIR | RETIRAR`; `Rule` ganha `action: Action = SUBSTITUIR` (campo novo com default → back-compat dos presets). `ScanResult` (contagem por arquivo **+ agregado** "X de Y arquivos contêm"). `Issue` (validação de lote). *(Sai o `RemovalResult`: não há mais motor de remoção próprio.)*
  - `core/line_cleanup.py` *(novo, pura)* — `clean_removed_lines(text, removed_line_idxs) -> CleanupResult`: faz a faxina (regras abaixo) e devolve texto novo + linhas afetadas + pares (antes→depois) p/ o preview.
  - `core/replacer.py` / `replacement_plan.py` — **ponto de integração mínimo:** depois de compor o texto, se houve edits de ação RETIRAR, rodar a faxina **escopada às linhas do resultado** que receberam remoção (`apply_edits` passa a devolver quais linhas do resultado foram tocadas por um RETIRAR).
  - `core/scan.py` *(novo)* — `count_occurrences(find, mode, case_sensitive, files, read_fn) -> ScanResult`, reusando `find_matches`. `read_fn` injetável (testável sem disco).
  - `core/batch.py` *(novo)* — `validate_batch(rules, library) -> list[Issue]`: **conflito de regra** (≥2 regras no mesmo código de origem → âmbar) · 1 Retirar por execução · allowlist (só código válido da biblioteca). *(Distinto do "conflito de pedaço" do `Suppression` — ver Mudança 4.)*
  - `core/publisher.py` *(novo, sensível)* — `publish_batch(working_dir, backup_dir, items, read_fn) -> PublishResult`. Por arquivo que **mudou**: grava `.tmp` na pasta de trabalho → confere SHA → **copia** o original → `backup_dir/_backup_orig_DATA_HORA/` + confere → `os.replace` atômico (`.tmp` → nome final) → confere o publicado → log. **Nunca** deixa a pasta de trabalho sem o arquivo; só toca o que mudou; `replace` só no mesmo share (backup é cópia, aguenta outro volume).
  - `core/settings_store.py` — `working_dir` + `backup_dir` (persistentes).
- **Faxina de linha** (decisão #2) — aplicada **só nas linhas que tiveram remoção**:
  1. (achar + remover o trecho já vêm do `build_plan`/`apply_edits` — boundary herdado.)
  2. Juntar 2+ espaços/tabs em 1; tirar espaço no fim; tirar espaço sobrando no começo.
  3. Se a linha ficou **vazia por causa da remoção**, apagar a linha (e a quebra). **Não** mexer em linha que já era vazia.
  4. **Preservar o EOL** (`\r\n`/`\n`) do arquivo (vem de `EncodingInfo`).
- **Detalhe de assinatura:** `find_matches(text, rule, case_sensitive)` recebe um **`Rule`** (precisa `id/find/replace`), não `(code, mode)` solto → o `scan.py` constrói um `Rule` descartável **ou** se extrai um helper `find_spans(text, find, mode, case_sensitive)`. Decisão na implementação.
- **Vetores de teste (exemplos):** `N50 M6 T0101`→`N50 T0101` · `M6` sozinho → linha some · `M6T1`→`T1` · `M8 M6 M9`→`M8 M9` · `M60` **não** é tocado ao retirar `M6` · linha vazia pré-existente mantida · EOL preservado · **lote misto** (`M8→M08` + retirar `M6`) compõe certo · **conflito** Substituir×Retirar no mesmo trecho resolvido por `Suppression`.
- **Testes:** `tests/test_line_cleanup.py`, `tests/test_scan.py`, `tests/test_batch_validate.py`, **`tests/test_publisher.py`** (backup versionado · troca atômica · só toca o que mudou · falha simulada deixa a produção intacta · backup em outro volume), + 1 de integração "Retirar dentro do `build_plan`".
- **Riscos:** a faxina **não pode** colapsar espaços de linhas **não tocadas** (escopo por nº de linha do resultado); apagar linha muda offsets → rodar a faxina sobre o **texto já composto**, indexada por nº de linha (não por offset). **Publicação é destrutiva na produção** → ordem à prova de falha + backup versionado + dupla conferência; cobrir com teste de interrupção simulada (a pasta de trabalho nunca pode ficar sem o arquivo).
- **Pronto quando:** testes novos verdes · `mypy --strict` limpo · vetores do Retirar passam · lote misto compõe · **publicação testada** (backup versionado + troca atômica + dupla conferência; falha simulada não corrompe a produção) · "o original nunca se perde" preservado.

---

### ▶ Mudança 2 — Biblioteca código-cêntrica + catálogo + migração  *(dados + diálogo)*

- **Objetivo:** transformar a biblioteca de "pares find/replace" em **dicionário de códigos** (código + função + variações por máquina), já vindo com catálogo de mercado.
- **Depende de:** nada (independente da Mudança 1).
- **Mexe em / nasce:**
  - `core/library_store.py` — novo modelo `LibraryCode { code, function, variants: dict[perfil, grafia] }`; `load/save`; `migrate_legacy(antigo) -> novo`; `default_catalog() -> list[LibraryCode]`. **Reusar `core/json_store.py`** (já existe) para load/save — não reinventar serialização.
  - `ui/library_dialog.py` — editar código/função/variações; "Adicionar código" + "+" (salvar no perfil ou global).
  - `data/library/` — catálogo padrão em JSON.
- **Contrato p/ a Mudança 3 (congelar aqui):** dado um código de origem e o perfil atual, a biblioteca sabe devolver a **forma normalizada** (o "Trocar por" sugerido) — ex.: `normalized_form("M8", perfil) -> "M08"` via `variants[perfil]`. A Mudança 3 depende disso para preencher o dropdown "Trocar por" e o banner "config montada". Definir e testar **nesta** mudança.
- **Catálogo padrão (semente):** M3/M4/M5 (liga/desliga árvore), M8/M9 (fluido), M6 (troca ferramenta), M30/M2 (fim), G0/G1/G2/G3, G54–G59 (origens), G90/G91, T.., S.., F.. — cada um com função em PT-BR. (Lista revisada com o validador CNC.)
- **Migração:** o `MAZAK_VTC530.json` atual (M08, M07, G54, T1) é convertido para o novo formato sem perder nada; variações (M8↔M08) viram `variants`.
- **Testes:** `tests/test_library_store.py` (ampliar): carregar/salvar/migrar/catálogo; `normalized_form`; back-compat com o JSON antigo.
- **Riscos:** baixo. Cuidar da migração não apagar dados antigos.
- **Pronto quando:** testes verdes · diálogo abre e edita · catálogo carrega · perfil antigo migra · contrato `normalized_form` definido e testado.

---

### ▶ Mudança 3 (Fase 3a) — UI 3 colunas + Substituir + varredura + executar/salvar  *(a fatia grande / MVP)*

- **Objetivo:** entregar a **tela do `09`** funcionando ponta a ponta com a ação **Substituir**, varredura em 2º plano e o ato de gravar com pop-up de resumo.
- **Depende de:** Mudança 1 (contagem) + Mudança 2 (biblioteca para os dropdowns + `normalized_form`).
- **Mexe em / nasce:**
  - `ui/main_window.py` — **reescrita** para 3 colunas (header + col1 compositor + col2 programas + col3 resumo). Estado de sessão: regras (cartões) + programas (efêmeros).
  - `ui/workers.py` *(novo)* — `ScanWorker` (varredura cancelável) e `ExecuteWorker` (planeja → grava → confere → log).
  - `ui/preview_dialog.py` — vira o **pop-up de resumo** (Executar → Analisar → Resumo → Publicar).
  - `ui/settings_dialog.py` *(novo)* — configurar **pasta de trabalho** (da máquina) + **pasta de backup** (reusa `settings_store`); valida caminho/acesso.
  - `ui/workers.py` — `ExecuteWorker` chama `core/publisher` (publicação em 2º plano; rede pode ser lenta → progresso por arquivo).
  - (opcional) `ui/widgets/` — `rule_card.py`, `program_row.py` para organizar.
  - `main.py` — carregar fontes IBM Plex; manter o `sys.excepthook` global (caixa de erro).
  - `assets/fonts/`, `assets/icons/` — recursos.
- **Marcos internos (ordem de construção):**
  1. Layout estático **2 colunas** (design B / §0 do `09`): esquerda empilhada (① compositor **horizontal/baixo** + ② programas **grande**) + ③ resumo **dominante** à direita (altura inteira). + tokens de cor/fonte do `09`.
  2. Compositor (col 1): dropdown de **código de origem** (da biblioteca) → banner "config montada". O "Trocar por" **exclui o código de origem** da lista e vem pré-preenchido com a **forma normalizada** (contrato da Mudança 2).
  3. Programas (col 2): "Adicionar programa(s)…" popula a lista (síncrono).
  4. **Varredura em 2º plano:** ao escolher o código, `ScanWorker` conta ocorrências e preenche os chips (`✓ N` / `▲ 0`) **+ o match-banner agregado** ("✓ 5/6 programas contêm M8", do `ScanResult`); 0 ocorrências **desmarca** o arquivo. **Progresso visível** (spinner/parcial) e cancela/reinicia se o código mudar.
  5. "Adicionar regra ao lote" → cria **cartão** (col 3), soma contadores, reseta col 2. **Trava de corrida (produto):** o botão fica **desabilitado enquanto a varredura ainda roda** (senão o contador "Alterações" sairia indefinido).
  6. **Configurar pastas:** diálogo define **pasta de trabalho** (da máquina) + **pasta de backup**; persistem em `settings_store`. Se faltar configuração, pedir antes de publicar.
  7. **Executar lote** → `ExecuteWorker` (anim. "Executando… Analisando…") → **pop-up de resumo** (com preview) → **Publicar** (anim. "Publicando…") → `core/publisher`: **backup versionado + troca atômica + dupla conferência** + log → **abre a pasta de trabalho**. Só os arquivos que **realmente mudaram** são tocados.
- **Testes:** ampliar `tests/test_ui_smoke.py` (construção da tela nova, fluxo Substituir headless); teste de fumaça do `ScanWorker`/`ExecuteWorker` (lógica via `core/`).
- **Riscos:** maior. Threading (condições de corrida na varredura ao trocar código rápido) · reescrita grande da `main_window` · **proposta grande** — considerar dividir o 3a em **3a-casca** (layout+tokens estáticos, sem lógica) e **3a-fluxo** (varredura+publicação) se a fatia ficar pesada demais para uma revisão. Mitigar: lógica pesada fica em `core/` (puro/testável); a UI só orquestra.
- **Pronto quando:** smoke test verde · fluxo **Substituir** completo (configurar pastas → escolher código → varredura → adicionar regra → executar → resumo → **publicar na pasta de trabalho** → **backup versionado** dos originais → abre a pasta) · **dupla conferência SHA-256** (backup + publicado) no log · selo reflete "Originais → backup; editados publicados" · **validação manual do Rafael**.

---

### ▶ Mudança 4 (Fase 3b) — UI: Retirar + aviso de conflito + polimento  *(fecha a dinâmica)*

- **Objetivo:** ligar a ação **Retirar** (motor da Mudança 1) na tela e fechar segurança/estados.
- **Depende de:** Mudança 1 (Retirar) + Mudança 3 (tela).
- **Mexe em:** `ui/main_window.py` (segmentado Substituir/Retirar; esconder "Trocar por"; trava visual), `ui/preview_dialog.py` (preview obrigatório das linhas afetadas pelo Retirar), `core/batch` (já feito na M1) ligado à UI.
- **Tarefas:** trava do Retirar (1 por execução · allowlist · preview obrigatório · bloqueio por conflito · log) · **aviso de conflito de regra** (âmbar) quando ≥2 regras mexem no mesmo código de origem — vem do `validate_batch` (Mudança 1); **distinto** do "conflito de pedaço" (`Suppression`) que o motor já resolve sozinho · **preview do Retirar** mostra explicitamente *"esta linha será APAGADA"* (modo visual novo no `preview_dialog`, diferente do diff de troca) · estados de cor/ícone (verde/âmbar/vermelho) · animações de progresso · mensagens de erro acionáveis.
- **Testes:** smoke do fluxo Retirar (preview mostra linhas afetadas; bloqueio por conflito); conflito entre regras.
- **Riscos:** médio (ação destrutiva na ponta). Mitigado pela cobertura da Mudança 1 + preview obrigatório.
- **Pronto quando:** Retirar funciona com todas as travas · conflito avisado · validação manual do Rafael.

---

### ▶ Futuro (fora deste plano) — Verificações como porteiro no resumo

Reintroduzir as verificações configuráveis (deve existir / não pode existir / contagem) como **porteiro no pop-up de resumo** (bloqueia Salvar se uma verificação crítica falhar). Rodar sobre o **resultado**, não sobre o original (achado técnico do handoff). `core/verifier.py` já existe.

---

## 5. Estratégia de testes

- **Núcleo (puro):** vetores para a **faxina do Retirar** (M1) + integração "Retirar no `build_plan`" (lote misto, conflito), contagem (M1), validadores (M1), biblioteca/migração + `normalized_form` (M2). É onde mora o risco real → cobertura forte.
- **GUI (headless/offscreen):** `test_ui_smoke.py` ampliado por fase (construção + fluxo).
- **Workers:** isolar a lógica em `core/` (testável sem Qt); o worker só "embrulha".
- **Manual (só o Rafael):** validação no chão de fábrica com arquivos reais, conferindo o `_log.txt` (seção `CONFERENCIA POS-SALVAMENTO`).
- **Regra de ouro:** nenhuma mudança no `core/` entra sem teste novo; "original nunca alterado" reverificado a cada fase.

---

## 6. Riscos globais e mitigações

| Risco | Mitigação |
|---|---|
| Reescrita grande da `main_window` | Lógica pesada em `core/`; UI só orquestra; construir por marcos (§4, Mudança 3); dividir 3a se preciso. |
| Threading (corrida ao trocar código rápido) | Worker cancelável; ignorar resultado de varredura obsoleta (token de geração). |
| Corrida de produto (somar regra antes da varredura) | Botão "Adicionar regra" desabilitado enquanto a varredura roda (§4, Mudança 3, marco 5). |
| Remoção destrutiva (Retirar) | Reuso do motor testado (boundary + conflito) + faxina coberta por vetores (M1) + preview obrigatório + bloqueio por conflito + log. |
| Lotes muito grandes | Varredura/execução em 2º plano (já decidido) + progresso visível. |
| **Publicar mexe na produção** (energia/falha no meio) | Fluxo à prova de falha (`publisher`): `.tmp` → confere → backup → `os.replace` atômico → confere. A pasta da máquina **nunca** fica sem o arquivo. |
| **Republicar na mesma pasta** (origem = destino) | **Backup versionado por data/hora** → o original verdadeiro nunca se perde (cada execução = pasta nova). (Rafael dispensou aviso prévio.) |
| **Pasta de trabalho em rede** (lenta/instável) | Publicação em 2º plano; `.tmp` no mesmo share (troca atômica); backup pode ser local. |
| Fontes ausentes no EXE | Embutir IBM Plex + fallback `system-ui`/`monospace`. |
| SmartScreen/antivírus (EXE não assinado) | Avisar; falso positivo do `onedir`; checar no PC alvo. |

---

## 7. Checklist macro (ordem de execução)

- [ ] **Mudança 1** — `core/line_cleanup.py` + `core/scan.py` + `core/batch.py` + **`core/publisher.py`** + `Action`/`ScanResult`/`Issue` nos models + `settings` (pasta trabalho/backup) + integração Retirar no `build_plan` + testes → verdes + mypy.
- [ ] **Mudança 2** — biblioteca nova + catálogo + migração + `normalized_form` + `library_dialog` + testes.
- [ ] **Mudança 3 (3a)** — tela 3 colunas + Substituir + varredura 2º plano + **diálogo de pastas** + executar → **publicar na pasta de trabalho + backup versionado** + pop-up + abre pasta → smoke + validação manual.
- [ ] **Mudança 4 (3b)** — Retirar + conflito + estados/animações → smoke + validação manual.
- [ ] **Rebuild EXE** (fontes/ícones) + smoke + teste no pendrive.
- [ ] (futuro) Verificações porteiro.

---

## 8. Mapeamento OpenSpec (uma mudança por vez)

Cada Mudança vira **uma** proposta OpenSpec (`propose → apply → archive`), nesta ordem. Nomes sugeridos:

| Mudança | Nome OpenSpec sugerido |
|---|---|
| 1 | `motor-retirar-contagem-e-publicacao` (ou 1a/1b se dividir) |
| 2 | `biblioteca-codigo-funcao-variacoes` |
| 3 (3a) | `ui-3-colunas-substituir` |
| 4 (3b) | `ui-retirar-e-conflito` |

> **Próximo passo concreto:** criar a proposta OpenSpec da **Mudança 1** (proposal + design + tasks + specs), já com "Retirar = troca-por-vazio + faxina" **e a publicação segura** (`publisher` + backup versionado, §4). Só ao receber **"pode seguir"**.

---

## 9. O que mudou nesta revisão (2026-06-03)

Confronto do plano com o **código real** (`matcher.py`, `replacement_plan.py`, `file_handler.py`, `models.py`). Confirmado que as bases existem mesmo: boundary `(?<![A-Z])…(?![0-9.])`, `EncodingInfo.eol`, `find_matches`, `Suppression`. Ajustes feitos:

1. **Mudança 1 — "Retirar" deixou de ser motor novo.** Vira **troca-por-vazio + faxina de linha**, reusando `build_plan`/`apply_edits` (matching com boundary + conflito + composição de lote misto já testados). Sai o `core/remover.py`; nasce o `core/line_cleanup.py` (só a faxina é código novo). Resolve de quebra o "lote misto" (substituir + retirar no mesmo arquivo), que o desenho anterior não compunha.
2. **Contradição resolvida.** A trava antiga *"Sem varredura"* (handoff §9) foi **substituída** pela decisão #1 ("varredura SIM, 2º plano"). Handoff corrigido na mesma sessão.
3. **Dois sentidos de "conflito" separados:** *de pedaço* (`Suppression`, já no core) × *de regra* (≥2 regras no mesmo código de origem → âmbar, novo em `batch.py`).
4. **Mudança 2** congela o contrato `normalized_form(código, perfil)` (o "Trocar por" sugerido) e reusa `core/json_store.py`.
5. **Mudança 3:** `ScanResult` carrega o **agregado** "X de Y contêm"; "Trocar por" exclui a origem; **trava de corrida de produto** (não somar regra antes da varredura terminar); progresso visível; considerar dividir o 3a se ficar grande.
6. **Mudança 4:** preview do Retirar mostra *"linha será apagada"* (modo visual próprio, diferente do diff).
7. **Salvamento virou "publicação" (2026-06-04).** Em vez de gravar em pasta `_processado_` (que o operador movia na mão), o app **publica o editado direto na pasta de trabalho da máquina** (fixa/configurável, pode ser de rede) e **leva os originais para um backup versionado** (configurável). Fluxo único, troca **atômica** à prova de falha, **dupla conferência** (backup + publicado). Novo `core/publisher.py` + 2 pastas em `settings_store` (Mudança 1) + diálogo de pastas (Mudança 3). Substitui a decisão travada antiga "pasta nova / original nunca tocado" (decisão #5).
8. **Layout final = 2 colunas (design B, 2026-06-04).** A tela deixou de ser 3 colunas iguais (col 1 sobrava vazia). Vira **2 colunas**: esquerda empilhada (① compositor horizontal/baixo + ② programas grande) + ③ **resumo dominante** à direita (altura inteira), com o conflito em destaque. Spec no **§0 do `09`**; mockup fiel `mockups\12-mockup-bancada-resumo-dominante.html`. A **Mudança 3** (UI) implementa esse arranjo.
