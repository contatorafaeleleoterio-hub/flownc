### Requirement: Tokens de design em theme.py

O sistema SHALL expor todos os tokens visuais do mockup `painel-final.v4.html` (paleta "Precisão Laranja", CTA `#E85D04`) como constantes Python em `flownc/ui/theme.py`, cobrindo: cores (`COLOR_*`), tipografia (`T_*`), espaçamentos (`SP_*`), raios (`RADIUS_*`), alturas (`H_*`), dimensões (`DIM_*`) e sombras (`SHADOW_*`/`METAL`). O módulo MUST ser importável sem instanciar QApplication.

#### Scenario: Importação sem QApplication

- **WHEN** o módulo `flownc.ui.theme` é importado em contexto sem display Qt
- **THEN** a importação sucede sem levantar exceção e todas as constantes estão acessíveis

#### Scenario: Tokens de cor presentes

- **WHEN** o módulo `flownc.ui.theme` é inspecionado
- **THEN** as constantes `COLOR_BG_BASE`, `COLOR_TEXT_PRIMARY`, `COLOR_INTERACTIVE`, `COLOR_SUCCESS`, `COLOR_WARNING`, `COLOR_DANGER` e `COLOR_CTA_START` existem com valores hexadecimais válidos

### Requirement: Fontes IBM Plex registradas no boot

O sistema SHALL registrar as fontes IBM Plex Sans e IBM Plex Mono via `QFontDatabase.addApplicationFont()` durante a inicialização de `MainWindow`. Se os arquivos `.ttf` não forem encontrados, o boot MUST continuar sem erro, usando fontes do sistema como fallback.

#### Scenario: Fontes registradas com sucesso

- **WHEN** os arquivos `.ttf` existem em `flownc/assets/fonts/`
- **THEN** `QFontDatabase.addApplicationFont()` retorna um ID ≥ 0 para cada arquivo e as famílias aparecem em `QFontDatabase.families()`

#### Scenario: Fallback seguro sem TTFs

- **WHEN** os arquivos `.ttf` não existem em `flownc/assets/fonts/`
- **THEN** o boot do app conclui sem levantar exceção e o app exibe fontes do sistema

### Requirement: Folha QSS central aplicada no boot

O sistema SHALL carregar `flownc/ui/style.qss` (template interpolado pelos tokens de `theme.py` via `render_qss`) e aplicá-lo via `setStyleSheet()` durante a inicialização. O QSS MUST cobrir seletores para QMainWindow, QPushButton, QComboBox, QListWidget, QLineEdit, QLabel, QCheckBox, QTabWidget e QDialog, além do rail customizado. A aplicação do QSS MUST NOT criar, remover ou mover nenhum widget.

#### Scenario: QSS aplicado sem erro

- **WHEN** o app é inicializado
- **THEN** `app.setStyleSheet()` é chamado com o conteúdo de `style.qss` sem levantar exceção

#### Scenario: Seletor para cada tipo de widget obrigatório

- **WHEN** o conteúdo de `style.qss` é inspecionado
- **THEN** o arquivo contém ao menos um bloco de regra para cada um dos tipos: QMainWindow, QPushButton, QComboBox, QListWidget, QLineEdit, QLabel, QCheckBox, QTabWidget, QDialog

#### Scenario: Hierarquia de widgets preservada

- **WHEN** o app é aberto com o QSS aplicado
- **THEN** o número de widgets visíveis e a hierarquia pai/filho são idênticos ao estado anterior à mudança

### Requirement: Testes existentes não regridem

O sistema SHALL manter todos os testes pytest existentes passando após a aplicação do QSS e registro de fontes. A suíte MUST rodar sem erro em ambiente sem display Qt (CI headless).

#### Scenario: Suíte completa de core passa

- **WHEN** `pytest flownc/tests/` é executado após a mudança
- **THEN** todos os testes que passavam antes continuam passando (zero regressões)
