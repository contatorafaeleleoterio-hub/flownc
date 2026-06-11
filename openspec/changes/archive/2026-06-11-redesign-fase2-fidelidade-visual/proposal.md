## Why

O protótipo `mockups/painel-final.v2.html` foi aprovado como contrato visual único (FASE 1 concluída). Agora é necessário reproduzir esse contrato no app PySide6, tela por tela, sem alterar lógica de negócio — somente layout, estilo e dados de exemplo fixos.

## What Changes

- **Compositor:** reescrever `compositor.py` no formato `editlist`/rascunho com dois campos separados (origem e destino), lista "Edições montadas (N)", linha em-edição com `✕` por linha, botão "+ adicionar outra edição" e CTA "Adicionar edição ao lote →".
- **Header:** corrigir marca para `FlowNC`/subtítulo do mockup; mover `Abrir pasta`/`Abrir programa(s)` para o painel de programas como `+ Adicionar programas` (com arrastar-e-soltar e estado vazio com CTA); `Salvar perfil` à esquerda; `+ Adicionar código` azul sólido.
- **Resumo:** escopo `N programas`; ações dos cards (`✎ ⧉ 🗑`) clicáveis (stub); selo de backup em escudo + 2 linhas.
- **Lista de programas:** remover checkbox duplicado; aplicar `.file.off` na linha desmarcada; título `Seleção de Programas`; metadados relativos; estado "em edição" na linha aberta no editor com botão contextual `Voltar`.
- **Editor:** glifos `🔍`/`↑↓`; separar labels `Substituir` + `por`; botão `💾 Salvar`; realçar **todas** as ocorrências da busca; stepbar inline para "Um a um"; `✕ Voltar ao resumo` proeminente no topo-esquerdo.
- **Tokens:** sincronizar `theme.py` e `style.qss` 1:1 com as variáveis CSS do protótipo (todas as `--color-*`, `--t-*`, `--sp-*`, `--radius-*`, `--h-*`, `--dim-*`).

## Capabilities

### New Capabilities

- `compositor-editlist`: Compositor no formato editlist/rascunho — dois campos origem/destino separados, lista "Edições montadas", linha em-edição com ✕, botão adicionar e CTA do painel 2.
- `lista-programas-fidelidade`: Correções visuais da lista de programas — checkbox único, .file.off, título correto, metadados relativos, estado "em edição" com botão Voltar contextual.

### Modified Capabilities

- `fundacao-visual`: Sincronizar tokens de `theme.py` e `style.qss` 1:1 com o protótipo aprovado (variáveis CSS completas).
- `layout-principal`: Fidelidade de header (marca, botões, posições) e Resumo (escopo, ações clicáveis, selo de backup).
- `editor-de-arquivo`: Fidelidade visual do editor — glifos, labels, 💾 Salvar, realce de todas as ocorrências, stepbar inline, Voltar proeminente.

## Impact

- `flownc/ui/components/compositor.py` — reescrita completa da camada visual.
- `flownc/ui/components/header.py` — ajustes de marca, posição de botões e remoção de Abrir pasta/programa(s).
- `flownc/ui/components/program_list.py` — remoção de checkbox duplicado, estilos .file.off, botão Voltar contextual.
- `flownc/ui/components/summary.py` — escopo, ações clicáveis (stub), selo de backup.
- `flownc/ui/editor_panel.py` — glifos, realce de ocorrências (QSyntaxHighlighter), stepbar, Voltar em destaque.
- `flownc/ui/theme.py` e `flownc/ui/style.qss` — sincronização de tokens.
- Sem alterações em `flownc/core/` — lógica de negócio intocada.
