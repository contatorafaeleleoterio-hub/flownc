## ADDED Requirements

### Requirement: Um único checkbox por linha na lista de programas

O `ProgramListPanel` SHALL exibir exatamente um `QCheckBox` por linha de programa. Qualquer checkbox duplicado proveniente da implementação anterior SHALL ser removido. O checkbox existente que controla a seleção para o lote MUST ser preservado e continuar emitindo os mesmos sinais.

#### Scenario: Um checkbox por linha

- **WHEN** a lista de programas é renderizada com N arquivos
- **THEN** cada linha contém exatamente um QCheckBox visível

#### Scenario: Sinal de seleção preservado

- **WHEN** o operador marca ou desmarca o checkbox de uma linha
- **THEN** o sinal de seleção existente é emitido (comportamento idêntico ao anterior)

### Requirement: Linha desmarcada com estilo .file.off

O `ProgramListPanel` SHALL aplicar estilo visual diferenciado (propriedade QSS `file-off` ou classe dinâmica equivalente) à linha de qualquer programa desmarcado, tornando-a visualmente esmaecida conforme o mockup.

#### Scenario: Linha desmarcada fica esmaecida

- **WHEN** o operador desmarca o checkbox de um programa
- **THEN** a linha correspondente recebe o estilo esmaecido (.file.off) imediatamente

#### Scenario: Linha marcada volta ao normal

- **WHEN** o operador marca o checkbox de um programa previamente desmarcado
- **THEN** o estilo .file.off é removido e a linha volta à aparência padrão

### Requirement: Título "Seleção de Programas" e metadados relativos

O cabeçalho do `ProgramListPanel` SHALL exibir o título `Seleção de Programas`. Os metadados de cada arquivo (tamanho, data) SHALL ser exibidos em formato relativo (ex.: "2,3 KB · há 3 dias"), não como caminho absoluto.

#### Scenario: Título correto

- **WHEN** o ProgramListPanel é exibido
- **THEN** o cabeçalho mostra o texto "Seleção de Programas"

#### Scenario: Metadados relativos

- **WHEN** um arquivo é listado com data e tamanho disponíveis
- **THEN** o metadado exibido usa formato relativo (tamanho humanizado + tempo relativo), não caminho absoluto

### Requirement: Estado "em edição" com botão Voltar contextual

A linha do arquivo atualmente aberto no editor SHALL receber estado visual "em edição" (destaque de borda/fundo). O botão `✎ Editar` dessa linha SHALL trocar para `Voltar` (estilo neutro/secundário). Ao clicar em `Voltar`, o `ProgramListPanel` SHALL emitir o sinal `fechar_editor_solicitado()`.

#### Scenario: Botão Voltar aparece na linha em edição

- **WHEN** o editor é aberto com um arquivo
- **THEN** a linha desse arquivo exibe o botão "Voltar" no lugar de "✎ Editar" e recebe destaque visual

#### Scenario: Botão Editar volta ao fechar o editor

- **WHEN** o editor é fechado
- **THEN** a linha do arquivo retorna ao botão "✎ Editar" e ao estilo normal

#### Scenario: Clicar em Voltar emite sinal

- **WHEN** o operador clica em "Voltar" na linha em edição
- **THEN** o ProgramListPanel emite o sinal `fechar_editor_solicitado()`

### Requirement: "+ Adicionar programas" no painel de programas

O `ProgramListPanel` SHALL exibir um botão `+ Adicionar programas` em seu cabeçalho. Clicar nele SHALL acionar o mesmo handler de abertura de pasta/arquivos já existente em `MainWindow`. O estado vazio da lista SHALL exibir CTA destacado convidando o operador a adicionar programas.

#### Scenario: Botão presente no cabeçalho

- **WHEN** o ProgramListPanel é exibido
- **THEN** o botão "+ Adicionar programas" está visível no cabeçalho do painel

#### Scenario: Estado vazio com CTA

- **WHEN** nenhum programa foi adicionado
- **THEN** a área da lista exibe uma mensagem/CTA destacado orientando o operador a adicionar programas
