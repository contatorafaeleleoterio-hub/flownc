## ADDED Requirements

### Requirement: Controle de backup na tela Lote, antes do CTA

O sistema SHALL exibir o controle de pasta de backup **na tela Lote**, no rodapé do painel "Lote de
edições", **imediatamente antes** do botão "Conferir lote →". O controle SHALL ser **sutil**
(visualmente secundário, menor que o antigo chip do topo). Clicar no controle SHALL abrir o seletor
de pasta; ao confirmar, o caminho escolhido SHALL passar a ser exibido.

#### Scenario: Controle aparece antes do CTA

- **WHEN** a tela Lote é exibida
- **THEN** o controle de backup aparece logo acima/antes do botão "Conferir lote →", em estilo discreto

#### Scenario: Clicar no controle abre o seletor de pasta

- **WHEN** o operador clica no controle de backup
- **THEN** um diálogo de seleção de pasta é aberto; ao confirmar, o caminho escolhido é exibido no controle

### Requirement: Estado "não configurado" sem caminho fake

O sistema NOT SHALL exibir um caminho de backup padrão/fictício. Enquanto nenhuma pasta tiver sido
escolhida (e nenhuma vier das configurações), o controle SHALL exibir um estado **"não
configurado"** (ex.: "Definir pasta de backup"). Quando configurado, SHALL exibir o caminho de forma
discreta com opção de trocar.

#### Scenario: Primeira vez mostra "não configurado"

- **WHEN** o app é aberto sem nenhuma pasta de backup definida
- **THEN** o controle exibe "Definir pasta de backup", não um caminho fictício

#### Scenario: Após escolher mostra o caminho

- **WHEN** o operador escolhe uma pasta de backup
- **THEN** o controle passa a exibir esse caminho de forma discreta com opção de trocar

### Requirement: Guarda de backup ao executar

Ao clicar em "Conferir lote →" **sem pasta de backup configurada**, o sistema SHALL abrir o
**seletor de pasta** antes de prosseguir. Se o operador escolher uma pasta, o sistema SHALL seguir
direto para a conferência. Se o operador cancelar o seletor, o sistema NOT SHALL executar (não abre
a conferência). A guarda NOT SHALL alterar as demais condições de habilitação do CTA (edições e
programas).

#### Scenario: Executar sem backup abre o seletor

- **WHEN** há edições e programas válidos, o backup não está configurado e o operador clica em "Conferir lote →"
- **THEN** o seletor de pasta de backup é aberto antes de qualquer conferência

#### Scenario: Escolher pasta segue para a conferência

- **WHEN** o operador escolhe uma pasta no seletor aberto pela guarda
- **THEN** o caminho é gravado e a conferência abre em seguida

#### Scenario: Cancelar o seletor não executa

- **WHEN** o operador cancela o seletor aberto pela guarda
- **THEN** a conferência não abre e o lote permanece como estava

#### Scenario: Com backup já configurado executa direto

- **WHEN** o backup já está configurado e o operador clica em "Conferir lote →"
- **THEN** a conferência abre direto, sem reabrir o seletor
