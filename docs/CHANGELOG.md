# Changelog

## 2026-06-13

- Documentação alinhada ao **mockup v4**: `PRD.md`, `DECISOES.md`, `PRODUTO.md`, `README.md` e
  este changelog atualizados (referência v2 → v4, link quebrado `CONTEXTO.md` → `CONTEXTO-IA.md`,
  estado do projeto). `CONTEXTO-IA.md` segue como fonte central.
- Change OpenSpec `plano-execucao-mockup-v4` arquivada (64/64 tarefas, Fase 2 aprovada).

## 2026-06-12

- **Fase 2 (interface v4) aprovada pelo Mestre (64/64 tarefas)**: rail + 4 telas (Lote · Editor ·
  Códigos · Histórico), topo global, compositor com abas, conferência com números reais,
  publicação com progresso, editor com contagem automática. EXE portátil gerado e repo publicado
  no GitHub.
- Docs de negócio criados: `MONETIZACAO.md` e `PAGINA-DE-VENDAS.md` (BR-first); decisões fechadas
  (comprador = gestor da oficina, pagamento via Stripe, preço-teste). Identidade visual: logo
  wordmark aprovada (azul = marca, laranja `#E85D04` = ação).

## 2026-06-11

- **Mockup `painel-final.v4.html` aprovado** como contrato visual único (rail + 4 telas).
  Supera o v2 (2 colunas dinâmicas), que passa a ser histórico em `_descarte/`.

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
