## MODIFIED Requirements

### Requirement: Toolbar do editor em 3 grupos

A toolbar SHALL ser organizada em **3 grupos visuais** separados: **Localizar** (dropdown de código + contador "N encontrados" + posição "i/N" + setas ↑ ↓), **Substituir** ("por [código ▾]" + "Substituir todos" + "Um a um") e **➕ Inserir bloco** (abre modal do inseridor de bloco). Os grupos SHALL ter separadores visuais entre si.

#### Scenario: Toolbar exibe os 3 grupos

- **WHEN** a tela Editor é aberta com um arquivo
- **THEN** a toolbar exibe os 3 grupos distintos: Localizar, Substituir e Inserir bloco, com separadores visuais

### Requirement: Contagem automática sem botão de varredura

O sistema SHALL recalcular automaticamente as ocorrências do código selecionado **sempre que**: o código for trocado no dropdown de localizar, o arquivo for trocado na faixa, ou o texto no buffer for editado. NÃO SHALL existir botão de "Varredura" ou estado "— encontrados" parado. O contador SHALL sempre refletir o estado atual do buffer.

#### Scenario: Trocar código reconta imediatamente

- **WHEN** o usuário seleciona um código diferente no dropdown de localizar
- **THEN** o contador "N encontrados" e a posição "i/N" são atualizados imediatamente sem clicar em nada

#### Scenario: Editar o buffer reconta

- **WHEN** o usuário digita texto no editor após uma localização ativa
- **THEN** o contador de ocorrências é recalculado automaticamente para refletir o buffer atualizado

#### Scenario: Trocar arquivo reconta

- **WHEN** o usuário clica em outro arquivo na faixa de arquivos
- **THEN** o contador "N encontrados" é recalculado para o novo arquivo com o mesmo código selecionado

### Requirement: Localizar código da biblioteca com contagem por borda CNC

O sistema SHALL oferecer um **dropdown pesquisável de "Código"** alimentado pela `library_store`. A contagem MUST usar `matcher.find_matches` (borda CNC), de modo que o número exibido seja idêntico ao que o Lote encontraria no mesmo arquivo.

#### Scenario: Contagem idêntica à do Lote

- **WHEN** o mesmo código é localizado no editor e processado pelo Lote no mesmo texto
- **THEN** a quantidade de ocorrências é a mesma

### Requirement: Navegação circular entre ocorrências

O sistema SHALL ter botões **↑** (anterior) e **↓** (próximo) que rolam até a ocorrência ao serem clicados. A navegação MUST ser **circular** e MUST atualizar a posição "i/N" e o realce da ocorrência corrente.

#### Scenario: Próximo rola até a ocorrência

- **WHEN** o usuário clica em "↓"
- **THEN** o editor rola até a próxima ocorrência, destaca-a com realce mais forte e atualiza "i/N"

#### Scenario: Navegação circular na última ocorrência

- **WHEN** o usuário está na última ocorrência e clica em "↓"
- **THEN** o editor volta para a primeira ocorrência

### Requirement: Realce de todas as ocorrências no editor

O sistema SHALL realçar **todas as ocorrências** do código localizado no texto com cor `COLOR_OCCURRENCE` (amarelo). A ocorrência corrente SHALL ter realce distinto mais forte (`COLOR_OCCURRENCE_CURRENT`). O realce SHALL ser implementado via `QSyntaxHighlighter`.

#### Scenario: Todas as ocorrências realçadas

- **WHEN** o usuário seleciona um código no dropdown de localizar
- **THEN** todas as ocorrências no texto ficam realçadas em amarelo; a corrente fica com realce mais forte

### Requirement: "Substituir todos" e "Um a um" via stepbar inline

O sistema SHALL ter o botão **"Substituir todos"** (substitui todas as ocorrências de uma vez) e o botão **"Um a um"** que abre uma **barra inferior inline** com "Ocorrência i/N — substituir [A] → [B]?" e botões **Substituir / Pular → / Concluir**. A stepbar NOT SHALL usar `QMessageBox`.

#### Scenario: "Um a um" abre stepbar inline

- **WHEN** o usuário clica em "Um a um" com um código localizado
- **THEN** a barra inferior aparece na tela com "Ocorrência 1/N — substituir [A] → [B]?" e os 3 botões

#### Scenario: "Substituir todos" substitui sem stepbar

- **WHEN** o usuário clica em "Substituir todos"
- **THEN** todas as ocorrências são substituídas no buffer de uma vez e o contador é zerado
