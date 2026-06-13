## Purpose

Define a tela Códigos: biblioteca código + descrição (com bloco opcional) que alimenta todos os dropdowns.

## ADDED Requirements

### Requirement: Tela Códigos como página dedicada

O sistema SHALL implementar a biblioteca de códigos como uma **tela dedicada** (não modal), acessível pelo rail. A tela SHALL exibir a lista de todos os códigos cadastrados com **código** e **descrição** em cada linha, campo de **busca** (por código ou descrição), contador "N cadastrados" e botão **"+ Adicionar código"**.

#### Scenario: Tela acessível pelo rail

- **WHEN** o usuário clica em "Códigos" no rail
- **THEN** a tela Códigos é exibida com a lista de todos os códigos da biblioteca

#### Scenario: Busca filtra por código ou descrição

- **WHEN** o usuário digita "M8" no campo de busca
- **THEN** a lista filtra e exibe apenas os itens cujo código ou descrição contêm "M8"

### Requirement: Adicionar código com suporte a bloco

O botão "+ Adicionar código" SHALL abrir um formulário com campos: **código** (obrigatório), **descrição** (obrigatório) e — opcional — **bloco de linhas** (textarea). Códigos com bloco SHALL ser marcados com a tag **"bloco"** na lista e SHALL estar disponíveis como **modelos reutilizáveis** nas funcionalidades "Inserir bloco" do compositor e do editor.

#### Scenario: Adicionar código simples

- **WHEN** o usuário preenche código e descrição e confirma
- **THEN** o novo código aparece na lista e fica disponível nos dropdowns de todos os painéis

#### Scenario: Código com bloco ganha tag "bloco"

- **WHEN** o usuário adiciona um código com o campo bloco preenchido
- **THEN** o código aparece na lista com a tag "bloco" e está disponível como modelo nos inseridores de bloco

### Requirement: Todos os dropdowns do app alimentados pela biblioteca

Os dropdowns de origem, destino, localizar, substituir e âncoras de bloco em **todas as telas** SHALL ser alimentados pela mesma `library_store`. Qualquer código adicionado ou editado na tela Códigos SHALL refletir imediatamente nos dropdowns de todas as outras telas.

#### Scenario: Código novo aparece imediatamente nos dropdowns

- **WHEN** o usuário adiciona um código na tela Códigos e volta para a tela Lote
- **THEN** o novo código aparece no dropdown de origem do compositor