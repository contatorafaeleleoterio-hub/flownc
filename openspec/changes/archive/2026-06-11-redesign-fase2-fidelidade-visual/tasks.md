## 1. Sincronizar tokens theme.py e style.qss com o protótipo

- [x] 1.1 Ler todas as variáveis CSS `--color-*`, `--t-*`, `--sp-*`, `--radius-*`, `--h-*`, `--dim-*` do `mockups/painel-final.v2.html` e atualizar os valores correspondentes em `flownc/ui/theme.py` (incluir `COLOR_OCCURRENCE` e `COLOR_OCCURRENCE_CURRENT` que ainda faltam)
- [x] 1.2 Atualizar `flownc/ui/style.qss` referenciando os tokens de `theme.py`; garantir que nenhum valor hex/px fixo reste nos seletores de UI

## 2. Reescrever CompositorPanel (formato editlist)

- [x] 2.1 Em `flownc/ui/components/compositor.py`, substituir o layout atual por: título "1 Configurações", dois `QComboBox` separados (origem e destino) populados com `addItem(code, code)` + `setItemData(i, label, ToolTipRole)`, linha de rascunho (fundo `COLOR_BG_SUBTLE`, borda tracejada) sempre ao fim da lista
- [x] 2.2 Implementar a lista "Edições montadas (N)" com um `QWidget` por linha contendo label `origem → destino` e botão `✕`; conectar ✕ ao sinal `edicao_removida(index: int)`
- [x] 2.3 Adicionar botão `+ adicionar outra edição` que confirma o rascunho atual e move para a lista montada, atualizando o contador no título
- [x] 2.4 Adicionar CTA `Adicionar edição ao lote →` (desabilitado quando lista vazia; emite `adicionar_ao_lote()` ao clicar)
- [x] 2.5 Verificar que os sinais conectados em `main_window.py` (`connect()`) continuam funcionando com a nova assinatura do compositor

## 3. Corrigir HeaderBar e SummaryPanel

- [x] 3.1 Em `flownc/ui/components/header.py`, atualizar marca para `FlowNC` + subtítulo conforme mockup; mover `Salvar perfil` para a esquerda; aplicar `COLOR_INTERACTIVE` (azul sólido) no botão `+ Adicionar código`; remover botões `Abrir pasta` e `Abrir programa(s)` do header
- [x] 3.2 Em `flownc/ui/components/summary.py`, alterar label de escopo para `N programas` (usando dado real ou stub "0 programas"); transformar ações dos cards (`✎ ⧉ 🗑`) em `QPushButton` com sinais `regra_editar(int)`, `regra_duplicar(int)`, `regra_excluir(int)` (stubs)
- [x] 3.3 Em `summary.py`, atualizar o selo de backup para exibir ícone de escudo + 2 linhas de texto conforme o mockup

## 4. Corrigir ProgramListPanel

- [x] 4.1 Em `flownc/ui/components/program_list.py`, identificar e remover o checkbox duplicado (manter apenas o que conecta à seleção de lote); rodar o app para confirmar que apenas um checkbox aparece por linha
- [x] 4.2 Implementar estilo `.file.off` (propriedade QSS dinâmica ou `setProperty`) na linha de cada arquivo desmarcado; ligar ao sinal de toggle do checkbox
- [x] 4.3 Atualizar o título do painel para `Seleção de Programas`; atualizar metadados de cada linha para formato relativo (tamanho humanizado + tempo relativo via `humanize` ou cálculo manual)
- [x] 4.4 Adicionar botão `+ Adicionar programas` no cabeçalho do `ProgramListPanel`; conectá-lo aos handlers `_open_folder`/`_open_files` de `main_window.py`
- [x] 4.5 Implementar estado vazio da lista com CTA destacado ("Adicione programas para começar" ou equivalente do mockup)
- [x] 4.6 Implementar estado "em edição" na linha do arquivo aberto no editor: trocar texto+estilo do `btn_edit` para `Voltar` (estilo neutro); emitir `fechar_editor_solicitado()` ao clicar; voltar ao `✎ Editar` ao fechar o editor
- [x] 4.7 Conectar o sinal `fechar_editor_solicitado()` em `main_window.py` para fechar o editor (mesmo caminho do botão Voltar do `editor_panel`)

## 5. Corrigir EditorPanel (glifos, realce, stepbar, Voltar)

- [x] 5.1 Em `flownc/ui/editor_panel.py`, atualizar o botão `Voltar ao resumo` para posição topo-esquerda proeminente: cor de alto contraste (não `--color-bg-rail`/`--t-caption`); garantir que seja o primeiro elemento do cabeçalho
- [x] 5.2 Trocar glifo de busca de `🔎` para `🔍`; trocar botões de navegação de `◂▸` para `↑↓`; separar campo de substituição em dois (`Substituir` + `por`)
- [x] 5.3 Atualizar botão de salvar para `💾 Salvar`
- [x] 5.4 Implementar `QSyntaxHighlighter` (`OccurrenceHighlighter`) ligado ao documento do `QPlainTextEdit`: realça todas as ocorrências com `COLOR_OCCURRENCE`; realça a ocorrência atual com `COLOR_OCCURRENCE_CURRENT`; atualiza ao mudar o campo de busca; desativa quando busca está vazia; desativa acima de 5.000 linhas com aviso na toolbar
- [x] 5.5 Substituir o `QMessageBox` do modo "Um a um" por um `QWidget` de stepbar inline com botões `← Anterior`, `→ Próxima`, `Substituir` e `Encerrar`; exibir/ocultar o stepbar ao ativar/encerrar o modo

## 6. Verificação e testes

- [x] 6.1 Rodar `pytest flownc/tests/` e corrigir qualquer regressão introduzida pelas mudanças de UI
- [x] 6.2 Rodar `mypy flownc/ --ignore-missing-imports` e corrigir erros de tipo nos arquivos modificados
- [x] 6.3 Rodar `ruff check flownc/` e corrigir avisos de lint nos arquivos modificados
- [ ] 6.4 Fazer smoke manual: abrir o app, conferir compositor (dois campos, lista, ✕, CTA), header (marca, botões, cores), lista de programas (um checkbox, .file.off, + Adicionar), editor (Voltar proeminente, 🔍, ↑↓, realce, stepbar) lado a lado com `mockups/painel-final.v2.html`
