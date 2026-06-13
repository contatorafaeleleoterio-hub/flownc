## MODIFIED Requirements

### Requirement: Aba "Trocar código" com dois dropdowns pesquisáveis

A aba "Trocar código" SHALL exibir dois `QComboBox` pesquisáveis: **Código de origem** e **Trocar por**. Cada dropdown SHALL abrir com campo de busca, seção **"★ Frequentes"** (5 mais usados) e lista completa da biblioteca. Os dropdowns SHALL mostrar **só o código** como texto visível; a **descrição** SHALL aparecer apenas em **tooltip** (ao passar o mouse). O botão "+ Adicionar ao lote" SHALL ser habilitado somente quando **ambos** os campos estiverem preenchidos **e houver ao menos 1 programa marcado** no painel Programas.

#### Scenario: Dropdown mostra só código, descrição no tooltip

- **WHEN** o usuário passa o mouse sobre um item no dropdown de origem
- **THEN** o tooltip exibe a descrição cadastrada do código; o texto visível do item é só o código

#### Scenario: Seção "★ Frequentes" presente

- **WHEN** o usuário abre um dos dropdowns
- **THEN** os 5 códigos mais usados aparecem no topo com a marcação "★"

#### Scenario: Botão habilitado só com origem e destino

- **WHEN** o usuário seleciona o código de origem mas não o destino
- **THEN** o botão "+ Adicionar ao lote" permanece desabilitado

#### Scenario: Botão exige programas marcados

- **WHEN** o usuário preenche origem e destino mas nenhum programa está marcado
- **THEN** o botão "+ Adicionar ao lote" permanece desabilitado com tooltip "Marque ao menos 1 programa"

#### Scenario: Botão habilitado com campos e programas

- **WHEN** o usuário seleciona origem e destino e há ao menos 1 programa marcado
- **THEN** o botão "+ Adicionar ao lote" fica habilitado

### Requirement: Lote de edições como lista de cartões numerados

O sistema SHALL exibir as edições adicionadas como **cartões numerados** na lista de edições. Cada cartão SHALL mostrar: número sequencial, a edição (troca `A → B`, `A → remover` ou `➕ bloco`) e, na ponta direita, a **contagem de programas** da edição (clicável, abre o dropdown de programas) seguida das ações **⧉ duplicar** e **✕ excluir**. Para cartões de troca de código, origem e destino SHALL ser **editáveis inline** (clique abre o dropdown da biblioteca no próprio cartão). Ao adicionar, o cartão novo SHALL piscar brevemente e a lista SHALL rolar até ele.

#### Scenario: Adicionar edição cria cartão numerado

- **WHEN** o usuário clica em "+ Adicionar ao lote"
- **THEN** um cartão numerado é adicionado à lista; o cartão novo pisca e a lista rola até ele

#### Scenario: Cartão exibe contagem de programas e ações

- **WHEN** um cartão de troca com 3 programas é exibido
- **THEN** o cartão mostra "3 programas" (clicável), ⧉ duplicar e ✕ excluir na ponta direita

#### Scenario: Editar origem/destino inline

- **WHEN** o usuário clica no código de origem ou destino de um cartão de troca
- **THEN** o dropdown pesquisável abre no próprio cartão e a escolha atualiza a edição na hora

#### Scenario: Excluir cartão remove da lista

- **WHEN** o usuário clica em ✕ num cartão
- **THEN** o cartão é removido e os demais são renumerados

### Requirement: CTA "Conferir lote →" habilitado com condições

O sistema SHALL exibir o botão laranja **"Conferir lote →"** no rodapé da lista de edições com o subtítulo "varre os programas e mostra os números reais — nada é gravado". O botão SHALL ser desabilitado se não houver edições **ou** se **alguma edição estiver sem programas** no seu conjunto. O tooltip do botão desabilitado SHALL explicar o que falta.

#### Scenario: CTA desabilitado sem edições

- **WHEN** a lista de edições está vazia
- **THEN** o botão "Conferir lote →" está desabilitado com tooltip "Adicione ao menos uma edição"

#### Scenario: CTA desabilitado com edição sem programas

- **WHEN** há edições mas alguma ficou com 0 programas no conjunto dela
- **THEN** o botão "Conferir lote →" está desabilitado com tooltip indicando a edição sem programas

#### Scenario: CTA habilitado com todas as edições com programas

- **WHEN** há ao menos uma edição e todas têm ≥1 programa no conjunto
- **THEN** o botão "Conferir lote →" está habilitado
