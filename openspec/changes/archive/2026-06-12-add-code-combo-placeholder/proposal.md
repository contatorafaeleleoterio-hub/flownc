## Why

Os campos **Código de origem** e **Trocar por** do compositor começam vazios, sem indicador visual de que são menus suspensos e sem placeholder-guide. Usuário clica esperando encontrar uma lista, mas sem feedback inicial. Falta clarity de que ali há uma seleção, não um campo de texto puro.

## What Changes

- Adiciona placeholder "Selecione o código" (cinza, some ao digitar/escolher) nos combos `cb_origem` e `cb_destino` 
- Adiciona seta visual unicode (▾ quando fechado, ▴ quando aberto) à direita de cada combo, indicando estado do menu suspenso
- Implementação por subclasse `CodeCombo(QComboBox)` com draw customizado da seta, sem assets novos
- Sem mudança em API, sinais ou comportamento — apenas visual

## Capabilities

### New Capabilities

- `code-input-feedback`: Interface de seleção de código com placeholder e indicador visual de menu suspenso

### Modified Capabilities

<!-- Nenhuma requirement de comportamento muda; é ajuste visual puro. -->

## Impact

- **Code**: `flownc/ui/components/compositor.py` (nova classe `CodeCombo`, fábrica `_make_code_combo` reduzida), `flownc/ui/style.qss` (esconde seta nativa de `CodeCombo`)
- **Testing**: Testes visuais (app manual) — placeholder + seta em estado aberto/fechado; testes automatizados não quebram (type signature `QComboBox` mantém compatibilidade)
- **Scope**: Muito baixo — 2 arquivos, sem novos assets, sem gerar `.exe`
