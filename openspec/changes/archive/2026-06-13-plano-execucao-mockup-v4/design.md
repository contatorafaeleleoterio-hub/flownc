## Context

O app atual (`main_window.py`) usa um `QSplitter(Qt.Horizontal)` com dois painéis (programas à esquerda, compositor + resumo à direita). As Mudanças A e B entregaram a fundação visual e os 4 componentes (`header.py`, `compositor.py`, `program_list.py`, `summary.py`). A change `redesign-fase2-fidelidade-visual` propôs fidelidade ao v2 — com o v4 aprovado, esta change a substitui como o plano oficial da FASE 2.

O v4 rompe com a estrutura de 2 colunas: introduz um **rail lateral escuro** com 4 botões-lugar e um `QStackedWidget` que troca a tela ativa. As telas Lote, Editor, Códigos e Histórico são widgets independentes. O núcleo (`core/`) está estável e não muda na FASE 2.

## Goals / Non-Goals

**Goals:**
- Reproduzir fielmente o v4 em PySide6, tela por tela, conferindo lado a lado com `mockups/painel-final.v4.html`.
- Entregar botões e navegação visualmente corretos; dados de exemplo podem ser fixos (FASE 2 = apenas layout/estilo).
- Preservar a lógica atual: 146 testes devem continuar verdes após cada mudança.

**Non-Goals:**
- Lógica de negócio nova (backend) — pertence à FASE 3.
- Alterações em `flownc/core/` — intocado na FASE 2.
- Implementar persistência de receitas, publicação real via `publish_batch`, `ensure_seed` ou empacotamento do EXE — FASE 3.

## Decisions

### 1. Rail + QStackedWidget como estrutura raiz
A janela principal troca o `QSplitter` por um layout horizontal: `RailWidget` (fixo, ~56px) + `QStackedWidget` (restante). O `RailWidget` emite `tela_mudou(id)` ao clicar; o maestro chama `stack.setCurrentIndex(id)`.

**Por que não QTabWidget?** Tabs ficam no topo por padrão e teriam estilo difícil de customizar para o visual de rail lateral escuro com filete laranja.

### 2. Uma classe por tela em `flownc/ui/screens/`
Cada tela é um `QWidget` independente: `LoteScreen`, `EditorScreen`, `CodigosScreen`, `HistoricoScreen`. O maestro (`main_window.py`) apenas instancia e empilha — sem lógica de conteúdo de tela.

**Por que não manter tudo em `main_window.py`?** O arquivo já é monolítico. Separar por tela limita o escopo de cada mudança e facilita testar cada tela em isolamento.

### 3. Topo global como widget separado (`TopBar`)
`TopBar` fica acima do `QStackedWidget` (fora do rail). Gerencia o seletor de receita/configuração (`QComboBox`) e o chip de backup (`QPushButton` com texto). O `main_window` conecta os sinais do `TopBar` às telas que precisam (ex.: `LoteScreen.on_receita_carregada`).

### 4. Compositor com abas usando QTabWidget interno
A `LoteScreen` tem internamente dois painéis: programas (esquerda) e um painel direito com `QTabWidget` (abas "Trocar código" / "➕ Inserir bloco") + lista de edições + CTA "Conferir lote →". O tab widget fica encapsulado no `CompositorV4Widget`.

### 5. Modal de Conferência como QDialog
`ConferenciaModal(QDialog)` — modal bloqueante, não fecha durante a varredura. Recebe a lista de edições e programas marcados, roda `build_plan` + `count_occurrences` do `core/` para popular os dados, e expõe sinal `publicar_confirmado()`. Na FASE 2 os dados podem ser simulados; na FASE 3 ligam ao `core/`.

### 6. Estratégia de migração por tela
Ordem de implementação:
1. **Rail + TopBar + esqueleto do QStackedWidget** (estrutura raiz) — base que tudo mais precisa.
2. **Tela Lote** — a mais complexa; compositor com abas + lista de edições + programas.
3. **Tela Editor** — reusa `editor_panel.py` existente, adaptado para tela cheia com faixa de arquivos.
4. **Tela Códigos** — nova tela simples de lista.
5. **Tela Histórico** — nova tela simples de lista.
6. **Modal Conferência** — modal que depende da Tela Lote estar pronta.
7. **Modal Publicação** — modal que depende da Conferência.

A cada tela: smoke test manual lado a lado com o mockup v4 antes de avançar.

### 7. Componentes reutilizáveis do v2 que continuam úteis
- `editor_panel.py` — reaproveitado (adaptado), não reescrito.
- `flownc/ui/theme.py` + `style.qss` — atualizados com tokens v4 (laranja #E85D04, nova paleta).
- `flownc/core/` — sem toque.

### 8. O que fazer com `redesign-fase2-fidelidade-visual` ✅ RESOLVIDO (2026-06-11)
Esta change SUBSTITUI `redesign-fase2-fidelidade-visual` como plano oficial. **Decisão executada:** arquivada com `openspec archive redesign-fase2-fidelidade-visual --skip-specs -y` — histórico preservado em `archive/2026-06-11-redesign-fase2-fidelidade-visual` **sem** consolidar os deltas do v2 nos specs base, evitando poluir a documentação e o conflito de escopo.

## Risks / Trade-offs

- **[Risco] Testes de UI smoke quebram ao remover QSplitter** → `test_ui_smoke.py` instancia `MainWindow` — se a estrutura mudar, os testes podem falhar. Mitigação: atualizar os smoke tests na mesma etapa em que o layout muda; manter os sinais/slots existentes com a mesma assinatura.
- **[Risco] `compositor.py` atual tem sinais conectados ao core** → Reescrever o compositor pode quebrar a lógica de montar edições. Mitigação: mapear todos os `connect()` em `main_window.py` antes de tocar no componente; preservar a assinatura dos sinais.
- **[Risco] Editor adaptado para tela cheia perde a alternância QSplitter** → O editor hoje abre no painel direito do QSplitter. No v4 ele é uma tela separada no rail. Mitigação: desacoplar o `EditorPanel` do QSplitter durante a etapa do esqueleto; garantir que ele ainda receba o arquivo correto via sinal.
- **[Trade-off] Dados simulados na FASE 2** → A Tela Lote mostrará edições e programas hardcoded — o smoke real só valida visual. Aceitável: a FASE 3 liga o backend sem alterar layout.

## Open Questions

- ✅ **Resolvido:** a change `redesign-fase2-fidelidade-visual` foi arquivada com `--skip-specs` antes de iniciar (ver Decisão 8).
- ✅ **Resolvido:** o `PLAN.md` foi reescrito do zero para o v4; é a fonte de verdade e este `tasks.md`/`design.md` são espelhos dele.
