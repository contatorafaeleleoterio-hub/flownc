## MODIFIED Requirements

### Requirement: Editor de texto integrado por programa

O sistema SHALL oferecer, para cada programa da lista, a ação **"Editar"** que abre um editor de texto **embutido na própria janela** (sem abrir o arquivo fora do app). O editor MUST exibir **numeração de linha** e usar **fonte monoespaçada**, permitindo **edição direta** do conteúdo. O conteúdo aberto MUST ser lido com `read_file`, preservando o texto e os metadados de codificação/EOL do original. O cabeçalho do editor SHALL exibir o botão `✕ Voltar ao resumo` **proeminente no topo-esquerdo** (alto contraste, não cinza apagado) e o nome do arquivo.

#### Scenario: Abrir um programa no editor

- **WHEN** o usuário clica em "Editar" num programa da lista
- **THEN** o conteúdo do arquivo é carregado no editor embutido, com numeração de linha e fonte monoespaçada, pronto para edição

#### Scenario: Botão Voltar proeminente no topo-esquerdo

- **WHEN** o editor está aberto
- **THEN** o botão "✕ Voltar ao resumo" é o primeiro elemento visível no topo-esquerdo do cabeçalho, com cor de alto contraste (não cinza apagado)

#### Scenario: Edição ocorre em memória até salvar

- **WHEN** o usuário digita ou apaga texto no editor
- **THEN** as alterações ficam apenas no buffer em memória e o arquivo em disco NÃO é tocado até um Salvar explícito

### Requirement: Botão Salvar com ícone 💾 e estado de alteração

O sistema SHALL exibir o botão `💾 Salvar` no editor. O botão SHALL estar desabilitado enquanto não houver alteração no buffer em relação ao conteúdo carregado, e habilitado assim que houver qualquer edição. Após um Salvar bem-sucedido, o estado MUST voltar a "sem alteração" (Salvar desabilitado).

#### Scenario: Botão 💾 Salvar visível com ícone

- **WHEN** o editor está aberto
- **THEN** o botão de salvar exibe o texto "💾 Salvar" (ou ícone equivalente conforme o mockup)

#### Scenario: Salvar começa desabilitado

- **WHEN** um arquivo acaba de ser aberto no editor
- **THEN** o botão Salvar está desabilitado

#### Scenario: Editar habilita Salvar

- **WHEN** o usuário faz a primeira alteração no buffer
- **THEN** o botão Salvar fica habilitado

### Requirement: Realce de todas as ocorrências da busca

O editor SHALL usar `QSyntaxHighlighter` para realçar **todas** as ocorrências do termo buscado com a cor `COLOR_OCCURRENCE`, e a ocorrência atualmente selecionada com a cor `COLOR_OCCURRENCE_CURRENT`. O realce SHALL ser atualizado a cada mudança no campo de busca.

#### Scenario: Realce de todas as ocorrências

- **WHEN** o usuário digita um termo no campo de busca
- **THEN** todas as ocorrências do termo no texto ficam realçadas com COLOR_OCCURRENCE

#### Scenario: Ocorrência atual com cor distinta

- **WHEN** o usuário navega entre ocorrências (↑↓)
- **THEN** a ocorrência atual fica realçada com COLOR_OCCURRENCE_CURRENT, distinta das demais

#### Scenario: Sem realce quando busca está vazia

- **WHEN** o campo de busca está vazio
- **THEN** nenhum realce de ocorrência é exibido no texto

### Requirement: Toolbar do localizador com glifos e labels corretos

A toolbar SHALL exibir: campo de busca, botões `↑` e `↓` para navegar entre ocorrências (não `◂▸`), campo `Substituir` + label `por` separados, contador `N/M`, botão `Substituir todos` e stepbar inline para "Um a um". O glifo de busca SHALL ser `🔍` (não `🔎`).

#### Scenario: Glifos de navegação corretos

- **WHEN** o editor está aberto com resultado de busca
- **THEN** os botões de navegação exibem ↑ e ↓ (setas verticais, não ◂▸)

#### Scenario: Labels Substituir + por separados

- **WHEN** a toolbar do editor é exibida
- **THEN** há dois campos distintos: o campo de substituição com label "Substituir" e o campo de destino com label "por"

### Requirement: Stepbar inline para "Um a um"

O modo "Um a um" SHALL ser implementado como um widget `QWidget` de stepbar inline no editor (não como `QMessageBox`), com botões `← Anterior`, `→ Próxima`, `Substituir` e `Encerrar`. O stepbar SHALL aparecer dentro do painel do editor, sem bloquear o loop de eventos.

#### Scenario: Stepbar inline visível ao ativar Um a um

- **WHEN** o usuário ativa o modo "Um a um"
- **THEN** o stepbar inline aparece dentro do editor com os botões ← Anterior, → Próxima, Substituir e Encerrar

#### Scenario: QMessageBox não é usado para Um a um

- **WHEN** o usuário ativa e usa o modo "Um a um"
- **THEN** nenhum QMessageBox é aberto; toda a interação ocorre no stepbar inline
