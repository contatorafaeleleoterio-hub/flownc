## ADDED Requirements

### Requirement: Aba "Inserir bloco" no compositor da tela Lote

A aba "➕ Inserir bloco" do compositor SHALL oferecer: **textarea** "Bloco a inserir (uma instrução por linha)", seletor de **posição** ("Abaixo da 1ª ocorrência de [código ▾]" ou "Abaixo da linha Nº [n]" com aviso de variabilidade entre programas), **chips de modelos salvos** (blocos reutilizáveis da biblioteca de códigos), e **prévia real** (trecho do primeiro programa marcado com as linhas novas destacadas com `+ ▶`). O botão "+ Adicionar ao lote" SHALL criar um cartão de tipo bloco.

#### Scenario: Prévia real do primeiro programa marcado

- **WHEN** o usuário preenche o textarea e escolhe posição ancorada em G54
- **THEN** a prévia exibe o trecho exato do primeiro programa marcado que receberia o bloco, com as linhas novas marcadas com "+ ▶"

#### Scenario: Cartão de bloco criado com tipo correto

- **WHEN** o usuário clica "+ Adicionar ao lote" na aba inserir bloco
- **THEN** um cartão numerado do tipo "➕ bloco · N linhas após G54" é adicionado à lista de edições

#### Scenario: Aviso ao usar posição por número de linha

- **WHEN** o usuário seleciona "Abaixo da linha Nº [n]" como posição
- **THEN** um aviso é exibido: "o número da linha pode variar entre programas"

### Requirement: "Inserir bloco" na toolbar do Editor

A toolbar do editor SHALL ter um **grupo "➕ Inserir bloco"** que abre um modal com: modelos salvos (chips), textarea, seletor de posição (abaixo da linha Nº / abaixo da 1ª ocorrência de um código) e prévia do resultado no arquivo aberto. Se o código-âncora não existir no arquivo, a prévia SHALL avisar "não aparece neste arquivo — nada será inserido" e o botão de inserir SHALL ser bloqueado.

#### Scenario: Prévia do editor mostra resultado no arquivo atual

- **WHEN** o usuário preenche o bloco e escolhe âncora G54
- **THEN** a prévia do modal mostra o trecho do arquivo aberto onde o bloco seria inserido

#### Scenario: Âncora inexistente bloqueia inserção

- **WHEN** o código-âncora escolhido não existe no arquivo aberto
- **THEN** a prévia exibe "não aparece neste arquivo — nada será inserido" e o botão de inserir fica desabilitado

#### Scenario: Inserção acontece no buffer (não salva)

- **WHEN** o usuário confirma a inserção no editor
- **THEN** o bloco é inserido no buffer do editor; o arquivo em disco NÃO é tocado até um Salvar explícito

### Requirement: Modelos de bloco reutilizáveis da biblioteca

O sistema SHALL disponibilizar como **chips de modelo** os códigos da biblioteca que possuem bloco cadastrado. Clicar num chip SHALL preencher o textarea com o bloco do modelo. Os chips SHALL estar presentes tanto na aba do compositor quanto no modal do editor.

#### Scenario: Chips de modelos refletem biblioteca

- **WHEN** o usuário abre a aba "Inserir bloco" ou o modal do editor
- **THEN** os chips de modelos exibem apenas os códigos da biblioteca que têm bloco cadastrado
