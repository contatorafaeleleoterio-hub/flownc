## Context

Os combos `cb_origem` e `cb_destino` em `compositor.py` são `QComboBox` editáveis criados pela fábrica `_make_code_combo()`. Hoje:
- Começam vazios sem placeholder
- Seta padrão do Qt (imagem nativa), não inverte ao abrir
- Sem feedback visual claro de que são menus suspensos

Plano aprovado: adicionar placeholder "Selecione o código" + seta unicode (▾/▴) que inverte com estado do popup. Sem assets novos — manter escopo em 2 arquivos (compositor.py + style.qss).

## Goals / Non-Goals

**Goals:**
- Placeholder "Selecione o código" visível quando combo vazio
- Seta unicode ▾ quando popup fechado, ▴ quando aberto
- Draw customizado em paintEvent() para evitar assets
- Manter compatibilidade de API (type signature `QComboBox`)

**Non-Goals:**
- Criar assets SVG/PNG ou modificar `.qrc`
- Mudar sinais, comportamento ou API de `QComboBox`
- Alterar lógica de população/commit de códigos
- Gerar `.exe` para verificação (testes + app manual bastam)

## Decisions

### 1. Subclasse `CodeCombo(QComboBox)` em `compositor.py`
**Rationale:** Placeholder em combo editável é do `lineEdit()` interno, não do `QComboBox` em si. Flip ▾→▴ por QSS puro exigiria 2 imagens (assets novos). Subclasse contém tudo em um lugar, evita assets, mantém o código próximo ao uso.

**Alternatives considered:**
- QSS puro: Placeholder funciona, mas seta exigiria `::down-arrow { image: url(...) }` (2 imagens + path frágil)
- Subclasse em módulo separado (`ui/widgets.py`): Escopo sai de 2 arquivos; subclasse é específica de compositor, não reutilizável globalmente

### 2. Seta desenhada em `paintEvent()` com QPainter
**Rationale:** `showPopup()` / `hidePopup()` já sinalizam estado. `paintEvent()` permite draw customizado sem assets. Caractere unicode ▾/▴ é legível, compatível com font.

**Alternatives considered:**
- Imagem SVG: Exigiria `.svg` + `.qrc` + Qt resource compiler; quebra escopo de 2 arquivos
- Emoji (🔽): Rendering inconsistente entre fontes; caractere ASCII é mais confiável

### 3. Esconder seta nativa do Qt via QSS
**Rationale:** QComboBox padrão desenha seta nativa (30px à direita). Para não duplicar, QSS `#CodeCombo::down-arrow { image: none; }` remove a nativa. Drop-down rect mantém espaço para a desenhada.

**Alternatives considered:**
- Não esconder: Seta desenhada + nativa lado a lado (visual ruim)
- Stylesheet global: Afetaria todos os combos do app; escopo específico em `#CodeCombo` é melhor

### 4. Cor da seta em `#56616D` (cinza secundário do mockup)
**Rationale:** Mockup v2 usa cinza para affordances. Placeholder + seta com cor consistente.

**Alternatives considered:**
- Qt default: Menos distinction
- Theme color: Depends em future dark mode; fixed gray é previsível agora

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| QPainter em combo pode impactar performance em listas grandes | Não há listas grandes de combos; paintEvent é leve (1 drawText) |
| Font size hardcoded em `setPixelSize(12)` pode não escalar | Escopo visual = mockup; ajuste manual se necessário |
| Caractere unicode ▾/▴ pode não renderizar em algumas fontes | IBM Plex Sans (padrão FlowNC) suporta; fallback é ▽/△ se necessário |
| `_popup_open` state não sincroniza se popup é ignorado by user | Improvável; showPopup/hidePopup são sempre chamados |

## Migration Plan

1. Implementar subclasse `CodeCombo` em compositor.py
2. Reduzir fábrica `_make_code_combo()` a `return CodeCombo()`
3. Adicionar QSS em style.qss para esconder seta nativa
4. Rodar testes (146 verde esperado, nada quebra)
5. Verificar app manual: placeholder + seta em ambos combos
6. Deploy: nenhuma build-time action (PySide6 bundled, Unicode nativo)

## Open Questions

- Placeholder color (padrão cinza do Qt é ok?) — Se diferente, ajustar em `__init__` via palette.
- Font size 12px é proporcional? — Mockup não especifica; 12px em combo padrão fica legível.
