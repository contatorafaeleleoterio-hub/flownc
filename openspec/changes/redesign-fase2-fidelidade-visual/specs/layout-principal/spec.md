## MODIFIED Requirements

### Requirement: HeaderBar com logo, perfil e ações

O sistema SHALL exibir uma barra de cabeçalho fixo (`HeaderBar`) com: logo/marca `FlowNC` com subtítulo conforme o mockup aprovado, seletor de perfil/máquina (`QComboBox`) à esquerda, botão `Salvar perfil` à **esquerda** (próximo ao seletor), botão `+ Adicionar código` com cor azul sólido (`COLOR_INTERACTIVE`). Os botões `Abrir pasta` e `Abrir programa(s)` **não** aparecem no HeaderBar — foram movidos para o `ProgramListPanel`. A altura SHALL ser de 70 px conforme o token `DIM_HEADER`.

#### Scenario: Presença dos elementos obrigatórios

- **WHEN** o app é iniciado
- **THEN** a HeaderBar exibe: logo FlowNC com subtítulo, ComboBox de perfil, botão "Salvar perfil" à esquerda e botão "+ Adicionar código" azul sólido; sem botões "Abrir pasta" ou "Abrir programa(s)"

#### Scenario: Botão + Adicionar código com cor correta

- **WHEN** o app é iniciado
- **THEN** o botão "+ Adicionar código" exibe fundo com a cor `COLOR_INTERACTIVE` (azul sólido do mockup)

#### Scenario: Seleção de perfil

- **WHEN** o usuário seleciona um item diferente no ComboBox de perfil do HeaderBar
- **THEN** HeaderBar emite o sinal `perfil_alterado(nome: str)` e MainWindow carrega o preset correspondente

### Requirement: SummaryPanel com escopo N programas e ações clicáveis

O `SummaryPanel` SHALL exibir o escopo como `N programas` (contagem dos programas selecionados), não como `todos/sel.`. As ações dos cards de regra (`✎ editar`, `⧉ duplicar`, `🗑 excluir`) SHALL ser `QPushButton` clicáveis que emitem sinais `regra_editar(index)`, `regra_duplicar(index)` e `regra_excluir(index)` respectivamente (stubs na FASE 2). O selo de backup SHALL exibir um ícone de escudo e duas linhas de texto conforme o mockup.

#### Scenario: Escopo como N programas

- **WHEN** há N programas selecionados
- **THEN** o SummaryPanel exibe o escopo como "N programas" (ex.: "3 programas")

#### Scenario: Ações dos cards clicáveis

- **WHEN** o usuário clica em ✎, ⧉ ou 🗑 em um card de regra
- **THEN** o botão responde visualmente ao clique (enabled, sem erro) e emite o sinal correspondente

#### Scenario: Selo de backup em 2 linhas com escudo

- **WHEN** o SummaryPanel exibe o selo de backup
- **THEN** o selo contém um ícone de escudo e duas linhas de texto conforme o mockup aprovado
