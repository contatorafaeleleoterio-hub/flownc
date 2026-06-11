## MODIFIED Requirements

### Requirement: Tokens de design em theme.py

O sistema SHALL expor todos os tokens visuais do mockup `painel-final.v4.html` como constantes Python em `flownc/ui/theme.py`, cobrindo: cores (`COLOR_*`), tipografia (`T_*`), espaçamentos (`SP_*`), raios (`RADIUS_*`), alturas (`H_*`), dimensões (`DIM_*`) e sombras. A paleta SHALL seguir o tema **"Precisão Laranja"** do v4: laranja `#E85D04` como cor de ação principal (CTA), fundo cinza-azulado, topo/rail em azul-ardósia escuro. O módulo MUST ser importável sem instanciar QApplication.

#### Scenario: Importação sem QApplication

- **WHEN** o módulo `flownc.ui.theme` é importado em contexto sem display Qt
- **THEN** a importação sucede sem levantar exceção e todas as constantes estão acessíveis

#### Scenario: Token de CTA laranja presente

- **WHEN** o módulo `flownc.ui.theme` é inspecionado
- **THEN** a constante `COLOR_CTA` (ou equivalente) contém o valor `#E85D04`

#### Scenario: Tokens de rail e topo presentes

- **WHEN** o módulo `flownc.ui.theme` é inspecionado
- **THEN** existem constantes para a cor de fundo do rail (`COLOR_RAIL`) e a cor de fundo do topo (`COLOR_TOP`)

### Requirement: Folha QSS central sincronizada com v4

O sistema SHALL carregar `flownc/ui/style.qss` e aplicá-lo via `app.setStyleSheet()` durante a inicialização. O QSS MUST usar os tokens do v4 e cobrir seletores para todos os tipos de widget usados no v4: QMainWindow, QPushButton, QComboBox, QListWidget, QLineEdit, QLabel, QCheckBox, QTabWidget, QDialog e o widget de rail customizado. Cores hardcoded NOT SHALL aparecer no QSS — todos os valores SHALL vir de tokens de `theme.py`.

#### Scenario: QSS aplicado sem erro

- **WHEN** o app é inicializado
- **THEN** `app.setStyleSheet()` é chamado com o conteúdo de `style.qss` sem levantar exceção

#### Scenario: Sem cores hardcoded no QSS

- **WHEN** o arquivo `style.qss` é inspecionado
- **THEN** nenhum valor hexadecimal de cor aparece diretamente no arquivo (todos os valores de cor são variáveis Python interpoladas dos tokens)

### Requirement: Fontes IBM Plex registradas no boot

O sistema SHALL registrar as fontes IBM Plex Sans e IBM Plex Mono via `QFontDatabase.addApplicationFont()` durante a inicialização de `MainWindow`. Se os arquivos `.ttf` não forem encontrados, o boot MUST continuar sem erro, usando fontes do sistema como fallback (Segoe UI / Consolas).

#### Scenario: Fontes registradas com sucesso

- **WHEN** os arquivos `.ttf` existem em `flownc/assets/fonts/`
- **THEN** `QFontDatabase.addApplicationFont()` retorna ID ≥ 0 para cada arquivo

#### Scenario: Fallback seguro sem TTFs

- **WHEN** os arquivos `.ttf` não existem em `flownc/assets/fonts/`
- **THEN** o boot conclui sem levantar exceção e o app exibe fontes do sistema

### Requirement: Testes existentes não regridem

O sistema SHALL manter todos os testes pytest existentes passando após a atualização dos tokens e QSS. A suíte MUST rodar sem erro em ambiente headless.

#### Scenario: Suíte completa de core passa

- **WHEN** `pytest flownc/tests/` é executado após a mudança
- **THEN** todos os testes que passavam antes continuam passando (zero regressões)
