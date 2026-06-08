## Context

As Mudanças A (fundação visual) e B (layout 2 colunas + 4 componentes) estão arquivadas e verificadas. O protótipo `mockups/painel-final.v2.html` foi aprovado como contrato visual único na FASE 1. A FASE 2 reproduz esse contrato no app PySide6 — componente por componente — sem tocar em `flownc/core/` nem alterar sinais/slots existentes. Dados de exemplo fixos substituem chamadas reais onde necessário; a lógica de negócio é conectada na FASE 3.

Arquivos de UI existentes a modificar: `compositor.py`, `header.py`, `program_list.py`, `summary.py`, `editor_panel.py`, `theme.py`, `style.qss`.

## Goals / Non-Goals

**Goals:**
- Compositor no formato editlist com dois campos origem/destino, lista de edições, rascunho e CTA.
- Header fiel ao mockup: marca correta, botões no lugar certo, `+ Adicionar programas` no painel de programas.
- Lista de programas: um checkbox por linha, `.file.off`, estado "em edição" com botão `Voltar` contextual.
- Resumo: escopo `N programas`, ações clicáveis (stub), selo de backup em 2 linhas.
- Editor: glifos corretos, realce de todas as ocorrências via `QSyntaxHighlighter`, stepbar inline, Voltar em destaque.
- Tokens `theme.py`/`style.qss` sincronizados 1:1 com o protótipo.
- Todos os testes (pytest), mypy e ruff passam ao fim.

**Non-Goals:**
- Lógica de negócio real (publicar lote, salvar perfil, arrastar-e-soltar funcional, busca real na biblioteca).
- Mudanças em `flownc/core/`.
- Empacotamento do EXE (FASE 3).
- Modais de overlay de publicação (Passo 6 / Mudança D).

## Decisions

**D1 — Compositor: dois campos independentes em vez de um par**
O mockup define `origem` e `destino` como `QComboBox` separados (cada um com a lista da biblioteca). O modelo de dados usa `replace=""` de propósito — o destino é escolhido pelo operador na hora. A linha em-edição (rascunho) fica sempre no final da lista `editlist`; ao confirmar, move para a lista montada. Razão: segue o contrato visual aprovado e o modelo "dicionário de códigos" (não pares prontos).

**D2 — Realce de ocorrências: QSyntaxHighlighter**
Usar `QSyntaxHighlighter` ligado ao documento do `QPlainTextEdit` para realçar todas as ocorrências com `--color-occurrence` e a ocorrência atual com `--color-occurrence-current`. Alternativa descartada: `ExtraSelections` exige recalcular a cada scroll e é mais frágil com documentos grandes. O `QSyntaxHighlighter` é reavaliado só quando o documento muda.

**D3 — Stepbar "Um a um": widget inline em vez de QMessageBox**
Trocar o `QMessageBox` atual por um `QWidget` de stepbar inline no `editor_panel` com botões `← Anterior` / `→ Próxima` / `Substituir` / `Encerrar`. Razão: o mockup exige esse padrão e o `QMessageBox` bloqueia o loop de eventos, impedindo realce visual durante a navegação.

**D4 — Botão Voltar contextual na lista de programas**
Cada linha da `program_list` já tem `btn_edit` (`QPushButton`). Quando o arquivo está aberto no editor, trocar texto+estilo do botão para `Voltar` (estilo neutro/secundário). Ao clicar, emitir sinal `file_editor_close_requested` que o maestro (`main_window`) recebe — o mesmo caminho que o botão `Voltar` do `editor_panel`. Razão: aproveita infraestrutura existente sem novo sinal.

**D5 — `+ Adicionar programas` no painel de programas**
Remover `Abrir pasta`/`Abrir programa(s)` do header e mover a funcionalidade para um botão `+ Adicionar programas` no cabeçalho do `program_list`. Na FASE 2, o botão existe com `setEnabled(True)` e chama os mesmos handlers já existentes em `main_window.py` (`_open_folder`/`_open_files`). O arrastar-e-soltar fica como stub visual (aceita o drop, exibe mensagem de orientação; a lógica real vai na FASE 3).

**D6 — Tokens: sincronização como substituição, não adição**
Ler todas as variáveis `--color-*`, `--t-*`, `--sp-*`, `--radius-*`, `--h-*`, `--dim-*` do protótipo e sobrescrever os valores em `theme.py` e `style.qss`. Não criar novos seletores — só atualizar valores existentes e adicionar os tokens que faltam. Razão: garantir fidelidade pixel a pixel sem risco de divergência.

## Risks / Trade-offs

- [Realce de ocorrências pesado em arquivos grandes] → Desativar o highlighter acima de 5.000 linhas; exibir aviso na toolbar.
- [Checkbox duplicado origina de dois widgets diferentes no delegate] → Identificar o widget real (QCheckBox vs delegate paint) antes de remover; rodar o app entre cada remoção.
- [Sinal quebrado ao refatorar compositor] → Manter assinaturas exatas dos sinais existentes; usar `grep` nos `connect()` de `main_window.py` antes de remover qualquer widget.
- [Teste de smoke falha após mudança de botão contextual] → `test_ui_smoke.py` instancia `MainWindow`; se o botão `Voltar` só aparecer após abrir o editor, o smoke não deve quebrar — verificar no gate de testes.
