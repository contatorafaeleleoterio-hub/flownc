# Contexto Atual

## Termos adotados (2026-06-06)

- **Plano de execução / plano de implementação:** criação de um documento com as etapas necessárias para executar uma solução já decidida. Vale para qualquer pedido de "plano", seja qual for o nome usado (stack, roteiro, documento etc.).
- **Implementação:** colocar a solução em funcionamento, executando o plano definido (por documentos, código, reprogramação ou reconstrução do zero — a forma não importa).
- **"Implementar o design":** refere-se **exclusivamente ao novo design aprovado** (`mockups/painel-final.v2.html`).
- **Design antigo: descartado.** Não é mais referência para nada. Menções a layouts antigos valem só como histórico.
- Plano de execução vigente: **`PLAN.md`** (raiz do projeto).

## Estado confirmado

- Projeto desktop Windows em Python 3.11+, com CLI e GUI PySide6.
- Núcleo `core/` está estável e coberto por testes.
- Baseline verificada em 2026-06-04: `106 passed`. **Atualizada em 2026-06-05: `121 passed`** após a mudança `editor-integrado-por-arquivo`.
- Existe EXE funcional antigo preservado em `flownc/dist` até o smoke do novo `FlowNC.exe`.
- O repositório Git foi inicializado em 2026-06-04 com baseline antes do rebrand.

## Editor integrado por arquivo — IMPLEMENTADO (2026-06-05)

Mudança OpenSpec `editor-integrado-por-arquivo` implementada (26/28 tarefas; faltam só
o smoke manual e o `/opsx:archive`):

- **`core/inplace_save.py`** (novo) — `salvar_no_lugar`: gravação in-place sem backup,
  atômica, com preflight de codificação e conferência SHA-256. Preserva encoding/BOM/EOL.
- **`ui/editor_panel.py`** (novo) — `EditorPanel` (editor mono com numeração de linha) +
  localizador que reusa `matcher.find_matches` (mesma borda CNC do Lote): varredura/contagem
  sem mover cursor, navegação i/N circular, substituir todos / um a um. Lógica de
  busca/substituição em funções puras testáveis.
- **`ui/main_window.py`** — botão "✎ Editar" por programa; área da direita virou
  `QStackedWidget` (tabelas/Lote ↔ editor); guarda de não-salvo. Fluxo de Lote inalterado.
- Detalhe importante: o `QPlainTextEdit` usa `\n` interno; o EOL real (CRLF) é reaplicado só
  na gravação, preservando byte-a-byte (travado por teste de regressão).

## Situação do produto

O produto já saiu do modelo antigo baseado em abas por programa e convergiu para uma dinâmica "por código", com composição de regras, seleção de programas e resumo dominante. O **design alvo é exclusivamente o mockup v2 aprovado** (`mockups/painel-final.v2.html`); qualquer layout anterior está **descartado** e vale apenas como histórico de evolução, nunca como referência de implementação.

## Situação da documentação

Antes desta consolidação, a documentação estava espalhada entre handoff, PRDs, análises, planos intermediários e mockups antigos. A estrutura em `docs/` passa a ser a fonte principal, enquanto o restante vai para `_descarte/` com índice rastreável.

## Próximos passos imediatos

### Prioridade 1 — Redesenho visual conforme o mockup v2 (plano ativo)

O mockup v2 (`mockups/painel-final.v2.html`) está **construído e aprovado**, e o **Editor integrado
por arquivo já foi implementado** (ver seção acima). O que falta agora é **portar o visual v2 para o
app Qt** — hoje o app ainda tem a cara antiga, apesar da função nova existir.

Plano (esqueleto, sessões → etapas): **`docs/PLANO-REDESIGN-VISUAL-V2.md`**.

Decisões estruturais fechadas:
- **Componentes separados** em `flownc/ui/components/` (quebrar a `MainWindow` monolítica de ~968 linhas).
- **Fluxo OpenSpec**, dividido em **3 mudanças sequenciais**:
  - **A — Fundação visual:** tokens (cores/fontes/espaçamentos) + tema/QSS aplicados ao app.
  - **B — Layout e painéis:** header + 2 colunas dinâmicas (60/40 ↔ 40/60) + coluna esquerda
    (Configurações + "Edições montadas") + coluna direita (Resumo).
  - **C — Editor, limpeza e entrega:** editor com cara final + remoções do v2
    (contagem automática, redundâncias) + integração + EXE novo.

Próxima ação concreta: **Sessão 0 da Mudança A** (proposta OpenSpec da fundação visual). O plano
ainda passará por uma rodada de refino de etapas antes de codar.

### Prioridade 2 — Gate do executável (não bloqueante)

`dist/FlowNC/FlowNC.exe` já existe e contém o editor, mas com o visual antigo. Smoke test manual,
entrega de cópia limpa na Área de Trabalho e afastamento da versão antiga
(`Desktop/CNC_BatchEditor/`, de 2026-06-01) ficam para o **fim do redesenho** (Sessão 7).

### Prioridade 3 — OpenSpec `motor-contagem-e-publicacao` — IMPLEMENTADO (2026-06-06)

Todos os grupos implementados via `/opsx:apply`:

- **Grupo 1–2** (`core/models.py`, `core/scan.py`): `ScanResult`, `Issue`, `count_occurrences` com boundary.
- **Grupo 3** (`core/batch.py`): `validate_batch` — detecta conflito de regra (≥2 regras no mesmo código).
- **Grupo 4** (`core/publisher.py`, `core/settings_store.py` v2): `publish_batch` — backup versionado por data/hora, troca atômica, dupla conferência SHA-256; settings migrado v1→v2 com `working_dir`/`backup_dir`.
- **Testes**: `test_scan.py` (5), `test_batch_validate.py` (4), `test_publisher.py` (9), `test_settings_store.py` (7) — todos verdes.

Próxima ação: `/opsx:archive motor-contagem-e-publicacao`.
