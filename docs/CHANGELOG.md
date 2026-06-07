# Changelog

## 2026-06-07

- Documentação (`docs/`) atualizada para refletir o mockup v2 aprovado (`mockups/painel-final.v2.html`); design antigo (3 colunas / `painel-final.html`) marcado como descartado.
- Baseline de testes em `146 passed` (venv `flownc/.venv`, PySide6 6.11.1).

## 2026-06-06

- Mudança `motor-contagem-e-publicacao` implementada e arquivada: `core/scan.py` (varredura/contagem), `core/batch.py` (validação de lote/conflitos), `core/publisher.py` (publicação com backup versionado + troca atômica + dupla conferência SHA-256), `settings_store` v1→v2.
- Ação separada `Retirar` descartada do plano (remoção via substituição-por-vazio).
- Mudança `redesign-fundacao-visual` (Mudança A) implementada e arquivada: tokens + tema/QSS.
- Mudança `redesign-layout-principal` (Mudança B) proposta e em implementação (2 colunas dinâmicas + componentes).

## 2026-06-05

- Mudança `editor-integrado-por-arquivo` implementada: `core/inplace_save.py` (gravação in-place atômica + SHA-256) e `ui/editor_panel.py` (editor mono com localizador), integrados via `QStackedWidget` em `main_window.py`.
- Baseline de testes subiu para `121 passed`.

## 2026-06-04

- Início controlado do rebrand para `FlowNC`.
- Repositório Git inicializado com baseline anterior ao rename.
- `requirements.lock` criado a partir do venv atual.
- Documentação consolidada em `docs/`.
- Material obsoleto movido para `_descarte/` em vez de apagado.
- Rename textual aplicado em código, build, guias, mockup, OpenSpec e memória.
- Pasta de código renomeada para `flownc/`; venv recriado a partir de `requirements.lock`.
- `dist/FlowNC/FlowNC.exe` gerado e validado em smoke test; `dist` antigo removido após o smoke.
