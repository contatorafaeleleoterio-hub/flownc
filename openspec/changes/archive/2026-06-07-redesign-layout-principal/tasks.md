> Layout principal: 4 componentes isolados + 2 colunas dinâmicas + MainWindow como maestro. Regra: core/ intocado; pytest verde ao final de cada grupo.

## 1. Estrutura base (`flownc/ui/components/`)

- [x] 1.1 Criar `flownc/ui/components/__init__.py` (vazio; será preenchido ao longo dos grupos).
- [x] 1.2 Confirmar que `import flownc.ui.components` funciona sem erro (importação pura, sem QApplication).

## 2. HeaderBar (`flownc/ui/components/header.py`)

- [x] 2.1 Criar `HeaderBar(QWidget)` com logo FlowNC (QLabel "⚙ FlowNC"), `QComboBox` de perfil (`cb_preset`), botões "Abrir pasta…" e "Abrir programa(s)…" e botão stub "Verificar".
- [x] 2.2 Adicionar sinais `perfil_alterado: Signal(str)`, `abrir_pasta_solicitado: Signal()`, `abrir_arquivos_solicitado: Signal()`.
- [x] 2.3 Adicionar métodos públicos `set_presets(nomes: list[str])` e `set_preset_atual(nome: str)` que atualizam o ComboBox sem disparar o sinal.
- [x] 2.4 Exportar `HeaderBar` em `components/__init__.py`.

## 3. CompositorPanel (`flownc/ui/components/compositor.py`)

- [x] 3.1 Criar `CompositorPanel(QWidget)` com dois `QComboBox` (De / Para) e um `QComboBox` de escopo (Todos / Só este programa).
- [x] 3.2 Adicionar lista de edições montadas: `QListWidget` mostrando cada regra como `"<De> → <Para> [escopo]"` + botão "➕ adicionar outra edição" que valida De/Para não-vazio e insere na lista.
- [x] 3.3 Adicionar botão "✕" por item (ou botão "Remover selecionada") que remove a regra da lista.
- [x] 3.4 Adicionar sinais `regra_adicionada: Signal(object)` (emite `Rule`) e `regra_removida: Signal(int)` (emite índice).
- [x] 3.5 Adicionar método `set_library(entries: list[CodeEntry])` que popula os ComboBoxes De/Para com os códigos da biblioteca.
- [x] 3.6 Adicionar método `get_regras() -> list[Rule]` que retorna as regras montadas em ordem.
- [x] 3.7 Exportar `CompositorPanel` em `components/__init__.py`.

## 4. ProgramListPanel (`flownc/ui/components/program_list.py`)

- [x] 4.1 Criar `ProgramListPanel(QWidget)` com `QListWidget` onde cada item exibe `path.name` e tem `Qt.ItemFlag.ItemIsUserCheckable` (checkbox marcado por padrão).
- [x] 4.2 Adicionar botão "✎ Editar programa selecionado" que emite `editar_arquivo: Signal(str)` com o path completo do item selecionado.
- [x] 4.3 Adicionar método `set_programs(paths: list[Path])` que limpa e repopula o QListWidget.
- [x] 4.4 Adicionar método `get_selecionados() -> list[Path]` que retorna apenas os paths marcados (checked).
- [x] 4.5 Exportar `ProgramListPanel` em `components/__init__.py`.

## 5. SummaryPanel (`flownc/ui/components/summary.py`)

- [x] 5.1 Criar `SummaryPanel(QWidget)` com área scrollável (`QScrollArea`) que exibe cards de regras (um `QFrame` por regra, com `De → Para [escopo]` em mono).
- [x] 5.2 Adicionar método `set_rules(rules: list[Rule])` que re-renderiza os cards (limpa e reconstrói).
- [x] 5.3 Adicionar botão CTA "APLICAR SUBSTITUIÇÕES" (altura 56 px via token `H_CTA`).
- [x] 5.4 Adicionar sinal `publicar_solicitado: Signal()` conectado ao CTA.
- [x] 5.5 Exportar `SummaryPanel` em `components/__init__.py`.

## 6. Refatoração do MainWindow (maestro)

- [x] 6.1 Em `_build_ui()`, substituir o layout antigo (top QHBoxLayout com preset/botões + dest + QTabWidget) pelo novo esqueleto: `HeaderBar` no topo + `QSplitter(Qt.Horizontal)` ocupando o restante da janela.
- [x] 6.2 Coluna esquerda do splitter: `QWidget` com `QVBoxLayout` contendo `CompositorPanel` (stretch=0) + `ProgramListPanel` (stretch=1).
- [x] 6.3 Coluna direita do splitter: `QStackedWidget` com `SummaryPanel` no índice 0 e `EditorPanel` no índice 1.
- [x] 6.4 Chamar `self._splitter.setSizes([600, 400])` após adicionar os widgets.
- [x] 6.5 Implementar `_abrir_editor(path: str)`: `self._stack.setCurrentIndex(1)` + `self._splitter.setSizes([400, 600])` + `self._editor_panel.abrir_arquivo(Path(path))`.
- [x] 6.6 Implementar `_fechar_editor()`: `self._stack.setCurrentIndex(0)` + `self._splitter.setSizes([600, 400])`.
- [x] 6.7 Conectar sinais no `__init__` (após `_build_ui()`): `header.perfil_alterado → _on_preset_changed_by_name`, `header.abrir_pasta_solicitado → _open_folder`, `header.abrir_arquivos_solicitado → _open_files`, `compositor.regra_adicionada → _on_regra_adicionada`, `compositor.regra_removida → _on_regra_removida`, `program_list.editar_arquivo → _abrir_editor`, `summary.publicar_solicitado → _on_aplicar`, `editor_panel.fechar_solicitado → _fechar_editor`.
- [x] 6.8 Adaptar `_load_presets()`, `_load_library()` e `_load_settings()` para chamar os métodos públicos dos novos componentes em vez de manipular widgets diretamente.
- [x] 6.9 Adaptar `_on_preset_changed_by_name(nome)` para chamar `self._header.set_preset_atual(nome)` e repassar estado ao compositor e summary.

## 7. QSS — seletores dos novos componentes

- [x] 7.1 Adicionar seletor `HeaderBar` em `style.qss`: altura mínima 70 px, gradiente `qlineargradient` usando tokens `COLOR_HEAD_TOP` / `COLOR_HEAD_MID` / `COLOR_HEAD_BOT`, borda inferior `COLOR_HEAD_BORDER`.
- [x] 7.2 Adicionar seletores para `CompositorPanel`, `ProgramListPanel` e `SummaryPanel`: fundo `COLOR_BG_BASE`, borda-radius `RADIUS_MD`, padding `SP_16`.

## 8. Verificação e QA

- [x] 8.1 Rodar `pytest flownc/tests/` — zero regressões (todos os testes que passavam antes continuam passando).
- [x] 8.2 Rodar `mypy flownc/ui/components/ --ignore-missing-imports` — sem erros de tipo nos componentes novos.
- [x] 8.3 Rodar `ruff check flownc/ui/components/ flownc/ui/main_window.py` — limpo.
- [ ] 8.4 Smoke manual: abrir app → confirmar layout 2 colunas → montar uma edição no compositor → verificar card no summary → clicar "Editar" em um programa → confirmar colunas invertem (editor visível) → fechar editor → confirmar colunas voltam ao normal.
