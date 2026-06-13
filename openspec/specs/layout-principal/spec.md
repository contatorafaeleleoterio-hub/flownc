# layout-principal

## Purpose

Define a estrutura raiz do app: rail + QStackedWidget de telas, com MainWindow como maestro.
## Requirements
### Requirement: Componentes isolados em flownc/ui/components/

O sistema SHALL organizar as 4 telas como classes QWidget independentes em `flownc/ui/screens/`: `LoteScreen`, `EditorScreen`, `CodigosScreen`, `HistoricoScreen`. Cada tela SHALL ser importável e instanciável sem depender das outras telas.

#### Scenario: Importação independente de cada tela

- **WHEN** qualquer uma das 4 telas é importada em isolamento
- **THEN** a importação sucede sem erro e a instanciação não levanta exceção

### Requirement: MainWindow como maestro

O sistema SHALL manter toda a lógica de estado global (preset/receita, lista de programas, edições do lote) em `MainWindow`. As telas SHALL comunicar ações via sinais Qt; `MainWindow` SHALL conectar os sinais no `__init__` e repassar dados entre telas conforme necessário. Lógica de conteúdo SHALL ficar nos widgets de tela, não no maestro.

#### Scenario: Sinal do rail troca a tela ativa

- **WHEN** o RailWidget emite `tela_mudou(2)` (Códigos)
- **THEN** MainWindow chama `stack.setCurrentIndex(2)` e o filete laranja move para "Códigos"

#### Scenario: Estado das telas preservado ao navegar

- **WHEN** o usuário carrega programas na tela Lote, navega para Histórico e volta
- **THEN** a lista de programas na tela Lote mantém o conteúdo carregado

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

### Requirement: Estrutura raiz como Rail + QStackedWidget

O sistema SHALL implementar a janela principal (`MainWindow`) como um layout horizontal de dois elementos: `RailWidget` (fixo, ~56px) à esquerda e um `QStackedWidget` (restante da largura) à direita. O `QSplitter` de 2 colunas da versão anterior SHALL ser removido. A `TopBar` SHALL ficar acima do `QStackedWidget` num layout vertical.

#### Scenario: Janela abre com rail e tela Lote ativa

- **WHEN** o app é iniciado
- **THEN** a janela exibe o rail à esquerda e a tela Lote (índice 0 do QStackedWidget) à direita

#### Scenario: MainWindow não tem mais QSplitter de 2 colunas

- **WHEN** o código de `main_window.py` é inspecionado
- **THEN** não existe instância de `QSplitter(Qt.Horizontal)` como layout raiz da janela

