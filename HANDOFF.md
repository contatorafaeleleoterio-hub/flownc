# Handoff — FlowNC — 2026-06-12
Status: Fase 2 em execução — Blocos 1, 2 e 3 concluídos e verdes (16/64 tarefas da change v4).

Feito nesta sessão:
- **Bloco 1 (fundação visual v4):** `theme.py` paleta "Precisão Laranja" (CTA `#E85D04`, rail/topo
  `#2B3A4A`) + `render_qss()`; `style.qss` virou template 100% tokenizado (sem hex literal) com
  `QTabWidget`/`QDialog`.
- **Bloco 2 (estrutura raiz):** `rail.py` + `top_bar.py` + `screens/` (4 telas); `main_window`
  reescrito como maestro (topo + rail + `QStackedWidget`) com navegação.
- **Bloco 3 (painel Programas):** `program_list_v4.py` (lista marcável, chip "N de M", marcar
  todos, arrastar-e-soltar, estado vazio) integrado na `LoteScreen`.
- **Limpeza v4 (ordem do Mestre):** v4 é a única versão; componentes/mockups/docs de versões
  antigas → `_descarte/`; PLAN/HANDOFF/CLAUDE/spec/testes sem rastros. Memória reforçada (não perguntar).

Onde parou: Bloco 3 concluído e verde; tela Lote com Programas à esquerda, navegável.
Próximo passo: **Bloco 4 — Compositor com abas + Lote de edições + CTA "Conferir lote →"** via
  `/opsx:apply plano-execucao-mockup-v4`.
Blockers: nenhum.
Arquivos tocados: `flownc/ui/{theme.py,style.qss,main_window.py,editor_panel.py}`,
  `components/{rail,top_bar,program_list_v4}.py`, `screens/*`, `tests/test_ui_smoke.py`;
  `PLAN.md`, `CLAUDE.md`, `openspec/specs/fundacao-visual/spec.md`, `tasks.md`; moves p/ `_descarte/`.
Verificação: pytest **142 verde**; mypy 2 (pré-existentes); ruff 7 (pré-existentes).
Retomar com: "continuar"
