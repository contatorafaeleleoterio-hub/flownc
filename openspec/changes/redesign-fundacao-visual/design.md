## Context

O app FlowNC (PySide6 / Qt Widgets) ainda exibe o tema padrão do Qt. O mockup `mockups/painel-final.v2.html` define um sistema de design completo com ~70 tokens CSS (cores, tipografia IBM Plex, espaçamentos, raios, alturas, sombras). O objetivo desta mudança é transferir esses tokens para o Python e aplicá-los via uma única folha QSS central, sem tocar na hierarquia de widgets existente.

## Goals / Non-Goals

**Goals:**
- Exportar todos os tokens do mockup como constantes Python em `flownc/ui/theme.py`.
- Embalar as fontes IBM Plex Sans e IBM Plex Mono em `flownc/assets/fonts/` e registrá-las no boot.
- Gerar `flownc/ui/style.qss` que cobre QMainWindow, QPushButton, QComboBox, QListWidget, QLineEdit, QLabel, QCheckBox e QSplitter usando os tokens.
- Aplicar o QSS uma vez no boot via `app.setStyleSheet()` em `main_window.py`.
- Todos os testes existentes continuam passando após a mudança.

**Non-Goals:**
- Alterar posição, número ou hierarquia de widgets (isso é Mudança B).
- Criar componentes novos (`header.py`, `compositor.py`, etc. — Mudança B).
- Estilizar o editor (`editor_panel.py`) — Mudança C.
- Remover contagem automática ou outros elementos de UI — Mudança C.

## Decisions

### D1 — `theme.py` como módulo de constantes, não dicionário

Os tokens serão variáveis Python (ex.: `COLOR_BG_BASE = "#F8FAFB"`) em vez de um dict global, para que o mypy e o autocomplete os vejam como strings tipadas. O QSS interpolará os valores em tempo de build (string format), não em runtime.

**Alternativa descartada:** dict `TOKENS = {...}` — perde type safety e autocomplete.

### D2 — Uma única folha QSS carregada do arquivo

`style.qss` é lido do disco e aplicado via `app.setStyleSheet()`. Isso facilita inspecionar o QSS no Qt Designer e editar sem recompilar. O arquivo é gerado com valores literais (não usa variáveis QSS — PySide6 não suporta CSS custom properties).

**Alternativa descartada:** QSS inline em strings Python — difícil de manter e inspecionar.

### D3 — Fontes via QFontDatabase.addApplicationFont()

Cada `.ttf` é registrado individualmente no boot. Fallback seguro: se `addApplicationFont` retornar -1 (arquivo não encontrado), o app usa `Segoe UI` / `Consolas` do sistema e não bloqueia o boot.

### D4 — Aplicação sem tocar em widgets

O `setStyleSheet()` é chamado no objeto `QApplication`, propagando o estilo para todos os widgets filhos. Nenhum widget é criado, removido ou movido. Isso preserva integralmente a lógica atual e os testes de UI existentes.

## Risks / Trade-offs

- **Fontes IBM Plex não embarcadas** → Fallback automático para `Segoe UI`/`Consolas`; anotar como blocker visual se os TTFs não chegarem antes do build.
- **Seletor QSS muito abrangente pode afetar widget inesperado** → Aplicar por tipo (ex.: `QPushButton { ... }`) em vez de por classe genérica (`QWidget`). Isolar por partes se o app quebrar.
- **test_ui_smoke.py requer QApplication** → Já existe; verificar que `setStyleSheet` não produz erro de inicialização nesses testes (normalmente inerte sem display).

## Migration Plan

1. Criar `theme.py` e `style.qss` (novos arquivos — sem risco de rollback).
2. Adicionar fontes em `assets/fonts/` (novos arquivos — sem risco).
3. Editar `main_window.py` para ler QSS + registrar fontes no `__init__` — mudança pontual de 5-10 linhas.
4. Rollback: remover as 3 chamadas inseridas em `main_window.py`; apagar `theme.py` e `style.qss`.

## Open Questions

- Os arquivos `.ttf` das fontes IBM Plex serão fornecidos pelo Rafael ou devem ser baixados automaticamente durante o build? (Fallback de sistema já previsto como plano B.)
