## ADDED Requirements

### Requirement: Barra de topo global persistente

O sistema SHALL exibir uma barra de topo (`TopBar`) fixa acima do `QStackedWidget`, visível em **todas as telas**. A barra SHALL conter o logotipo/nome "FlowNC" à esquerda, o seletor de configuração ao centro e o chip de backup à direita.

#### Scenario: Topo visível em todas as telas

- **WHEN** o usuário navega entre qualquer uma das 4 telas
- **THEN** a barra de topo permanece visível com o mesmo conteúdo

### Requirement: Seletor de configuração/receita

O sistema SHALL exibir um `QComboBox` de configurações salvas no topo. O menu SHALL incluir o item especial **"💾 Salvar lote atual como…"** no fim da lista. Selecionar uma receita SHALL emitir `receita_selecionada(nome: str)` para que a tela Lote carregue as edições salvas. Se houver um lote já montado ao selecionar uma receita, o sistema SHALL exibir confirmação antes de substituir.

#### Scenario: Carregar receita com lote vazio

- **WHEN** o lote de edições está vazio e o usuário seleciona uma receita
- **THEN** as edições da receita são carregadas na tela Lote sem confirmação

#### Scenario: Carregar receita com lote preenchido pede confirmação

- **WHEN** há edições no lote e o usuário seleciona uma receita diferente
- **THEN** uma caixa de confirmação é exibida antes de substituir o lote atual

#### Scenario: Item "Salvar lote atual como…" está sempre presente

- **WHEN** o ComboBox de configurações é aberto
- **THEN** o item "💾 Salvar lote atual como…" aparece no fim da lista independentemente do conteúdo

### Requirement: Chip de backup clicável

O sistema SHALL exibir um chip/botão no topo mostrando o **caminho da pasta de backup atual** (ex.: `D:\CNC\backup\`). Clicar no chip SHALL abrir um diálogo de seleção de pasta para trocar o destino do backup.

#### Scenario: Chip exibe pasta de backup atual

- **WHEN** o app é iniciado com uma pasta de backup configurada
- **THEN** o chip exibe o caminho dessa pasta no topo

#### Scenario: Clicar no chip abre seletor de pasta

- **WHEN** o usuário clica no chip de backup
- **THEN** um diálogo de seleção de pasta é aberto; ao confirmar, o chip é atualizado com o novo caminho
