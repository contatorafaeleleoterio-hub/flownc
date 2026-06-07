### Requirement: Layout de 2 colunas dinâmicas

O sistema SHALL exibir a interface em 2 colunas horizontais separadas por `QSplitter`. A coluna esquerda SHALL ter proporção inicial de ~60% e a coluna direita de ~40% da largura total. Ao abrir o editor de arquivo, a proporção SHALL inverter para ~40/60 (esquerda/direita). Ao fechar o editor, SHALL retornar para ~60/40.

#### Scenario: Proporção inicial

- **WHEN** o app é iniciado
- **THEN** o splitter está posicionado com a coluna esquerda ocupando aproximadamente 60% da largura e a direita 40%

#### Scenario: Expansão ao abrir editor

- **WHEN** o usuário clica em "Editar" em um arquivo da lista
- **THEN** o splitter ajusta para ~40% esquerda / ~60% direita e o painel direito exibe o EditorPanel

#### Scenario: Retorno ao fechar editor

- **WHEN** o usuário fecha o EditorPanel (botão voltar ou equivalente)
- **THEN** o splitter retorna para ~60% esquerda / ~40% direita e o painel direito exibe o SummaryPanel

### Requirement: Componentes isolados em flownc/ui/components/

O sistema SHALL organizar os 4 painéis da interface como classes QWidget independentes em `flownc/ui/components/`: `HeaderBar`, `CompositorPanel`, `ProgramListPanel`, `SummaryPanel`. Cada componente SHALL ser importável e instanciável sem depender de outros componentes.

#### Scenario: Importação independente de cada componente

- **WHEN** qualquer um dos 4 componentes é importado em isolamento
- **THEN** a importação sucede sem erro e a instanciação com `QApplication` ativa não levanta exceção

#### Scenario: Exportação via __init__.py

- **WHEN** `from ui.components import HeaderBar, CompositorPanel, ProgramListPanel, SummaryPanel` é executado
- **THEN** todos os 4 nomes estão disponíveis sem erro de importação

### Requirement: MainWindow como maestro

O sistema SHALL manter toda a lógica de estado (preset, programas, regras, `_file_subs`) em `MainWindow`. Os componentes SHALL comunicar ações do usuário via sinais Qt e receber dados via métodos públicos (`set_programs`, `set_rules`, `set_summary`). `MainWindow` SHALL conectar todos os sinais no seu `__init__`.

#### Scenario: Sinal de edição montada

- **WHEN** o usuário monta uma edição no CompositorPanel
- **THEN** o sinal correspondente do CompositorPanel é emitido e MainWindow atualiza o estado interno e repassa os dados ao SummaryPanel

#### Scenario: Sinal de abertura do editor

- **WHEN** o usuário clica em "Editar" em um arquivo do ProgramListPanel
- **THEN** ProgramListPanel emite o sinal `editar_arquivo(path: str)` e MainWindow ativa o EditorPanel com o arquivo correspondente

### Requirement: Painel direito alternável via QStackedWidget

O sistema SHALL implementar a coluna direita como `QStackedWidget` com dois widgets: índice 0 = `SummaryPanel`, índice 1 = `EditorPanel`. A troca SHALL ocorrer atomicamente junto com o ajuste do splitter.

#### Scenario: Exibição do SummaryPanel por padrão

- **WHEN** o app é iniciado e nenhum editor está ativo
- **THEN** o QStackedWidget exibe o SummaryPanel (índice 0)

#### Scenario: Troca para EditorPanel

- **WHEN** MainWindow recebe o sinal `editar_arquivo`
- **THEN** o QStackedWidget passa para o índice 1 (EditorPanel) e o splitter ajusta as proporções

### Requirement: HeaderBar com logo, perfil e ações

O sistema SHALL exibir uma barra de cabeçalho fixo (`HeaderBar`) com: logo FlowNC, seletor de perfil/máquina (QComboBox), botão "Verificar" (stub) e botão "Preferências" (stub). A altura SHALL ser de 70 px conforme o token `DIM_HEADER`.

#### Scenario: Presença dos elementos obrigatórios

- **WHEN** o app é iniciado
- **THEN** a HeaderBar exibe logo, ComboBox de perfil, botão "Verificar" e botão "Preferências" visíveis

#### Scenario: Seleção de perfil

- **WHEN** o usuário seleciona um item diferente no ComboBox de perfil do HeaderBar
- **THEN** HeaderBar emite o sinal `perfil_alterado(nome: str)` e MainWindow carrega o preset correspondente

### Requirement: Testes existentes não regridem

O sistema SHALL manter todos os testes pytest existentes passando após a refatoração do layout. Nenhum módulo de `core/` é alterado.

#### Scenario: Suíte completa passa após refatoração

- **WHEN** `pytest flownc/tests/` é executado após a mudança
- **THEN** todos os testes que passavam antes continuam passando (zero regressões)
