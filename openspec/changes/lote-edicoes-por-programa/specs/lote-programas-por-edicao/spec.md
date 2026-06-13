## ADDED Requirements

### Requirement: Cada edição guarda seu próprio conjunto de programas

O sistema SHALL associar a cada edição do lote um **conjunto próprio de programas**, fotografado no
momento em que o operador clica "+ Adicionar ao lote" (os programas marcados naquele instante no
painel Programas). A conferência e a publicação SHALL aplicar cada edição **apenas aos programas do
conjunto dela**, não a uma marcação global. Alterar a marcação no painel Programas após adicionar
NOT SHALL alterar o conjunto de uma edição já no lote.

#### Scenario: Adicionar fotografa os programas marcados

- **WHEN** o operador marca 10 programas e clica "+ Adicionar ao lote" com uma troca G54 → G55
- **THEN** a edição criada guarda exatamente esses 10 programas, independente de marcações futuras

#### Scenario: Edições diferentes, escopos diferentes

- **WHEN** o operador adiciona G54 → G55 com 10 programas marcados, depois desmarca, marca outros 6 e adiciona M8 → M9
- **THEN** a primeira edição mantém seus 10 programas e a segunda guarda os 6 — sem misturar

#### Scenario: Marcar/desmarcar depois não afeta edições no lote

- **WHEN** o operador altera a marcação no painel Programas após já ter adicionado edições
- **THEN** os conjuntos das edições existentes permanecem inalterados

### Requirement: Contagem de programas e dropdown no cartão

O sistema SHALL exibir, na ponta direita de cada cartão de edição, a **contagem de programas** da
edição (ex.: "3 programas") como um controle clicável. Clicar SHALL abrir um **dropdown** listando
os programas daquela edição (nome em fonte monoespaçada). O cartão SHALL manter também as ações
**⧉ duplicar** e **✕ excluir** a edição.

#### Scenario: Cartão mostra a contagem

- **WHEN** uma edição com 3 programas é exibida no lote
- **THEN** o cartão mostra "3 programas" na ponta direita, ao lado de ⧉ e ✕

#### Scenario: Abrir o dropdown lista os programas

- **WHEN** o operador clica na contagem de programas de um cartão
- **THEN** abre um dropdown com a lista dos programas daquela edição, um por linha

#### Scenario: Excluir o cartão remove a edição inteira

- **WHEN** o operador clica em ✕ no cartão
- **THEN** a edição é removida do lote e os cartões restantes são renumerados

### Requirement: Remover programa de uma edição com desfazer

Cada item do dropdown de programas SHALL ter um botão **✕** para removê-lo da edição. Ao clicar em
✕, o item SHALL ficar **riscado** e o botão SHALL virar **"desfazer"**, permitindo restaurar o
programa. A remoção SHALL ser efetivada no conjunto da edição ao fechar o dropdown; itens riscados
não desfeitos SHALL sair do conjunto. A contagem do cartão SHALL refletir o novo total.

#### Scenario: Remover risca e oferece desfazer

- **WHEN** o operador clica no ✕ de um programa no dropdown
- **THEN** o programa fica riscado e o botão vira "desfazer"

#### Scenario: Desfazer restaura o programa

- **WHEN** o operador clica em "desfazer" de um programa riscado
- **THEN** o programa volta ao normal e permanece no conjunto da edição

#### Scenario: Fechar efetiva as remoções

- **WHEN** o operador risca 1 programa e fecha o dropdown sem desfazer
- **THEN** esse programa sai do conjunto da edição e a contagem do cartão diminui

### Requirement: Edição inline de origem e destino no cartão

Em cartões de **troca de código**, o sistema SHALL permitir editar **origem** e **destino**
diretamente no cartão: clicar no código (ou no indicador de seta/lápis) SHALL abrir o dropdown
pesquisável da biblioteca ali mesmo, e a escolha SHALL atualizar a edição imediatamente, sem
round-trip pelo compositor. O dropdown de destino SHALL manter a opção "✕ Remover (sem código)".

#### Scenario: Clicar na origem abre o dropdown no cartão

- **WHEN** o operador clica no código de origem (ex.: G54) de um cartão de troca
- **THEN** o dropdown pesquisável abre no próprio cartão e permite escolher outro código

#### Scenario: Trocar o destino inline atualiza o cartão

- **WHEN** o operador escolhe um novo destino no dropdown inline do cartão
- **THEN** a fórmula do cartão passa a refletir o novo destino imediatamente

### Requirement: Habilitação por escopo de programas

O sistema SHALL exigir **≥1 programa marcado** para habilitar "+ Adicionar ao lote" (além dos campos
obrigatórios da aba). O sistema SHALL habilitar "Conferir lote →" somente quando houver **≥1 edição**
e **toda edição tiver ≥1 programa**; caso contrário o botão SHALL ficar desabilitado com tooltip
explicando o que falta.

#### Scenario: Não dá para adicionar sem programas marcados

- **WHEN** os campos da aba estão preenchidos mas nenhum programa está marcado
- **THEN** "+ Adicionar ao lote" permanece desabilitado com tooltip "Marque ao menos 1 programa"

#### Scenario: Conferir bloqueado por edição sem programas

- **WHEN** uma edição do lote ficou com 0 programas (todos removidos)
- **THEN** "Conferir lote →" fica desabilitado e o cartão dessa edição mostra estado de aviso

#### Scenario: Conferir habilitado com todas as edições com programas

- **WHEN** há ao menos 1 edição e todas têm ≥1 programa
- **THEN** "Conferir lote →" fica habilitado

### Requirement: Botão "Desmarcar selecionados" no painel Programas

O painel Programas SHALL oferecer um botão **"Desmarcar selecionados"** que limpa toda a marcação
atual de uma vez. O botão SHALL ficar habilitado somente quando houver ao menos 1 programa marcado.

#### Scenario: Desmarcar limpa a seleção atual

- **WHEN** há programas marcados e o operador clica em "Desmarcar selecionados"
- **THEN** nenhum programa fica marcado e o chip "N de M marcados" zera

#### Scenario: Botão desabilitado sem marcação

- **WHEN** nenhum programa está marcado
- **THEN** o botão "Desmarcar selecionados" está desabilitado
