## Why

O app FlowNC ainda usa o visual padrão do Qt (cinza sistema, fonte padrão, sem identidade). O mockup `mockups/painel-final.v2.html` está aprovado e define todos os tokens visuais do produto; o app precisa receber esses tokens antes de qualquer refatoração de layout (Mudanças B e C).

## What Changes

- Criar `flownc/ui/theme.py` com todos os tokens do mockup como constantes Python (cores, tipografia, espaçamentos, raios, alturas, dimensões, sombras).
- Adicionar fontes IBM Plex Sans e IBM Plex Mono em `flownc/assets/fonts/` e registrá-las no boot via `QFontDatabase`.
- Criar `flownc/ui/style.qss` cobrindo os 8 tipos de widget principais (QMainWindow, QPushButton, QComboBox, QListWidget, QLineEdit, QLabel, QCheckBox, QSplitter).
- Aplicar o QSS no boot do app (`app.setStyleSheet()`) sem alterar posição, número ou hierarquia de widgets.

## Capabilities

### New Capabilities

- `fundacao-visual`: Tokens de design (cores, fontes, espaçamentos, raios, alturas, dimensões, sombras) como constantes Python em `theme.py` + folha QSS central aplicada no boot do app.

### Modified Capabilities

<!-- Nenhuma capability existente tem seus requisitos alterados — só aparência, sem mudança de comportamento. -->

## Impact

- **Arquivos novos:** `flownc/ui/theme.py`, `flownc/ui/style.qss`, `flownc/assets/fonts/*.ttf` (IBM Plex Sans + Mono).
- **Arquivo alterado:** `flownc/ui/main_window.py` — leitura do QSS + registro de fontes no boot (sem tocar em widgets).
- **Sem impacto em `core/`** — puramente visual.
- **Sem impacto em testes existentes** — os testes de core não dependem de UI; o `test_ui_smoke.py` pode precisar de stub de QApplication se não tiver.
