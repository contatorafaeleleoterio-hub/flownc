## Purpose

Define o compositor de edições da tela Lote com duas abas (Trocar código e Inserir bloco) e um único botão de adicionar ao lote, conforme o mockup v4.

## ADDED Requirements

### Requirement: Compositor com duas abas

O sistema SHALL implementar o compositor de edições como um `QTabWidget` com exatamente **duas abas**: "Trocar código" e "➕ Inserir bloco". As abas SHALL compartilhar o mesmo botão **"+ Adicionar ao lote"** abaixo do tab widget. O botão SHALL estar desabilitado até que os campos obrigatórios da aba ativa estejam preenchidos.

#### Scenario: Duas abas sempre presentes

- **WHEN** a tela Lote é aberta
- **THEN** o compositor exibe as abas "Trocar código" e "➕ Inserir bloco" e o botão "+ Adicionar ao lote" abaixo

#### Scenario: Botão desabilitado sem campos preenchidos

- **WHEN** a aba "Trocar código" está ativa e nenhum código de origem foi selecionado
- **THEN** o botão "+ Adicionar ao lote" permanece desabilitado

### Requirement: Aba "Trocar código" com dois dropdowns pesquisáveis

A aba "Trocar código" SHALL exibir dois `QComboBox` pesquisáveis: **Código de origem** e **Trocar por**. Cada dropdown SHALL abrir com campo de busca, seção **"★ Frequentes"** (5 mais usados) e lista completa da biblioteca. Os dropdowns SHALL mostrar **só o código** como texto visível; a **descrição** SHALL aparecer apenas em **tooltip** (ao passar o mouse). O botão "+ Adicionar ao lote" SHALL ser habilitado somente quando **ambos** os campos estiverem preenchidos.

#### Scenario: Dropdown mostra só código, descrição no tooltip

- **WHEN** o usuário passa o mouse sobre um item no dropdown de origem
- **THEN** o tooltip exibe a descrição cadastrada do código; o texto visível do item é só o código

#### Scenario: Seção "★ Frequentes" presente

- **WHEN** o usuário abre um dos dropdowns
- **THEN** os 5 códigos mais usados aparecem no topo com a marcação "★"

#### Scenario: Botão habilitado só com origem e destino

- **WHEN** o usuário seleciona o código de origem mas não o destino
- **THEN** o botão "+ Adicionar ao lote" permanece desabilitado

#### Scenario: Botão habilitado com ambos preenchidos

- **WHEN** o usuário seleciona código de origem e destino
- **THEN** o botão "+ Adicionar ao lote" fica habilitado

### Requirement: Opção explícita "✕ Remover" no dropdown de destino

O dropdown "Trocar por" SHALL incluir o item especial **"✕ Remover (sem código)"** como primeira opção. Ao selecioná-la, o botão de destino SHALL exibir visual vermelho com texto "✕ remover". A opção "destino vazio" NOT SHALL ser interpretada como remoção — apenas a escolha explícita de "✕ Remover" configura o cartão como remoção.

#### Scenario: Selecionar "✕ Remover" exibe visual vermelho

- **WHEN** o usuário seleciona "✕ Remover (sem código)" no dropdown de destino
- **THEN** o dropdown exibe visual vermelho com "✕ remover" e o botão "+ Adicionar ao lote" fica habilitado

#### Scenario: Destino vazio não cria edição de remoção

- **WHEN** o usuário seleciona apenas a origem e tenta adicionar ao lote sem destino
- **THEN** o botão "+ Adicionar ao lote" permanece desabilitado (não cria edição)

### Requirement: Lote de edições como lista de cartões numerados

O sistema SHALL exibir as edições adicionadas como **cartões numerados** na lista de edições. Cada cartão SHALL mostrar: número sequencial, tipo (troca `A → B` ou `A → remover` ou `➕ bloco`), e ações **✎ editar**, **⧉ duplicar**, **✕ excluir**. Clicar em ✎ SHALL carregar a edição de volta no compositor na aba correta.

#### Scenario: Adicionar edição cria cartão numerado

- **WHEN** o usuário clica em "+ Adicionar ao lote"
- **THEN** um cartão numerado é adicionado à lista de edições; o cartão novo pisca brevemente e a lista rola até ele

#### Scenario: Editar cartão carrega no compositor

- **WHEN** o usuário clica em ✎ num cartão de troca de código
- **THEN** o compositor vai para a aba "Trocar código" com os valores do cartão preenchidos; o botão muda para "Atualizar"

#### Scenario: Excluir cartão remove da lista

- **WHEN** o usuário clica em ✕ num cartão
- **THEN** o cartão é removido e os demais são renumerados

### Requirement: Destaque âmbar para conflitos

O sistema SHALL detectar conflito quando **dois cartões têm o mesmo código de origem**. Cartões em conflito SHALL ficar âmbar com ícone "▲ Conflito". O chip do painel SHALL mostrar "⚠ N conflitos" quando houver ao menos um.

#### Scenario: Dois cartões com mesma origem detectam conflito

- **WHEN** o usuário adiciona dois cartões que compartilham o mesmo código de origem
- **THEN** ambos os cartões ficam âmbar com "▲ Conflito" e o chip exibe "⚠ 1 conflito"

### Requirement: CTA "Conferir lote →" habilitado com condições

O sistema SHALL exibir o botão laranja **"Conferir lote →"** no rodapé da lista de edições com o subtítulo "varre os programas e mostra os números reais — nada é gravado". O botão SHALL ser desabilitado se não houver edições **ou** se não houver programas marcados. O tooltip do botão desabilitado SHALL explicar o que falta.

#### Scenario: CTA desabilitado sem edições

- **WHEN** a lista de edições está vazia
- **THEN** o botão "Conferir lote →" está desabilitado com tooltip "Adicione ao menos uma edição"

#### Scenario: CTA desabilitado sem programas marcados

- **WHEN** há edições mas nenhum programa está marcado
- **THEN** o botão "Conferir lote →" está desabilitado com tooltip "Marque ao menos um programa"

#### Scenario: CTA habilitado com edições e programas marcados

- **WHEN** há ao menos uma edição e ao menos um programa marcado
- **THEN** o botão "Conferir lote →" está habilitado