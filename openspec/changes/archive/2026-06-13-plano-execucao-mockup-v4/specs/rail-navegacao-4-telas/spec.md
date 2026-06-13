## Purpose

Define a barra lateral (rail) com os 4 lugares fixos: Lote, Editor, Códigos e Histórico.

## ADDED Requirements

### Requirement: Rail lateral com 4 botões-lugar

O sistema SHALL exibir um rail lateral escuro (cor de fundo `COLOR_RAIL`) fixo à esquerda da janela principal, com 4 botões verticais: **Lote**, **Editor**, **Códigos**, **Histórico**. O botão ativo SHALL ter um filete laranja (`COLOR_CTA`) na borda esquerda. O rail SHALL ter largura fixa (~56px).

#### Scenario: Botão ativo com filete laranja

- **WHEN** a tela Lote está ativa
- **THEN** o botão "Lote" no rail exibe o filete laranja e os demais botões não têm filete

#### Scenario: Clicar em botão muda tela ativa

- **WHEN** o usuário clica em "Histórico" no rail
- **THEN** a área principal exibe a tela Histórico e o filete laranja move para o botão "Histórico"

### Requirement: Bolinha de status no botão Editor

O sistema SHALL exibir uma **bolinha laranja** sobre o ícone do botão "Editor" no rail quando houver **alteração não salva** no editor. A bolinha MUST desaparecer ao salvar ou descartar a edição.

#### Scenario: Bolinha aparece ao editar sem salvar

- **WHEN** o usuário abre um arquivo no editor e digita qualquer texto
- **THEN** o botão "Editor" no rail exibe a bolinha laranja

#### Scenario: Bolinha some ao salvar

- **WHEN** o usuário salva o arquivo no editor
- **THEN** a bolinha laranja no botão "Editor" desaparece

### Requirement: QStackedWidget de telas

O sistema SHALL implementar a área principal como `QStackedWidget` com 4 índices fixos: 0 = Lote, 1 = Editor, 2 = Códigos, 3 = Histórico. O rail SHALL emitir o sinal `tela_mudou(int)` ao ser clicado; o `MainWindow` SHALL responder chamando `stack.setCurrentIndex(indice)`.

#### Scenario: Troca de tela sem recriar widgets

- **WHEN** o usuário alterna entre telas múltiplas vezes
- **THEN** os widgets das telas mantêm seu estado interno (a lista de programas carregados na tela Lote continua preenchida ao voltar para ela)