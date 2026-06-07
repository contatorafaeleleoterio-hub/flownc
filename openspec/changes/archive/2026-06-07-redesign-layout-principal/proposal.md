## Why

O app ainda usa o layout monolítico antigo (QTabWidget em `main_window.py`). A Mudança A instalou o design system (tokens + QSS), mas o layout visual do mockup aprovado (`painel-final.v2.html`) ainda não existe no app. Esta mudança implementa a estrutura real: header, 2 colunas dinâmicas e componentes isolados.

## What Changes

- **Novo** `flownc/ui/components/` com 4 componentes extraídos de `main_window.py`:
  - `header.py` — barra superior (logo FlowNC, seletor de perfil/máquina, botões de ação)
  - `compositor.py` — painel esquerdo superior (dropdowns de/para/escopo + lista de edições montadas)
  - `program_list.py` — painel esquerdo inferior (lista de arquivos com checkbox + botão Editar)
  - `summary.py` — painel direito em modo normal (contadores, cards de regras, CTA de publicação)
- **Refatoração** de `main_window.py`: deixa de ser monolítico e passa a ser maestro que instancia e conecta os componentes
- **Layout 2 colunas** via `QSplitter` horizontal: coluna esquerda (~60%) e coluna direita (~40%), com inversão dinâmica ao abrir o editor (esquerda encolhe para ~40%, direita expande para ~60%)
- **Troca direita**: coluna direita alterna entre `summary.py` e o `editor_panel.py` existente via `QStackedWidget`
- `QTabWidget` de SUBSTITUIÇÕES/VERIFICAÇÕES é **removido**; a aba de verificações passa a ser acessível via botão no header

## Capabilities

### New Capabilities

- `layout-principal`: Estrutura de 2 colunas dinâmicas com header, compositor, lista de programas e painel direito alternável (resumo ↔ editor)

### Modified Capabilities

- `fundacao-visual`: Nenhum requisito de spec muda; os novos componentes apenas consomem os tokens já definidos

## Impact

- `flownc/ui/main_window.py` — refatorado (estrutura, não lógica de negócio)
- `flownc/ui/components/` — diretório novo com 4 arquivos
- `flownc/ui/editor_panel.py` — sem alteração (já implementado); apenas integrado no `QStackedWidget`
- `flownc/ui/style.qss` — pode receber seletores adicionais para os novos componentes
- `flownc/tests/` — smoke tests existentes devem continuar passando; novos testes de integração para os sinais entre componentes
