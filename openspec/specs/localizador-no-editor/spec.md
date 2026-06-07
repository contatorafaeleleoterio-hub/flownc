### Requirement: Localizar código da biblioteca

O sistema SHALL oferecer, no cabeçalho do editor, um **dropdown pesquisável de "Código da biblioteca"** alimentado por `library_store` (a biblioteca de códigos do app). O usuário MUST poder filtrar a lista digitando e escolher o código a ser localizado no arquivo aberto.

#### Scenario: Escolher o código pela biblioteca

- **WHEN** o usuário digita parte de um código no dropdown de localização
- **THEN** a lista é filtrada e, ao escolher um item, esse código passa a ser o alvo da varredura

### Requirement: Varredura conta sem mover o cursor

O sistema SHALL, ao acionar a **Varredura**, contar as ocorrências do código escolhido no buffer em edição **sem mover o cursor de edição nem rolar o texto**. A contagem MUST usar `matcher.find_matches` (mesma semântica de **borda CNC** do motor de Lote), de modo que o número apresentado seja idêntico ao que o Lote encontraria. O resultado MUST exibir **"N encontrados"** e a **posição "i/N"** da ocorrência corrente.

#### Scenario: Contar sem deslocar a visão

- **WHEN** o usuário aciona a Varredura
- **THEN** o editor mostra "N encontrados" e "i/N" sem rolar o texto nem mover o cursor de edição

#### Scenario: Contagem idêntica à do Lote

- **WHEN** o mesmo código é varrido no editor e processado pelo Lote no mesmo texto
- **THEN** a quantidade de ocorrências é a mesma (mesma borda CNC de `find_matches`)

#### Scenario: Edição manual invalida a contagem

- **WHEN** o usuário edita o texto após uma varredura
- **THEN** a contagem exibida é marcada como desatualizada até uma nova varredura ser acionada

### Requirement: Navegação sob demanda entre ocorrências

O sistema SHALL oferecer botões **anterior** e **próximo** que **só rolam até a ocorrência quando clicados** (a varredura por si não navega). A navegação MUST ser **circular** (após a última volta à primeira e vice-versa) e MUST atualizar a posição "i/N" e o destaque da ocorrência corrente.

#### Scenario: Próximo rola até a ocorrência

- **WHEN** o usuário clica em "próximo"
- **THEN** o editor rola até a próxima ocorrência, destaca-a e atualiza "i/N"

#### Scenario: Navegação circular

- **WHEN** o usuário está na última ocorrência e clica em "próximo"
- **THEN** a navegação volta para a primeira ocorrência

### Requirement: Substituir em massa no buffer

O sistema SHALL oferecer um **dropdown "Substituir por"** (também da biblioteca) e a ação **"Substituir todos"**, que troca todas as ocorrências do código localizado pelo código de substituição **no buffer em edição** (sem tocar o disco). Após a substituição, o estado de alteração MUST ficar ativo (Salvar habilitado) e a contagem MUST refletir o novo conteúdo.

#### Scenario: Substituir todos de uma vez

- **WHEN** o usuário escolhe "Substituir por" e clica em "Substituir todos"
- **THEN** todas as ocorrências do código localizado são trocadas no buffer, Salvar fica habilitado e a contagem é recalculada

### Requirement: Substituir um a um com confirmação

O sistema SHALL oferecer a ação **"Um a um"**, que percorre as ocorrências **uma de cada vez, pedindo confirmação por ocorrência** (substituir esta / pular / concluir), navegando até a ocorrência atual antes de cada decisão. As trocas MUST ocorrer no buffer em edição.

#### Scenario: Confirmar ocorrência a ocorrência

- **WHEN** o usuário aciona "Um a um"
- **THEN** o editor navega até a primeira ocorrência e oferece substituir / pular / concluir, repetindo para as seguintes

#### Scenario: Pular não altera a ocorrência

- **WHEN** o usuário escolhe "pular" numa ocorrência
- **THEN** essa ocorrência permanece inalterada e o editor avança para a próxima
