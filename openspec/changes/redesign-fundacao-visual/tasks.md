> Fundação visual: tokens → QSS → fontes → boot. Regra: nenhum widget criado/movido/removido; suíte pytest verde ao final.

## 1. Tokens de design (`flownc/ui/theme.py`)

- [x] 1.1 Criar `flownc/ui/theme.py` com todas as constantes de cor (`COLOR_*`) extraídas do mockup `painel-final.v2.html`.
- [x] 1.2 Adicionar constantes de tipografia (`T_*`: font-family, size, weight — para uso como valores QSS).
- [x] 1.3 Adicionar constantes de espaçamento (`SP_*`), raios (`RADIUS_*`), alturas (`H_*`) e dimensões (`DIM_*`).
- [x] 1.4 Adicionar constantes de sombra (`SHADOW_SCREEN`, `SHADOW_MODAL`, `METAL`, `FOCUS_RING`, `CONFLICT_BAR`).
- [x] 1.5 Verificar que `import flownc.ui.theme` funciona sem QApplication (importação pura).

## 2. Fontes IBM Plex (`flownc/assets/fonts/`)

- [x] 2.1 Criar pasta `flownc/assets/fonts/` (se não existir).
- [ ] 2.2 Adicionar arquivos `.ttf` de IBM Plex Sans (Regular, SemiBold, Bold) em `flownc/assets/fonts/`. ⚠ BLOCKER: fontes não encontradas no sistema — aguardando TTFs.
- [ ] 2.3 Adicionar arquivos `.ttf` de IBM Plex Mono (SemiBold) em `flownc/assets/fonts/`. ⚠ BLOCKER: idem.
- [x] 2.4 Se fontes não disponíveis: registrar como blocker e documentar o fallback (`Segoe UI` / `Consolas`) em `theme.py`.

## 3. Folha QSS (`flownc/ui/style.qss`)

- [x] 3.1 Criar `flownc/ui/style.qss` com seletor e regras para `QMainWindow` (cor de fundo, fonte base).
- [x] 3.2 Adicionar seletor para `QPushButton` (normal, hover, pressed, disabled) usando tokens de cor/altura.
- [x] 3.3 Adicionar seletor para `QComboBox` (fundo, borda, dropdown arrow) usando tokens.
- [x] 3.4 Adicionar seletor para `QListWidget` (fundo, item selecionado, hover) usando tokens.
- [x] 3.5 Adicionar seletor para `QLineEdit` (fundo, borda, foco com focus-ring) usando tokens.
- [x] 3.6 Adicionar seletor para `QLabel` (cor de texto primário e secundário via `QLabel[secondary="true"]`).
- [x] 3.7 Adicionar seletor para `QCheckBox` (indicator checked/unchecked) usando tokens.
- [x] 3.8 Adicionar seletor para `QSplitter::handle` (largura, cor de fundo) usando tokens.

## 4. Aplicação no boot (`flownc/ui/main_window.py`)

- [x] 4.1 No `__init__` de `MainWindow`, registrar cada `.ttf` via `QFontDatabase.addApplicationFont()`; logar caminho se retornar -1 (não bloquear boot).
- [x] 4.2 No `__init__` de `MainWindow`, ler `style.qss` (path relativo ao arquivo) e chamar `app.setStyleSheet(qss)`.
- [x] 4.3 Verificar que nenhum widget foi criado, removido ou movido (diff de `main_window.py` deve mostrar apenas as novas linhas de fonts + QSS).

## 5. Verificação e QA

- [x] 5.1 Rodar `pytest flownc/tests/` — zero regressões (todos os testes que passavam antes continuam passando).
- [x] 5.2 Rodar `mypy flownc/ui/theme.py --ignore-missing-imports` — limpo.
- [x] 5.3 Rodar `ruff check flownc/ui/theme.py flownc/ui/style.qss` (só `.py`) — limpo nos arquivos novos/alterados.
- [x] 5.4 Smoke manual: abrir o app e confirmar que cores/fontes do mockup aparecem e nenhum widget sumiu ou quebrou.
