# CLAUDE.md — FlowNC

## Stack
- App desktop Windows. Python 3.11+, PySide6 (GUI) + CLI. Código em `flownc/`.
- Build: PyInstaller (`flownc/FlowNC.spec`) → `flownc/dist/FlowNC/FlowNC.exe`.
- Verificação: pytest (verde, zero regressões — usar o venv `flownc/.venv` com PySide6 6.11.1), mypy, ruff.

## Objetivo atual
Implementar o **design aprovado** no app: mockup **`mockups/painel-final.v4.html`** (aprovado 2026-06-11 = contrato visual e **única versão considerada**). Plano de execução: `PLAN.md` (raiz). Estado entre sessões: `HANDOFF.md` (raiz). **Contexto central do produto (para qualquer agente/IA): `docs/CONTEXTO-IA.md`** — descreve as 4 telas, fluxos, interatividade e regras de negócio do v4.

> **Regra de versão:** o v4 é o único alvo. Nada de design anterior entra no fluxo; o que for de versão antiga já está arquivado em `_descarte/` e não se menciona mais. Não perguntar sobre versões anteriores — arquivar ou refatorar para o v4 (ver memória `arquivar-obsoleto-versao-antiga`).

## Estrutura
- `flownc/ui/` — interface v4: `main_window.py` (maestro: topo + rail + `QStackedWidget`), `components/` (`rail.py`, `top_bar.py`, `code_combo.py`), `screens/` (Lote/Editor/Códigos/Histórico), `editor_panel.py` (motor de edição, adaptado no Bloco 7).
- `flownc/core/` — lógica estável (`inplace_save.py`, matcher, etc.).
- `docs/` — contexto (`CONTEXTO-IA.md` ★central, `PRD.md`, `DECISOES.md`). **Plano único e vivo: `PLAN.md` (raiz)**. Material de versões antigas em `_descarte/`.
- `openspec/` — fluxo OpenSpec (propose → apply → archive).

## Continuidade
Fluxo guiado por `HANDOFF.md`. Pipeline de refino do `PLAN.md`:
`/plan-disambiguate` → `/plan-atomize` → `/plan-resilience` → `/plan-validate`.
