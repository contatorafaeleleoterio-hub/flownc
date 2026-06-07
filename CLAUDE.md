# CLAUDE.md — FlowNC

## Stack
- App desktop Windows. Python 3.11+, PySide6 (GUI) + CLI. Código em `flownc/`.
- Build: PyInstaller (`flownc/FlowNC.spec`) → `flownc/dist/FlowNC/FlowNC.exe`.
- Verificação: pytest (146 testes verdes; usar o venv `flownc/.venv` com PySide6 6.11.1), mypy, ruff.

## Objetivo atual
Implementar o **novo design aprovado** (mockup `mockups/painel-final.v2.html`) no app. Design antigo **descartado**. Plano de execução: `PLAN.md` (raiz). Estado entre sessões: `HANDOFF.md` (raiz).

## Estrutura
- `flownc/ui/` — interface: `main_window.py` (monolítico), `editor_panel.py`. O redesenho criará `flownc/ui/components/`.
- `flownc/core/` — lógica estável (`inplace_save.py`, matcher, etc.).
- `docs/` — contexto (`CONTEXTO.md`, `PRD.md`, `DECISOES.md`). **Plano único e vivo: `PLAN.md` (raiz)** — os planos antigos foram arquivados em `_descarte/`.
- `openspec/` — fluxo OpenSpec (propose → apply → archive).

## Continuidade
Fluxo guiado por `HANDOFF.md`. Pipeline de refino do `PLAN.md`:
`/plan-disambiguate` → `/plan-atomize` → `/plan-resilience` → `/plan-validate`.
