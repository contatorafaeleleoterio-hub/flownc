## MODIFIED Requirements

### Requirement: Barra de topo global persistente

O sistema SHALL exibir uma barra de topo (`TopBar`) fixa acima do `QStackedWidget`, visível em **todas as telas**. A barra SHALL conter o logotipo/nome "FlowNC" à esquerda. A barra NOT SHALL conter chip/controle de backup — a escolha da pasta de backup é função da tela Lote, antes do CTA "Conferir lote →".

#### Scenario: Topo visível em todas as telas

- **WHEN** o usuário navega entre qualquer uma das 4 telas
- **THEN** a barra de topo permanece visível com a marca "FlowNC"

#### Scenario: Topo não tem controle de backup

- **WHEN** a barra de topo é exibida
- **THEN** não há chip nem botão de pasta de backup no topo

## REMOVED Requirements

### Requirement: Chip de backup clicável

**Reason**: O chip de backup no topo ficava fora do caminho de execução, com um caminho fictício que
dava falsa sensação de "configurado". O controle de backup foi movido para a tela Lote,
imediatamente antes do CTA, em estilo sutil, com estado real "não configurado" e guarda no executar
(capacidade `backup-antes-de-executar`).
**Migration**: A pasta de backup passa a ser escolhida pelo controle na tela Lote (ou pelo seletor
que abre ao clicar em "Conferir lote →" sem backup). A linha de backup no modal de Conferência
permanece como confirmação.
