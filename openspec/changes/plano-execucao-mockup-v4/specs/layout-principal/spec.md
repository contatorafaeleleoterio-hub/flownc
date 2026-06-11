## MODIFIED Requirements

### Requirement: Estrutura raiz como Rail + QStackedWidget

O sistema SHALL implementar a janela principal (`MainWindow`) como um layout horizontal de dois elementos: `RailWidget` (fixo, ~56px) à esquerda e um `QStackedWidget` (restante da largura) à direita. O `QSplitter` de 2 colunas da versão anterior SHALL ser removido. A `TopBar` SHALL ficar acima do `QStackedWidget` num layout vertical.

#### Scenario: Janela abre com rail e tela Lote ativa

- **WHEN** o app é iniciado
- **THEN** a janela exibe o rail à esquerda e a tela Lote (índice 0 do QStackedWidget) à direita

#### Scenario: MainWindow não tem mais QSplitter de 2 colunas

- **WHEN** o código de `main_window.py` é inspecionado
- **THEN** não existe instância de `QSplitter(Qt.Horizontal)` como layout raiz da janela

### Requirement: Componentes isolados por tela em flownc/ui/screens/

O sistema SHALL organizar as 4 telas como classes QWidget independentes em `flownc/ui/screens/`: `LoteScreen`, `EditorScreen`, `CodigosScreen`, `HistoricoScreen`. Cada tela SHALL ser importável e instanciável sem depender das outras telas.

#### Scenario: Importação independente de cada tela

- **WHEN** qualquer uma das 4 telas é importada em isolamento
- **THEN** a importação sucede sem erro e a instanciação não levanta exceção

### Requirement: MainWindow como maestro de sinais

O sistema SHALL manter toda a lógica de estado global (preset/receita, lista de programas, edições do lote) em `MainWindow`. As telas SHALL comunicar ações via sinais Qt; `MainWindow` SHALL conectar os sinais no `__init__` e repassar dados entre telas conforme necessário. Lógica de conteúdo SHALL ficar nos widgets de tela, não no maestro.

#### Scenario: Sinal do rail troca a tela ativa

- **WHEN** o RailWidget emite `tela_mudou(2)` (Códigos)
- **THEN** MainWindow chama `stack.setCurrentIndex(2)` e o filete laranja move para "Códigos"

#### Scenario: Estado das telas preservado ao navegar

- **WHEN** o usuário carrega programas na tela Lote, navega para Histórico e volta
- **THEN** a lista de programas na tela Lote mantém o conteúdo carregado

## REMOVED Requirements

### Requirement: Layout de 2 colunas dinâmicas

**Reason**: O v4 substitui a estrutura de 2 colunas por rail + 4 telas no QStackedWidget. A proporção dinâmica 60/40 ↔ 40/60 era específica do layout de 2 colunas que foi removido.
**Migration**: A tela Lote implementa suas próprias proporções internas (programas esquerda + compositor+edições direita). A tela Editor usa faixa de arquivos estreita à esquerda + editor à direita, sem QSplitter dinâmico.

### Requirement: Painel direito alternável via QStackedWidget

**Reason**: Substituído pela estrutura de 4 telas no `QStackedWidget` raiz gerenciado pelo Rail. O padrão "coluna direita alterna entre Resumo e Editor" deixou de existir.
**Migration**: O editor agora é uma tela dedicada (índice 1 do QStackedWidget raiz), não um painel da coluna direita.
