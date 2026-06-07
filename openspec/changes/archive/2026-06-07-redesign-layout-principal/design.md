## Context

`main_window.py` tem ~1 200 linhas e carrega tudo em `_build_ui()`: layout, lógica de estado, sinais e renderização. O resultado é difícil de testar e impossível de ler em paralelo com o mockup. A Mudança A instalou tokens e QSS; agora o layout precisa refletir o mockup `painel-final.v2.html`: header fixo, 2 colunas dinâmicas, painel direito alternável (resumo ↔ editor).

## Goals / Non-Goals

**Goals:**
- Criar `flownc/ui/components/` com 4 QWidget isolados: `HeaderBar`, `CompositorPanel`, `ProgramListPanel`, `SummaryPanel`
- Refatorar `main_window.py` para maestro: instanciar componentes, conectar sinais, manter estado
- Layout 2 colunas via `QSplitter` com proporção ~60/40 → ~40/60 ao abrir editor
- Coluna direita com `QStackedWidget` alternando entre `SummaryPanel` e `EditorPanel` existente
- Zero regressão nos 121+ testes existentes

**Non-Goals:**
- Reimplementar lógica de negócio (matcher, replacer, verifier) — core/ não muda
- Reescrever `EditorPanel` — já implementado e testado
- Implementar a aba de Verificações no novo layout (fica como acesso via botão no header, stub)
- Animação CSS de transição das colunas (Qt não suporta; troca direta via `setSizes()`)

## Decisions

### 1. QSplitter para as 2 colunas (não QHBoxLayout fixo)

**Escolhido:** `QSplitter(Qt.Horizontal)` com `setSizes([600, 400])` no estado normal e `setSizes([400, 600])` ao abrir o editor.

**Alternativa descartada:** `QHBoxLayout` com `setStretch()`. Não permite redimensionamento pelo usuário.

**Rationale:** QSplitter preserva a proporção do mockup e deixa o usuário ajustar livremente. A troca programática de `setSizes()` emula o comportamento dinâmico do mockup sem animação.

### 2. Maestro em main_window.py (não bus de eventos global)

**Escolhido:** `MainWindow` instancia todos os componentes e conecta os sinais diretamente: `compositor.edicao_montada.connect(main.on_edicao_montada)`, etc.

**Alternativa descartada:** Event bus / QObject global de sinais. Adiciona indireção desnecessária para 4 componentes.

**Rationale:** 4 componentes com dependências simples e lineares. Maestro direto é legível e testável sem mock do bus.

### 3. Estado de aplicação permanece em MainWindow

Preset, lista de programas, regras montadas, `_file_subs` — tudo fica em `MainWindow`. Os componentes recebem dados via métodos públicos (`set_programs(...)`, `set_rules(...)`) e emitem sinais quando o usuário age.

**Rationale:** Evita estado distribuído. Os componentes são "buracos de display + input", não donos de dados.

### 4. Coluna direita via QStackedWidget

`QStackedWidget` com índice 0 = `SummaryPanel`, índice 1 = `EditorPanel`. Trocar: `stack.setCurrentIndex(1)` + `splitter.setSizes([400, 600])`. Voltar: índice 0 + `setSizes([600, 400])`.

### 5. Componentes extraídos (não reescritos)

A lógica de cada painel é movida de `_build_ui()` para o `__init__` do componente correspondente. Os métodos de atualização de UI que hoje estão em `MainWindow` viram métodos públicos dos componentes. A lógica de negócio (cálculos, chamadas ao core/) permanece em `MainWindow`.

### 6. __init__.py em components/

`flownc/ui/components/__init__.py` exporta os 4 componentes para manter imports limpos:
```python
from ui.components import HeaderBar, CompositorPanel, ProgramListPanel, SummaryPanel
```

## Risks / Trade-offs

- **Regressão de sinais:** ao mover `connect()` de `_build_ui()` para o maestro, é fácil esquecer uma conexão. Mitigação: rodar o smoke manual após cada componente extraído, não só ao final.
- **Tamanho da tarefa:** `main_window.py` tem ~1 200 linhas. Extrair 4 componentes é trabalho de precisão. Mitigação: extrair um componente por vez, rodar `pytest` após cada um.
- **QSplitter e proporção em resize:** `setSizes()` usa pixels absolutos; se a janela for redimensionada, a proporção pode ser perdida. Mitigação: conectar `splitter.splitterMoved` para recalcular se necessário (post-MVP).
- **Aba Verificações descontinuada:** a aba VERIFICAÇÕES some do QTabWidget. O botão no header é um stub por ora. Mitigação: documentar como blocker conhecido e retomar em change futura.

## Migration Plan

1. Criar `flownc/ui/components/__init__.py` (vazio inicialmente)
2. Extrair `HeaderBar` → mover código do topo de `_build_ui()`
3. Extrair `CompositorPanel` → mover código do compositor/edições montadas
4. Extrair `ProgramListPanel` → mover código da lista de arquivos
5. Extrair `SummaryPanel` → mover código do painel de resumo/CTA
6. Refatorar `_build_ui()` em `MainWindow` para usar QSplitter + QStackedWidget + os 4 componentes
7. Reconectar todos os sinais no maestro
8. `pytest` completo — zero regressões
9. Smoke manual: abrir app, montar edição, selecionar arquivo, abrir editor, voltar ao resumo

**Rollback:** a refatoração é interna à `ui/`; core/ e CLI não mudam. Reverter é `git checkout flownc/ui/`.

## Open Questions

- A aba VERIFICAÇÕES: stub no header é suficiente por agora, ou precisa de rota mínima funcional? (Assumido: stub aceitável)
- `QSplitter` deve salvar a posição no `AppSettings`? (Assumido: não — pós-MVP)
