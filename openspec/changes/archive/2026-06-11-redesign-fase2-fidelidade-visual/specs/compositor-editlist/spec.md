## ADDED Requirements

### Requirement: Compositor no formato editlist com dois campos separados

O `CompositorPanel` SHALL exibir dois `QComboBox` independentes — `origem` e `destino` — populados com a lista da biblioteca (código como texto visível; descrição no `ToolTipRole`). O campo de rascunho SHALL estar sempre visível no fim da lista de edições montadas, com visual diferenciado (fundo `--color-bg-subtle`, borda tracejada). Nenhum par é confirmado automaticamente: o operador escolhe os dois campos e clica em "+ adicionar outra edição".

#### Scenario: Dois campos independentes visíveis

- **WHEN** o CompositorPanel é exibido
- **THEN** dois QComboBox distintos (origem e destino) estão visíveis e populados com os códigos da biblioteca

#### Scenario: Rascunho no fim da lista

- **WHEN** o CompositorPanel é exibido com lista vazia ou com edições montadas
- **THEN** a linha em-edição (rascunho) aparece sempre ao final da lista, com fundo e borda distintos das linhas confirmadas

#### Scenario: Descrição no hover, não inline

- **WHEN** o operador passa o mouse sobre um item nos QComboBox de origem ou destino
- **THEN** o tooltip exibe a descrição do código; o texto do item mostra apenas o código

### Requirement: Lista "Edições montadas" com ✕ por linha

O CompositorPanel SHALL exibir a lista `Edições montadas (N)` com cada par origem→destino confirmado em linha separada. Cada linha SHALL ter um botão `✕` que remove a edição ao ser clicado, emitindo o sinal `edicao_removida(index: int)`.

#### Scenario: Contagem no título

- **WHEN** há N edições montadas
- **THEN** o título exibe "Edições montadas (N)"

#### Scenario: Remover edição pelo ✕

- **WHEN** o operador clica no botão ✕ de uma linha
- **THEN** essa edição é removida da lista e a contagem no título é atualizada

### Requirement: CTA "Adicionar edição ao lote →" no painel de programas

O `CompositorPanel` SHALL emitir o sinal `adicionar_ao_lote()` ao clicar no CTA `Adicionar edição ao lote →`. O botão SHALL estar desabilitado quando não houver nenhuma edição montada.

#### Scenario: CTA desabilitado sem edições

- **WHEN** a lista de edições montadas está vazia
- **THEN** o botão "Adicionar edição ao lote →" está desabilitado (setEnabled(False))

#### Scenario: CTA habilitado com edições

- **WHEN** há ao menos uma edição montada
- **THEN** o botão "Adicionar edição ao lote →" está habilitado e ao clicar emite o sinal `adicionar_ao_lote()`
